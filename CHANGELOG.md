# Changelog

All notable changes to the TRMNL MNR Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0-beta] - 2025-08-03

### Added

- **Transfer Support**: API now finds routes requiring transfers when no direct service exists
- **Mixed Trip Results**: By default, shows both direct and transfer trips sorted chronologically (matching official Metro-North app behavior)
- **Configurable Transfer Times**: New API parameters `transferTimeMin` and `transferTimeMax` to customize acceptable transfer wait times
- **Direct Trips Only Filter**: New `showDirectTripsOnly` parameter to show only direct connections
- **Universal Transfer Station Support**: Works with all Metro-North transfer stations across all lines (Harlem, New Haven, Hudson, and branch lines)
- **Cross-Line Transfer Support**: Handles transfers between different Metro-North lines (e.g., Danbury Branch to New Haven Line)
- **Bidirectional Transfer Support**: Works for both directions (to/from Grand Central)

### Changed

- **Default Behavior**: API now shows both direct and transfer trips by default instead of transfers as fallback only
- **Transfer Time Limits**: Default maximum transfer time reduced from 4 hours to 2 hours (120 minutes)
- **Response Format**: Added new fields for transfer trips:
  - `transfer_required`: Boolean indicating if transfer is needed
  - `transfer_station`: Name of the transfer station
  - `transfer_wait_minutes`: Wait time at transfer station
  - `trip_short_name`: Combined format for transfers (e.g., "9950 → 9650")
  - `trip_id`: Combined format for transfers (e.g., "trip1 → trip2")

### Enhanced

- **API Documentation**: Comprehensive README updates with parameter tables, examples, and error responses
- **Transfer Logic**: Intelligent filtering to show only reasonable transfer connections
- **Error Handling**: Better validation and error messages for transfer time parameters

## API Parameters Added

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `transferTimeMin` | integer | 5 | Minimum transfer time in minutes (1-60) |
| `transferTimeMax` | integer | 120 | Maximum transfer time in minutes (transferTimeMin-480) |
| `showDirectTripsOnly` | string | "0" | Set to "1" to show only direct trips |

## Example Usage

### Mixed Results (Default)

```
GET /find-mnr-trips?origin=TenMile%20River&destination=Grand%20Central
```

Returns both direct and transfer trips sorted by departure time.

### Direct Trips Only

```
GET /find-mnr-trips?origin=TenMile%20River&destination=Grand%20Central&showDirectTripsOnly=1
```

Returns only direct connections.

### Custom Transfer Times

```
GET /find-mnr-trips?origin=TenMile%20River&destination=Grand%20Central&transferTimeMin=10&transferTimeMax=60
```

Returns trips with transfer wait times between 10-60 minutes.

## Transfer Stations Verified

- **Harlem Line**: Southeast, Tenmile River, Dover Plains, Harlem Valley-Wingdale, Pawling, Patterson
- **New Haven Line**: South Norwalk, West Haven, Harlem-125 St
- **Hudson Line**: New Hamburg
- **Cross-Line**: South Norwalk (Danbury Branch ↔ New Haven Line)

## Breaking Changes

None. All existing API calls continue to work with the same response format. New fields are additive only.

## [1.0.0] - 2024-06-16

### Added

- **Initial Release**: Flask REST API for querying Metro-North Railroad (MNR) train trips
- **GTFS Integration**: Combines static GTFS data with real-time GTFS-RT feeds
- **Direct Trip Search**: Find upcoming trips between any two MNR stations
- **Real-time Updates**: Live departure, arrival, and delay information
- **CLI Utility**: Command-line interface for trip queries
- **Docker Support**: Containerized deployment with Dockerfile
- **TRMNL Plugin Integration**: Compatible with TRMNL e-ink display platform

### Features

- Search by origin and destination station names
- Optional date parameter for future trip planning
- Real-time status updates (On Time, Delayed X min(s))
- Track assignment information
- Trip duration and stop count
- Last stop destination for each trip
- Automatic GTFS data updates (weekly refresh)

### API Endpoints

- `GET /find-mnr-trips` - Main trip search endpoint
- `GET /` - Welcome message and API information

### Response Format

```json
{
  "trips": [
    {
      "trip_id": "...",
      "trip_short_name": "...",
      "origin": "...",
      "destination": "...",
      "scheduled_departure_time": "...",
      "scheduled_arrival_time": "...",
      "departure_status": "...",
      "arrival_status": "...",
      "track": "...",
      "duration_minutes": ...,
      "stop_count": ...,
      "last_stop": "..."
    }
  ]
}
```

### Data Sources

- **GTFS Static**: Metro-North Google Transit Feed
- **GTFS Realtime**: MTA Realtime Feed for live updates

### Limitations

- Direct trips only (no transfer support)
- Limited to same-route connections

---

*This changelog documents the evolution from the original direct-trips-only API (v1.0.0) to a comprehensive trip planner with intelligent transfer support.*
