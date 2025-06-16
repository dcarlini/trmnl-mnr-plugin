from flask import Flask, request, jsonify
from mnr_trip_finder import MNR_Trip_Finder

app = Flask(__name__)

# Initialize the trip finder with real-time updates enabled
trip_finder = MNR_Trip_Finder(use_realtime=True)

@app.route("/")
def home():
    return "Hi! Welcome to the MNR Trip Finder API. Use the /find-mnr-trips endpoint to find trips."

@app.route('/find-mnr-trips', methods=['GET'])
def get_trips():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    date = request.args.get('date')  # Optional: format YYYY-MM-DD

    if not origin or not destination:
        return jsonify({'error': 'Both origin and destination parameters are required.'}), 400

    try:
        trips = trip_finder.find_trips(origin, destination, date)
        return jsonify({"trips": trips})
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({
            'error': 'Failed to retrieve trips.',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=False, port=8080)
