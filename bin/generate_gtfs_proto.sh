#!/bin/bash
set -e

# PROTO_URL="https://developers.google.com/transit/gtfs-realtime/gtfs-realtime.proto"
# PROTO_URL="https://github.com/google/transit/blob/master/gtfs-realtime/proto/gtfs-realtime.proto"
PROTO_URL="https://gtfs.org/documentation/realtime/gtfs-realtime.proto"

PROTO_FILE="gtfs-realtime.proto"
OUT_DIR="../generated"

echo "Downloading GTFS Realtime proto file..."
curl -sSL "$PROTO_URL" -o "$PROTO_FILE"

if [ $? -ne 0 ]; then
    echo "Failed to download proto file."
    exit 1
fi

mkdir -p "$OUT_DIR"

echo "Compiling proto file with protoc..."
protoc --python_out="$OUT_DIR" "$PROTO_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Generated gtfs_realtime_pb2.py in $OUT_DIR"
else
    echo "❌ Failed to compile proto file. Make sure protoc is installed and in your PATH."
    exit 1
fi
