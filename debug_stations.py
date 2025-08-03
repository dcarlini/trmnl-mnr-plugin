#!/usr/bin/env python3

from server.mnr_trip_finder import MNR_Trip_Finder

# Initialize the trip finder
finder = MNR_Trip_Finder()

# Wait for GTFS data to load
import time
time.sleep(2)

# Get all station names
stop_name_to_id, stop_id_to_name = finder.build_lookup_tables()

# Look for stations that might match "Tenmile River"
print("Looking for stations containing 'mile' or 'river':")
for name in sorted(stop_name_to_id.keys()):
    if 'MILE' in name or 'RIVER' in name:
        print(f"  {name}")

print("\nAll station names:")
for name in sorted(stop_name_to_id.keys()):
    print(f"  {name}")