# Use a minimal Python image with build tools
FROM python:3.10-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    protobuf-compiler

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy project files
COPY server/ /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Generate gtfs_realtime_pb2.py
RUN chmod +x /bin/generate_gtfs_proto.sh && ./bin/generate_gtfs_proto.sh

# Move the generated gtfs_realtime_pb2.py to the correct location
RUN mv gtfs_realtime_pb2.py /app/generated
# Delete the gtfs-realtime.proto file
RUN rm /bin/gtfs-realtime.proto

# Expose Flask port
EXPOSE 5000

# Start the Flask API
CMD ["python", "mnr_trip_finder_api.py"]
