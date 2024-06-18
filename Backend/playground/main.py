import argparse
import sqlite3
import fitz  # PyMuPDF
import os
import re
import googlemaps
import openmeteo_requests
import requests_cache
from retry_requests import retry

from datetime import datetime, timedelta
from math import radians, cos, sin, atan2, degrees


# Lists to store extracted day of the week and time of the day

# Define a function to check if a string can be parsed into a datetime object.
def checkdatetime(str):
    try:
        datetime.strptime(str, "%d/%m/%Y %H:%M")
        return True
    except ValueError:
        return False

# Define a function to extract incident data from the fetched PDF.
def extractincidents():
    # Open the temporary PDF file.
    doc = fitz.open("temp.pdf")

    all_text = ""
    # Iterate through each page in the PDF and extract text.
    for page in doc:
        all_text += page.get_text()

    # Close the PDF document to free resources.
    doc.close()

    # Split the extracted text into lines.
    lines = all_text.split('\n')

    # Clean up the extracted lines if necessary.
    for i in range(5):
        if len(lines) > 0:
            lines.pop(0)

    if len(lines) > 0 and lines[-1] == "":
        lines.pop()
    
    if len(lines) > 0 and ":" in lines[-1] and "/" in lines[-1]:
        lines.pop()

    # Initialize lists to hold the extracted incident data.
    date_times, incident_numbers, locations, natures, incident_oris = [], [], [], [], []

    # Loop through the lines and extract incident data.
    for i in range(0, len(lines)):
        if 'Date / Time' in lines[i]: 
            continue

        # Check for the pattern indicating the start of an incident record.
        if i + 4 < len(lines) and '/' in lines[i] and ':' in lines[i]:
            date_times.append(lines[i].strip())
            incident_numbers.append(lines[i + 1].strip())
            locations.append(lines[i + 2].strip())
            if checkdatetime(lines[i + 3].strip()):
                natures.append("")
            else:
                if lines[i + 3].strip() == "RAMP":
                    natures.append(lines[i+4].strip())
                else:
                    natures.append(lines[i + 3].strip())
            incident_oris.append(lines[i + 4].strip())

    # Package the extracted data into a dictionary.
    data = {
        'Date/Time': date_times,
        'Incident Number': incident_numbers,
        'Location': locations,
        'Nature': natures,
        'Incident ORI': incident_oris 
    }

    return data

# Define a function to create a SQLite database for storing incident data.
def createdb(db, table_name):
    table_name = f'"{table_name}"'
    try:
        # Connect to the SQLite database (or create it if it doesn't exist).
        con = sqlite3.connect(f"{db}")
        cur = con.cursor()
        # Create the incidents table.
        cur.execute(
            f'''
            CREATE TABLE {table_name} (
                incident_time TEXT,
                incident_number TEXT,
                incident_location TEXT,
                nature TEXT,
                incident_ori TEXT
            )
            '''
        )
        return con
    except sqlite3.OperationalError as e:
        print(e)
        print("Invalid Database String")
        return e

# Define a function to populate the SQLite database with incident data.
def populatedb(db, data, table_name):
    table_name = f'"{table_name}"'
    cur = db.cursor()
    # Clear any existing data in the incidents table.
    cur.execute(f"DELETE FROM {table_name}")
    n = len(data["Date/Time"])

    # Insert the new incident data into the database.
    for i in range(n):
        cur.execute(
            f'''
            INSERT INTO {table_name} (incident_time, incident_number, incident_location, nature, incident_ori)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (data['Date/Time'][i], data['Incident Number'][i], data['Location'][i], data['Nature'][i], data['Incident ORI'][i])
        )
    # Commit the changes to the database.
    db.commit()
    # Remove the temporary PDF file.
    os.remove("temp.pdf")

# Used to retrieve the data from the database.
def getfromDB(db, table_name):
    # Enclose table_name in double quotes to handle cases with special characters or spaces
    table_name = f'"{table_name}"'
    
    # Create a cursor object to interact with the database
    cur = db.cursor()
    
    # Build the SQL query to select all data from the specified table
    query = f"SELECT * FROM {table_name}"

    # Execute the SQL query using the cursor
    cur.execute(query)

    # Initialize an empty list to store the retrieved data
    data = []

    # Fetch all rows returned by the query and append them to the 'data' list
    for row in cur.fetchall():
        data.append(row)

    # Return the collected data from the database
    return data

# Defining the function daytime that takes a data parameter
def daytime(data):
    # Mapping weekdays to their corresponding numeric values
    days_map = {
        "Sunday": 1,
        "Monday": 2,
        "Tuesday": 3,
        "Wednesday": 4,
        "Thursday": 5,
        "Friday": 6,
        "Saturday": 7
    }
    day_of_the_week = []
    time_of_day = []

    # Looping through each row in the input data
    for row in data:
        # Extracting the date from the first element of the row
        date = row[0].split(" ")[0]
        # Converting the date string to a datetime object
        date_obj = datetime.strptime(date, '%m/%d/%Y')
        # Extracting the day of the week from the datetime object
        day = date_obj.strftime('%A')

        # Checking if the extracted day is present in the days_map
        if day in days_map:
            # Appending the numeric day of the week to the list
            day_of_the_week.append(days_map[day])

        # Extracting the time from the first element of the row
        time = row[0].split(" ")[1]
        # Converting the time string to a datetime object
        time_obj = datetime.strptime(time, '%H:%M')
        # Extracting the hour from the datetime object
        hour = time_obj.hour

        # Appending the hour to the time_of_day list
        time_of_day.append(hour)
    
    # Returning a list containing day_of_the_week and time_of_day lists
    return [day_of_the_week, time_of_day]

# defining the function to rank the location based on its frequency.
def locationrank(data, output_table):
    # Initialize an empty dictionary to store location frequencies
    location_freq = {}

    # Iterate through the 'rows' in the data
    for row in data:
        # Increment the frequency count for each location
        location_freq[row[2]] = location_freq.get(row[2], 0) + 1

    # Sort the location frequencies in ascending order
    sorted_location_freq = sorted(location_freq.items(), key=lambda x: x[1])

    # Initialize an empty dictionary to store sorted location frequencies with ranks
    sorted_location_freq_map = {}

    # Initialize variables for ranking
    count = 1
    last_rank = 1

    # Assign ranks to each location based on their frequencies
    for location in sorted_location_freq:
        if (location[1] != last_rank):
            last_rank = count
        
        sorted_location_freq_map[location[0]] = last_rank

        count += 1
    
    # Iterate through each element in the data
    for ele in data:
        # Get the address from the element
        address = ele[2]
        # Append the location rank to the output table
        output_table["location_rank"].append(sorted_location_freq_map[address])

    # Return the dictionary containing sorted location frequencies with ranks
    return sorted_location_freq_map

# Function to find coordinates using Google Maps API
def findcoordinates(ele, gmaps):
    address = ele[2]  # Get the address from the input data
    address_by_google = gmaps.geocode(address)  # Use Google Maps API to geocode the address
    location_lat = 0.0  # Initialize latitude
    location_lng = 0.0  # Initialize longitude
    dir = ""  # Initialize direction

    # Check if Google Maps API returned any results
    if len(address_by_google) > 0:
        location = address_by_google[0]['geometry']['location']  # Extract location data
        location_lng = location["lng"]  # Get longitude
        location_lat = location["lat"]  # Get latitude
    else:
        pattern = r"[-+]?\d*\.\d+"  # Regular expression pattern to check for coordinates in the address

        # Check if the address contains coordinates
        is_coordinate = re.search(pattern, address) is not None
        if is_coordinate:
            location_lng = float(address.split(";")[1])  # Extract longitude from coordinates
            location_lat = float(address.split(";")[0])  # Extract latitude from coordinates
        else:
            address = ele[2] + ", Norman, OK"  # Append city and state to the address
            address_by_google = gmaps.geocode(address)  # Geocode the updated address

            if len(address_by_google) == 0:  # If still no results, check for cardinal directions in the address
                pattern = r'\b(N|NE|E|SE|S|SW|W|NW)\b'
                dir = re.findall(pattern, address)  # Extract cardinal directions from the address
            else:
                location = address_by_google[0]['geometry']['location']  # Extract location data
                location_lng = location["lng"]  # Get longitude
                location_lat = location["lat"]  # Get latitude

    # Return the latitude, longitude, and direction (if any)
    return (location_lng, location_lat, dir)

# # Function to determine the side of town based on coordinates
def sideoftown(data, output_table):
    # Initialize Google Maps API client with API key
    gmaps = googlemaps.Client(key="YOUR API KEY")
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]  # List of cardinal directions
    norman_lng = -97.43948  # Longitude of Norman, OK
    norman_lat = 35.22257  # Latitude of Norman, OK
    address_coordinates = {}  # Dictionary to store address coordinates
    location_lng, location_lat, dir = 0.0, 0.0, ""  # Initialize variables

    # Iterate through input data
    for ele in data:
        if ele[2] in address_coordinates:  # Check if coordinates are already stored
            location_lng, location_lat = address_coordinates[ele[2]][0], address_coordinates[ele[2]][1]
        else:
            # Get coordinates using findcoordinates function
            location_lng, location_lat, dir = findcoordinates(ele, gmaps)

        if dir == "":  # If no cardinal direction found
            address_coordinates[ele[2]] = [location_lng, location_lat]  # Store coordinates
            # Calculate bearing and determine side of town
            lon1, lat1, lon2, lat2 = map(radians, [location_lng, location_lat, norman_lng, norman_lat])
            dlon = lon2 - lon1
            x = cos(lat2) * sin(dlon)
            y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
            bearing = atan2(x, y)
            bearing = degrees(bearing)
            bearing = (bearing + 360) % 360
            ix = round(bearing / (360. / len(dirs)))
            output_table["side_of_town"].append(dirs[ix % len(dirs)])  # Append side of town to output table
        else:
            output_table["side_of_town"].append(dir)  # Append cardinal direction to output table

    # print(output_table["side_of_town"])

    # Return the dictionary of address coordinates
    return address_coordinates

# Function to rank the incidents based on the frequency of the nature
def incidentrank(data, output_table):
    # Initialize an empty dictionary to store the frequency of each nature
    nature_freq = {}
    
    # Iterate through the 'Nature' column of the data
    for row in data:
        # Update the frequency of each nature in the dictionary
        nature_freq[row[3]] = nature_freq.get(row[3], 0) + 1

    # Sort the nature frequencies in ascending order
    sorted_nature_freq = sorted(nature_freq.items(), key=lambda x: x[1])

    # Initialize an empty dictionary to map nature to its rank
    sorted_nature_freq_map = {}

    # Initialize count and last_rank variables to track ranks
    count = 1
    last_rank = 1

    # Iterate through the sorted nature frequencies
    for nature in sorted_nature_freq:
        # Update last_rank if the frequency is different from the previous one
        if nature[1] != last_rank:
            last_rank = count

        # Map nature to its rank in the sorted_nature_freq_map dictionary
        sorted_nature_freq_map[nature[0]] = last_rank

        # Increment the count for the next iteration
        count += 1
    
    # Iterate through each element in the data
    for ele in data:
        # Get the nature of the incident from the element
        nature = ele[3]
        # Append the corresponding rank from sorted_nature_freq_map to the output table
        output_table["incident_rank"].append(sorted_nature_freq_map[nature])

    # Return the output table with incident ranks
    return output_table

# Define a function called 'nature' that takes a parameter 'data'
def nature(data, output_table):
    # Loop through each row in the 'data' parameter
    for row in data:
        # Append the element at index 3 of each row to the "nature" key in the 'output_table' dictionary
        output_table["nature"].append(row[3])

def weather(data, address_coordinates, output_table):
    # Initialize Google Maps client with API key
    gmaps = googlemaps.Client(key="YOUR API KEY")

    # Set up a caching session for requests to reduce API call frequency
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    # Apply retry logic to the session to handle intermittent request failures
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)

    # Initialize OpenMeteo client with the retry-enabled session
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # API endpoint for historical weather data
    url = "https://archive-api.open-meteo.com/v1/archive"

    # Loop through each data element to fetch and process weather information
    for ele in data:
        # Initialize default location coordinates and direction
        location_lng, location_lat, dir = 0.0, 0.0, ""

        # Check if the location is already in the cached coordinates
        if ele[2] not in address_coordinates:
            # Find coordinates using the Google Maps API if not cached
            location_lng, location_lat, dir = findcoordinates(ele, gmaps)
        else:
            # Use cached coordinates
            location_lng, location_lat = address_coordinates[ele[2]][0], address_coordinates[ele[2]][1]

        # Handle cases where direction is specified (indicating an error or specific condition)
        if dir != "":
            output_table["weather"].append(0)
        else:
            # Parse the date from the input data
            date_obj = datetime.strptime(ele[0], "%m/%d/%Y %H:%M")
            # Format date components to ensure two digits
            date = "0" + str(date_obj.day) if date_obj.day < 10 else str(date_obj.day)
            month = "0" + str(date_obj.month) if date_obj.month < 10 else str(date_obj.month)
            year = str(date_obj.year)

            # Prepare parameters for the OpenMeteo API request
            params = {
                "latitude": location_lat,
                "longitude": location_lng,
                "start_date": year + "-" + month + "-" + date,
                "end_date": (date_obj + timedelta(days=1)).strftime("%Y-%m-%d"),
                "hourly": ["temperature_2m", "precipitation", "weather_code"],
                "daily": "weather_code",
                "temperature_unit": "fahrenheit"
            }
            # Make the API call to OpenMeteo to retrieve weather data
            responses = openmeteo.weather_api(url, params=params)
            response = responses[0]

            # Extract the daily weather code from the response
            daily = response.Daily()
            daily_weather_code = daily.Variables(0).ValuesAsNumpy()

            # Append the weather code to the output table
            output_table["weather"].append(daily_weather_code[0])
    
    return output_table["weather"]

# Function to check whether the current Incident_ORI is EMSSTAT and whether the adjacent entries have the same location and same time as of the entry with the ORI of EMSSTAT
def emsstat(db, data, table_name, output_table):
    # Wrapping the table name in double quotes to ensure it's correctly formatted for SQL queries
    table_name = f'"{table_name}"'
    cur = db.cursor()  # Creating a cursor object to execute SQL queries

    n = len(data)  # Getting the length of the input data list

    # Creating a list of False values with the same length as the input data
    emsstat_lst = [False]*n

    # Looping through the data to find occurrences of "EMSSTAT"
    for i in range(n):
        curr_inc_ORI = data[i][-1]  # Extracting the last element of each sublist in data

        if (curr_inc_ORI == "EMSSTAT"):  # Checking if the last element is "EMSSTAT"
            emsstat_lst[i] = True  # Setting the corresponding index in emsstat_lst to True
            j = i-1
            # Checking and marking previous occurrences of the same incident and agency
            while (j > 0 and data[j][0] == data[i][0] and data[j][2] == data[i][2]):
                emsstat_lst[j] = True
                j -= 1 
            j = i+1
            # Checking and marking subsequent occurrences of the same incident and agency
            while (j < n and data[j][0] == data[i][0] and data[j][2] == data[i][2]):
                emsstat_lst[j] = True
                j += 1

    # Assuming output_table is a global variable, appending the emsstat_lst to it under "EMSSTAT" key
    output_table["EMSSTAT"].append(emsstat_lst)

    # Dropping the specified table from the database using the formatted table_name
    cur.execute(f"DROP TABLE {table_name}")

def printoutput(output_table):
    # Calculate the maximum length of the lists in the output_table dictionary
    # This is used to determine the number of rows to print
    max_length = max(len(column) for column in output_table.values())

    # Print the header row of the table
    print("Day of the Week\tTime of Day\tWeather\tLocation Rank\tSide of Town\tIncident Rank\tNature\tEMSSTAT")

    # Iterate over each row index based on the maximum length calculated
    for i in range(max_length):
        # Iterate over each key in the dictionary to print the values in each column
        for key in output_table.keys():
            # Print each value in the row, separated by a tab character
            if (len(output_table[key]) > 0):
                print(output_table[key][i], end="\t")
            else:
                print(None)
        # After printing all columns in a row, print a newline character to move to the next row
        print()
      
def main(url):
        output_table = {
            "day_of_the_week": [],
            "time_of_day": [],
            "weather": [],
            "location_rank": [],
            "side_of_town": [],
            "incident_rank": [],
            "nature": [],
            "EMSSTAT": []
        }
        # Extract incident data from the PDF
        incidents = extractincidents()

        # Create and connect to the database
        db = createdb("db.sqlite3", url[0][-37:-33] + "_" + url[0][-32:-30] + "_" + url[0][-29:-4])
            
        # Populate the database with incident data
        populatedb(db, incidents, url[0][-37:-33] + "_" + url[0][-32:-30] + "_" + url[0][-29:-4])

        # Retrieve data from the database based on a specific date
        data = getfromDB(db, url[0][-37:-33] + "_" + url[0][-32:-30] + "_" + url[0][-29:-4])

        # Analyze and process the data for daytime incidents
        day_of_the_week, time_of_day = daytime(data)
        output_table["day_of_the_week"] = day_of_the_week
        output_table["time_of_day"] = time_of_day

        # Analyze and rank incidents based on location
        locationrank(data, output_table)

        # Determine the side of town where incidents occur
        address_coordinates = sideoftown(data, output_table)

        # Fetch weather data for the incident locations
        weather(data, address_coordinates, output_table)

        # Rank incidents based on severity
        incidentrank(data, output_table)

        # Classify incidents by nature (e.g., theft, assault)
        nature(data, output_table)

        # Perform statistical analysis on EMS data and update the database
        emsstat(db, data, url[0][-37:-33] + "_" + url[0][-32:-30] + "_" + url[0][-29:-4], output_table)
        
        # Flatten the output_table["EMSSTAT"] list of lists
        output_table["EMSSTAT"] = [item for sublist in output_table["EMSSTAT"] for item in sublist]

        # Write the data from output_table into a terminal
        printoutput(output_table)

        return output_table

