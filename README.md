# TRMNL-MNR-PLUGIN 

This project is also used as a plugin for the [TRMNL](https://usetrmnl.com/) app — a platform for displaying real-time data on low-power **e-ink displays**.

It includes server side Flask restful api.
for querying upcoming Metro-North Railroad (MNR) train trips. It combines **static GTFS** data with **real-time GTFS-RT** feeds to give you accurate departure, arrival, and delay information between any two MNR stations.

The TRMNL plugin UI queries the Flask API hosted by this project.
The JSON response is parsed and rendered visually defined by liquid templates

## Server Side

- Search for upcoming trips by **origin** and **destination**
- Real-time updates for departures, arrivals, and delays
- GTFS static + real-time data integration
- CLI utility and Flask API
- Docker-ready deployment

## Plugin Integration

- Retrieves real-time Metro-North Railroad (MNR) departures between configured origin and destination stations.
- Filters and formats trips for clean, minimal presentation.
- Periodically updates to reflect:
  - Delays
  - Track assignments


## 📦 Installation

```bash
git clone https://github.com/yourusername/mnr-trip-finder.git
cd mnr-trip-finder
pip install -r requirements.txt
```

## 🐳 Docker

Build and run using Docker:

```bash
docker build -t mnr-finder .
docker run -p 5000:5000 mnr-finder
```

## 🧪 Usage (Command Line)

You can run the trip finder as a script:

```bash
python server/mnr_trip_finder.py
```

## 🌐 Usage (Flask API)

Start the API server:

```bash
python server/mnr_trip_finder_api.py
```

Then access via:

```
http://localhost:8080/find-mnr-trips?origin=Stamford&destination=Grand%20Central
```

Returns:

```json
{
  "trips": [
    {
      "trip_id": "...",
      "trip_short_name": "...",
      "origin": "...",
      "destination": "...",
      "scheduled_departure_time": "...",
      "updated_departure_time": "...",
      "scheduled_arrival_time": "...",
      "updated_arrival_time": "...",
      "departure_delay": ...,
      "arrival_delay": ...,
      "track": "...",
      "duration_minutes": ...,
      "stop_count": ...,
      "last_stop": "...",
      "stops": [...]
    }
  ]
}
```


## 🗃️ Data Sources

- **GTFS Static**: [Metro-North Google Transit Feed](http://web.mta.info/developers/data/mnr/google_transit.zip)
- **GTFS Realtime**: [MTA Realtime Feed](https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/mnr%2Fgtfs-mnr)






