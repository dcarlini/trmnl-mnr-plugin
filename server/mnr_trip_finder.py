import csv
import json
import zipfile
import requests
import os
import threading
from io import BytesIO
from datetime import datetime, date, time, timedelta
from collections import defaultdict
from google.transit import gtfs_realtime_pb2
import pytz

GTFS_STATIC_URL = "http://web.mta.info/developers/data/mnr/google_transit.zip"
GTFS_REALTIME_URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/mnr%2Fgtfs-mnr"
TZ = pytz.timezone("America/New_York")

class MNR_Trip_Finder:
    def __init__(self, use_local_path=None, use_realtime=False):
        self.gtfs_data = {}
        self.use_realtime = use_realtime
        self._gtfs_lock = threading.Lock()
        self._gtfs_thread = threading.Thread(target=lambda: self._periodic_update_gtfs(use_local_path), daemon=True)
        self._gtfs_thread.start()
        self._update_gtfs_data()

    def _update_gtfs_data(self):
        with self._gtfs_lock:
            self.gtfs_data = self.download_and_extract()

    def _periodic_update_gtfs(self, use_local_path):
        while True:
            threading.Event().wait(7 * 24 * 60 * 60)  # Sleep for 1 week
            self._update_gtfs_data()

    def download_and_extract(self, use_local_path=None):
        file_names = ["stops.txt", "trips.txt", "stop_times.txt", "calendar.txt", "calendar_dates.txt"]
        files = {}

        if use_local_path and os.path.isfile(use_local_path):
            zip_source = open(use_local_path, "rb")
        else:
            response = requests.get(GTFS_STATIC_URL)
            zip_source = BytesIO(response.content)

        with zipfile.ZipFile(zip_source) as z:
            for name in file_names:
                with z.open(name) as f:
                    files[name] = list(csv.DictReader(f.read().decode("utf-8").splitlines()))

        if use_local_path:
            zip_source.close()

        return files

    def get_trip_updates(self):
        response = requests.get(GTFS_REALTIME_URL)
        response.raise_for_status()

        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)

        updates = {}
        for entity in feed.entity:
            if not entity.HasField("trip_update"):
                continue

            trip_id = entity.trip_update.trip.trip_id
            entry_id = entity.id

            for stop_time_update in entity.trip_update.stop_time_update:
                stop_id = stop_time_update.stop_id

                # Determine delay status early
                has_dep_delay = stop_time_update.HasField("departure") and stop_time_update.departure.HasField("delay")
                delay_seconds = stop_time_update.departure.delay if has_dep_delay else None

                if has_dep_delay and delay_seconds == 0:
                    status = "On Time"
                elif has_dep_delay:
                    status = f"Delayed {int(delay_seconds // 60)} min(s)"
                else:
                    status = "On Time"

                # Optional arrival and departure times
                arrival = stop_time_update.arrival.time if stop_time_update.HasField("arrival") and stop_time_update.arrival.HasField("time") else None
                departure = stop_time_update.departure.time if stop_time_update.HasField("departure") and stop_time_update.departure.HasField("time") else None

                updates[(entry_id, stop_id)] = {
                    "trip_id": trip_id,
                    "stop_id": stop_id,
                    # "arrival_time": datetime.fromtimestamp(arrival).strftime("%I:%M %p") if arrival else None,
                    # "departure_time": datetime.fromtimestamp(departure).strftime("%I:%M %p") if departure else None,
                    # "arrival_delay": stop_time_update.arrival.delay if stop_time_update.HasField("arrival") and stop_time_update.arrival.HasField("delay") else None,
                    # "departure_delay": delay_seconds,
                    "status": status,
                }

        return updates
    
    def parse_gtfs_time(self, t_str):
        try:
            dt = datetime.strptime(t_str, "%H:%M:%S")
            dt = datetime.combine(date.today(), dt.time())
        except ValueError:
            hours, minutes, seconds = map(int, t_str.split(":"))
            dt = datetime.combine(date.today(), time(0, 0)) + timedelta(hours=hours, minutes=minutes, seconds=seconds)

        return dt

    def build_lookup_tables(self):
        stop_name_to_id = {}
        stop_id_to_name = {}
        for stop in self.gtfs_data["stops.txt"]:
            name = stop["stop_name"].strip().upper()
            stop_id = stop["stop_id"].strip()
            stop_name_to_id[name] = stop_id
            stop_id_to_name[stop_id] = stop["stop_name"].strip()
        return stop_name_to_id, stop_id_to_name

    def get_service_ids_for_date(self, target_date):
        day_name = target_date.strftime('%A').lower()
        valid_services = set()
        for row in self.gtfs_data["calendar.txt"]:
            start_date = datetime.strptime(row["start_date"], "%Y%m%d").date()
            end_date = datetime.strptime(row["end_date"], "%Y%m%d").date()
            if start_date <= target_date <= end_date and row.get(day_name) == "1":
                valid_services.add(row["service_id"])
        for row in self.gtfs_data["calendar_dates.txt"]:
            service_date = datetime.strptime(row["date"], "%Y%m%d").date()
            if service_date == target_date:
                if row["exception_type"] == "1":
                    valid_services.add(row["service_id"])
                elif row["exception_type"] == "2":
                    valid_services.discard(row["service_id"])
        return valid_services

    def get_realtime_updates_for_trip(self, realtime_updates, trip_short_name, trip_id, from_id, to_id):
        def safe_format(raw_time):
            try:
                return datetime.strptime(raw_time, "%I:%M %p").strftime("%I:%M %p") if raw_time else None
            except:
                return raw_time

        dep_key_short = (trip_short_name, from_id)
        arr_key_short = (trip_short_name, to_id)
        dep_key_id = (trip_id, from_id)
        arr_key_id = (trip_id, to_id)

        dep_update = realtime_updates.get(dep_key_short) or realtime_updates.get(dep_key_id)
        arr_update = realtime_updates.get(arr_key_short) or realtime_updates.get(arr_key_id)

        # updated_departure_time = safe_format(dep_update["departure_time"]) if dep_update else None
        # updated_arrival_time = safe_format(arr_update["arrival_time"]) if arr_update else None

        # departure_delay = dep_update["departure_delay"] if dep_update else None
        # arrival_delay = arr_update["arrival_delay"] if arr_update else None

        # get status messages
        departure_status = dep_update["status"] if dep_update and dep_update.get("status") else None
        arrival_status = arr_update["status"] if arr_update and arr_update.get("status") else None

        return departure_status, arrival_status

    def find_trips(self, origin, destination, date_str=None):
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
        now = datetime.now(TZ)

        stop_name_to_id, stop_id_to_name = self.build_lookup_tables()
        from_id = stop_name_to_id.get(origin.strip().upper())
        to_id = stop_name_to_id.get(destination.strip().upper())
        if not from_id or not to_id:
            raise ValueError("Invalid station names.")

        valid_services = self.get_service_ids_for_date(target_date)

        trip_stops = defaultdict(list)
        for entry in self.gtfs_data["stop_times.txt"]:
            trip_stops[entry["trip_id"]].append(entry)

        trip_service = {t["trip_id"]: t["service_id"] for t in self.gtfs_data["trips.txt"]}
        trip_short_name_map = {t["trip_id"]: t.get("trip_short_name", "") for t in self.gtfs_data["trips.txt"]}
        upcoming_trips = []
        realtime_updates = {}
        if self.use_realtime:
            try:
                realtime_updates = self.get_trip_updates()
            except Exception as e:
                print(f"Warning: failed to fetch real-time updates: {e}")

        for trip_id, stops in trip_stops.items():
            if trip_service.get(trip_id) not in valid_services:
                continue

            stops_sorted = sorted(stops, key=lambda x: int(x["stop_sequence"]))
            stop_ids = [s["stop_id"] for s in stops_sorted]

            if from_id in stop_ids and to_id in stop_ids and stop_ids.index(from_id) < stop_ids.index(to_id):
                from_stop = next(s for s in stops_sorted if s["stop_id"] == from_id)
                to_stop = next(s for s in stops_sorted if s["stop_id"] == to_id)

                dep_time_dt = self.parse_gtfs_time(from_stop["departure_time"])
                arr_time_dt = self.parse_gtfs_time(to_stop["arrival_time"])

                if arr_time_dt < dep_time_dt:
                    arr_time_dt += timedelta(days=1)

                if dep_time_dt.time() <= now.time() and target_date == date.today():
                    continue

                duration_minutes = int((arr_time_dt - dep_time_dt).total_seconds() // 60)
                track = from_stop.get("stop_headsign", "") or from_stop.get("track", "") or "N/A"
                departure_time_fmt = dep_time_dt.strftime("%I:%M %p")
                arrival_time_fmt = arr_time_dt.strftime("%I:%M %p")

                trip_short_name = trip_short_name_map.get(trip_id, "")
                departure_status, arrival_status = self.get_realtime_updates_for_trip(
                    realtime_updates, trip_short_name, trip_id, from_id, to_id)

                last_stop = stop_id_to_name.get(stops_sorted[-1]["stop_id"], stops_sorted[-1]["stop_id"])
                upcoming_trips.append({
                    "trip_short_name": trip_short_name,
                    "origin": origin,
                    "destination": destination,
                    "trip_id": trip_id,
                    "raw_departure_time": dep_time_dt,
                    "scheduled_departure_time": departure_time_fmt,
                    # "updated_departure_time": updated_departure_time,
                    "scheduled_arrival_time": arrival_time_fmt,
                    # "updated_arrival_time": updated_arrival_time,
                    # "departure_delay": departure_delay,
                    # "arrival_delay": arrival_delay,
                    "departure_status": departure_status,
                    "arrival_status": arrival_status,
                    "duration_minutes": duration_minutes,
                    "track": track,
                    # "stops": [stop_id_to_name.get(s["stop_id"], s["stop_id"]) for s in stops_sorted],
                    "stop_count": stop_ids.index(to_id) - stop_ids.index(from_id) + 1,
                    "last_stop": last_stop
                })

        return sorted(upcoming_trips, key=lambda x: x["raw_departure_time"])[:10]


if __name__ == "__main__":
    use_realtime = True
    output_format = "text"
    origin = "Stamford"
    destination = "Grand Central"

    finder = MNR_Trip_Finder(use_realtime=use_realtime)
    trips = finder.find_trips(origin, destination)

    if output_format == "json":
        print(json.dumps(trips, indent=2))
    else:
        for trip in trips:
            print(f"{trip['scheduled_departure_time']} - {trip['scheduled_arrival_time']} | {trip['origin']} -> {trip['destination']}  | Track: {trip['track']} | Duration: {trip['duration_minutes']} min | Stops: {trip['stop_count']} | Last Stop: {trip['last_stop']}  | Dep Status: {trip['departure_status']} | Arr Status: {trip['arrival_status']}\n")
