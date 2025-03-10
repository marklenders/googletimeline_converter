import json
import csv
import datetime
import os
import sys
import simplekml
import pytz

# 📌 Define timezone for Italy (handles CET/CEST automatically)
utc_tz = pytz.utc
italy_tz = pytz.timezone("Europe/Rome")

def convert_to_local_time(utc_timestamp):
    """
    Converts a UTC timestamp to local Italian time (CET/CEST)
    and returns it in HH:MM format.
    """
    utc_time = datetime.datetime.fromisoformat(utc_timestamp.replace("Z", "+00:00")).replace(tzinfo=utc_tz)
    local_time = utc_time.astimezone(italy_tz)  # Convert to Italian time
    return local_time.strftime("%H:%M")  # Format HH:MM

# 📌 Define custom locations with names and coordinates
nearby_locations = {
    "Holiday Apartment Civitanova ": (43.307546, 13.7294109),
	"Holiday Apartament Chrzanow": (50.1407078, 19.4056969)
}

def get_nearby_location(lat, lon, threshold=0.0020):
    """
    Checks if (lat, lon) is near any custom location
    and returns the location name if found.
    """
    for place_name, (target_lat, target_lon) in nearby_locations.items():
        if abs(lat - target_lat) < threshold and abs(lon - target_lon) < threshold:
            return place_name
    return None

# 📌 Check if folder path is provided as an argument
if len(sys.argv) < 2:
    print("❌ ERROR: You must specify the JSON folder as an argument!")
    print("📌 Example usage: python timeline_converter.py /path/to/folder")
    sys.exit(1)

# 📂 Set the JSON folder from command line argument
json_folder = sys.argv[1]

# 📌 Extract only the last part of the path for file names
folder_name = os.path.basename(json_folder.rstrip(os.sep))
csv_filename = f"{folder_name}.csv"
kml_filename = f"{folder_name}.kml"

# 📂 Find all JSON files in the folder
json_files = sorted([f for f in os.listdir(json_folder) if f.endswith(".json")])

if not json_files:
    print("❌ No JSON files found in the folder.")
    sys.exit(1)

print(f"📂 Found {len(json_files)} JSON files to process...\n")

# 📌 Collect all data in a list for sorting
entries = []

# 📂 Scan each JSON file in the folder
for json_file in json_files:
    json_path = os.path.join(json_folder, json_file)
    print(f"📂 Processing {json_file}...")

    try:
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if "timelineObjects" not in data:
            print(f"⚠️ The file {json_file} does not contain 'timelineObjects', skipped.")
            continue

        # 📌 Process each entry in the timeline
        for item in data["timelineObjects"]:
            try:
                if "activitySegment" in item:  # Movement data
                    segment = item["activitySegment"]

                    start_time = segment["duration"]["startTimestamp"]
                    end_time = segment["duration"]["endTimestamp"]
                    activity_type = segment.get("activityType", "Unknown")
                    distance = segment.get("distance", 0)

                    start_date = start_time.split("T")[0]  # Extract only the date
                    start_time_local = convert_to_local_time(start_time)
                    end_time_local = convert_to_local_time(end_time)

                    start_lat = segment["startLocation"]["latitudeE7"] / 1e7
                    start_lon = segment["startLocation"]["longitudeE7"] / 1e7
                    end_lat = segment["endLocation"]["latitudeE7"] / 1e7
                    end_lon = segment["endLocation"]["longitudeE7"] / 1e7

                    # Extract start and end locations
                    start_location = segment.get("startLocation", {})
                    end_location = segment.get("endLocation", {})

                    # Try to get addresses if available
                    start_address = start_location.get("address", "")
                    end_address = end_location.get("address", "")

                    # Fallback: Try to get address from roadSegment (if available)
                    if not start_address and "roadSegment" in segment:
                        start_address = segment["roadSegment"][0].get("placeId", "")

                    if not end_address and "roadSegment" in segment:
                        end_address = segment["roadSegment"][-1].get("placeId", "")

                    # Append data with address
                    entries.append([start_date, start_time_local, start_time, start_lat, start_lon, "", start_address, "Start", distance, activity_type])
                    entries.append([start_date, end_time_local, end_time, end_lat, end_lon, "", end_address, "End", distance, activity_type])
                    
                elif "placeVisit" in item:  # Visited places
                    visit = item["placeVisit"]
                    
                    visit_location = visit.get("location", {})

                    # Check if 'name' is missing, use 'address' instead
                    place_name = visit_location.get("name") or visit_location.get("address") or "Unknown Place"
                    
                    #place_name = visit["location"].get("name", "Unknown Place")
                    place_name = visit.get("location", {}).get("name", "Unknown Place")
                    visit_time = visit["duration"]["startTimestamp"]
                    address = visit["location"].get("address", "-")

                    visit_date = visit_time.split("T")[0]  # Extract only the date
                    visit_time_local = convert_to_local_time(visit_time)

                    lat = visit["location"]["latitudeE7"] / 1e7
                    lon = visit["location"]["longitudeE7"] / 1e7

                    # 📌 Check if the place is near any known location
                    nearby_place = get_nearby_location(lat, lon)
                    if (not place_name or place_name == "Unknown Place") and nearby_place:
                        place_name = nearby_place
                        
                    # 📌 Replace "calzaturificiojessie" with "4D Engineering S.r.l."
                    if place_name.lower() == "calzaturificiojessie":
                        place_name = "4D Engineering S.r.l."
                        
                    entries.append([visit_date, visit_time_local, visit_time, lat, lon, place_name, address, "Place", "", ""])

            except Exception as e:
                print(f"⚠️ Error processing an item in {json_file}: {e}")

    except Exception as e:
        print(f"❌ Error processing {json_file}: {e}")

# 📌 Sort data by timestamp (date + UTC time)
entries.sort(key=lambda x: x[2])

# 📌 Create sorted CSV file
with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Date", "Time", "Timestamp", "Latitude", "Longitude", "Location", "Address", "Type", "Distance (m)", "Activity"])

    for entry in entries:
        writer.writerow(entry)

print(f"\n✅ Sorted CSV file created: {csv_filename}")

# 📌 Create KML file
kml = simplekml.Kml()

for entry in entries:
    lat, lon, place_name, address, location_type = entry[3], entry[4], entry[5], entry[6], entry[7]

    if location_type == "Place":
        kml.newpoint(name=f"{place_name} ({address})", coords=[(lon, lat)])
    elif location_type == "Start" or location_type == "End":
        kml.newpoint(name=f"{location_type}: {entry[1]}", coords=[(lon, lat)])

# 📌 Save KML file
kml.save(kml_filename)

print(f"✅ KML file created: {kml_filename}")