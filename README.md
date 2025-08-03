# TRMNL-MNR-PLUGIN

This project is also used as a plugin for the [TRMNL](https://usetrmnl.com/) app — a platform for displaying real-time data on low-power **e-ink displays**.

It includes server side Flask restful api.
for querying upcoming Metro-North Railroad (MNR) train trips. It combines **static GTFS** data with **real-time GTFS-RT** feeds to give you accurate departure, arrival, and delay information between any two MNR stations.

The TRMNL plugin UI queries the Flask API hosted by this project.
The JSON response is parsed and rendered visually defined by liquid templates

## Server Side

- Search for upcoming trips by **origin** and **destination**
- **Direct and transfer routes** - finds connections requiring transfers when no direct service exists
- **Configurable transfer times** - customize minimum and maximum transfer wait times
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
docker run -p 8080:8080 mnr-finder
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

### API Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `origin` | string | *required* | Origin station name |
| `destination` | string | *required* | Destination station name |
| `date` | string | today | Date in YYYY-MM-DD format |
| `transferTimeMin` | integer | 5 | Minimum transfer time in minutes (1-60) |
| `transferTimeMax` | integer | 120 | Maximum transfer time in minutes (transferTimeMin-480) |
| `showDirectTripsOnly` | string | 0 | Set to "1" to show only direct trips, omit or "0" for both direct and transfer trips |

### Examples

**Basic trip search:**

```
http://localhost:8080/find-mnr-trips?origin=Stamford&destination=Grand%20Central
```

**Trip with transfer (e.g., TenMile River to Grand Central via Southeast):**

```
http://localhost:8080/find-mnr-trips?origin=TenMile%20River&destination=Grand%20Central
```

**Custom transfer time limits (30 minutes max):**

```
http://localhost:8080/find-mnr-trips?origin=TenMile%20River&destination=Grand%20Central&transferTimeMax=30
```

**Tight transfer window (5-15 minutes):**

```
http://localhost:8080/find-mnr-trips?origin=TenMile%20River&destination=Grand%20Central&transferTimeMin=5&transferTimeMax=15
```

**Future date:**

```
http://localhost:8080/find-mnr-trips?origin=Stamford&destination=Grand%20Central&date=2025-08-04
```

**Show only direct trips:**

```
http://localhost:8080/find-mnr-trips?origin=TenMile%20River&destination=Grand%20Central&showDirectTripsOnly=1
```

### Error Responses

**Invalid station names:**

```json
{
  "error": "Invalid station names."
}
```

**Invalid transfer time parameters:**

```json
{
  "error": "transferTimeMax must be between transferTimeMin and 480 minutes (8 hours)."
}
```

**Missing required parameters:**

```json
{
  "error": "Both origin and destination parameters are required."
}
```

### Response Format

**Direct Trip Response:**

```json
{
  "trips": [
    {
      "trip_id": "246089224608951+1545618+1",
      "trip_short_name": "916",
      "origin": "Stamford",
      "destination": "Grand Central",
      "scheduled_departure_time": "05:49 AM",
      "scheduled_arrival_time": "07:55 AM",
      "departure_status": "On Time",
      "arrival_status": "On Time",
      "track": "1",
      "duration_minutes": 126,
      "stop_count": 13,
      "last_stop": "Grand Central",
      "transfer_required": false
    }
  ]
}
```

**Transfer Trip Response:**

```json
{
  "trips": [
    {
      "trip_id": "246089124609187+1546738+0 → 246089124609057+1546482+0",
      "trip_short_name": "9950 → 9650",
      "origin": "TenMile River",
      "destination": "Grand Central",
      "scheduled_departure_time": "04:19 PM",
      "scheduled_arrival_time": "06:40 PM",
      "departure_status": null,
      "arrival_status": null,
      "track": "N/A",
      "duration_minutes": 141,
      "stop_count": "Transfer required",
      "last_stop": "Grand Central",
      "transfer_required": true,
      "transfer_station": "Southeast",
      "transfer_wait_minutes": 9
    }
  ]
}
```

## 🚂 Transfer Support

The API intelligently handles routes that require transfers:

1. **Mixed Results**: By default, shows both direct and transfer trips sorted chronologically (like the official Metro-North app)
2. **Direct Only Option**: Use `showDirectTripsOnly=1` to filter out transfer connections
3. **Smart Filtering**: Only shows reasonable transfer times (configurable 5-120 minutes by default)
4. **Transfer Details**: Provides transfer station name and wait time information

### Common Transfer Routes

- **TenMile River ↔ Grand Central**: via Southeast
- **Smaller branch stations**: Often require transfers at major junction stations

### Transfer Time Configuration

- **Minimum Transfer Time**: Ensures sufficient time to change trains (default: 5 minutes)
- **Maximum Transfer Time**: Avoids unreasonably long waits (default: 2 hours)
- **Customizable**: Adjust via API parameters based on your preferences

## 🗃️ Data Sources

- **GTFS Static**: [Metro-North Google Transit Feed](http://web.mta.info/developers/data/mnr/google_transit.zip)
- **GTFS Realtime**: [MTA Realtime Feed](https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/mnr%2Fgtfs-mnr)
