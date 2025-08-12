# microserviceA-coverter
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

def is_dst_period(dt):
    """ In the U.S., DST runs from the second Sunday in March 
    to the first Sunday in November."""
    year = dt.year

    # From March.1, search second sunday
    march = datetime(year, 3, 1)
    first_sunday = march + timedelta(days=(6 - march.weekday()) % 7)
    second_sunday_march = first_sunday + timedelta(weeks=1)

    # From Nov.1, search first sunday
    november = datetime(year, 11, 1)
    first_sunday_nov = november + timedelta(days=(6 - november.weekday()) % 7)
    
    return second_sunday_march <= dt <first_sunday_nov


# convert service main
def convert_utc_to_local(utc_str, offset, is_dst):
    """ UTC str + timezone offset(+-12) + DST """
    utc_dt = datetime.strptime(utc_str, "%Y-%m-%d %H:%M")
    
    # If DST is True, and date is in DST period = +1
    dst_hour = 1 if is_dst and is_dst_period(utc_dt) else 0

    total_offset = offset + dst_hour
    local_dt = utc_dt + timedelta(hours=total_offset)

    return {
        "date": local_dt.strftime("%Y-%m-%d"),
        "time": local_dt.strftime("%H:%M")
    }

@app.route("/convert", methods=["POST"])
def convert():
    data = request.get_json()
    print(f"Received request: {data}")  # Add receive message

    if data.get("command") != "convert_datetime":
        return jsonify({"error": "Invalid command"}), 400

    try:
        utc_datetime = data["utc_datetime"]
        offset = int(data["timezone_offset"])
        is_dst = bool(data["is_dst"])

        # check range
        if not -12 <= offset <= 12:
            return jsonify({"error": "timezone_offset must be between -12 and +12"}), 400

        converted = convert_utc_to_local(utc_datetime, offset, is_dst)
        return jsonify({"converted_datetime": converted})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(port=5001)
