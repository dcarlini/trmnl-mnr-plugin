from flask import Flask, request, jsonify
from mnr_trip_finder import MNR_Trip_Finder
from __version__ import __version__, __title__, __description__, API_VERSION

app = Flask(__name__)

# Initialize the trip finder with real-time updates enabled
trip_finder = MNR_Trip_Finder(use_realtime=True)

@app.route("/")
def home():
    return jsonify({
        "name": __title__,
        "description": __description__,
        "version": __version__,
        "api_version": API_VERSION,
        "endpoints": {
            "/": "API information",
            "/find-mnr-trips": "Find Metro-North trips between stations",
            "/version": "Version information"
        },
        "message": "Welcome to the MNR Trip Finder API!"
    })

@app.route("/version")
def version():
    return jsonify({
        "version": __version__,
        "api_version": API_VERSION,
        "name": __title__
    })

@app.route('/find-mnr-trips', methods=['GET'])
def get_trips():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    date = request.args.get('date')  # Optional: format YYYY-MM-DD
    transfer_time_min = request.args.get('transferTimeMin', 5, type=int)  # Default 5 minutes
    transfer_time_max = request.args.get('transferTimeMax', 120, type=int)  # Default 2 hours
    show_direct_trips_only = request.args.get('showDirectTripsOnly', '0') == '1'  # Default false

    if not origin or not destination:
        return jsonify({'error': 'Both origin and destination parameters are required.'}), 400

    # Validate transfer time parameters
    if transfer_time_min < 1 or transfer_time_min > 60:
        return jsonify({'error': 'transferTimeMin must be between 1 and 60 minutes.'}), 400
    
    if transfer_time_max < transfer_time_min or transfer_time_max > 480:
        return jsonify({'error': 'transferTimeMax must be between transferTimeMin and 480 minutes (8 hours).'}), 400

    try:
        trips = trip_finder.find_trips(origin, destination, date, transfer_time_min, transfer_time_max, show_direct_trips_only)
        return jsonify({"trips": trips})
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve trips.',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
