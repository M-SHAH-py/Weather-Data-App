# Author: <Your name here>
# Student ID: <Your Student ID>

import sqlite3
from datetime import datetime, timedelta

# Phase 1 - Starter
# 
# Note: Display all real/float numbers to 2 decimal places.

'''
Satisfactory
'''

def select_all_countries(connection):
    # Queries the database and selects all the countries 
    # stored in the countries table of the database.
    # The returned results are then printed to the 
    # console.
    try:
        # Define the query
        query = "SELECT * from countries"

        # Get a cursor object from the database connection
        # that will be used to execute database query.
        cursor = connection.cursor()

        # Execute the query via the cursor object.
        results = cursor.execute(query)

        # Iterate over the results and display the results.
        for row in results:
            print(f"Country Id: {row[0]} -- Country Name: {row[1]} -- Country Timezone: {row[2]}")

    except sqlite3.OperationalError as ex:
        print(ex)

def select_all_cities(connection):
    try:
        query = "SELECT * FROM cities"
        cursor = connection.cursor()
        results = cursor.execute(query)
        for row in results:
            print(f"City Id: {row[0]} -- City Name: {row[1]} -- Country Id: {row[2]}")
    except sqlite3.OperationalError as ex:
        print(ex)

def average_annual_temperature(connection, city_id, year):
    try:
        query = "SELECT AVG(mean_temp) FROM daily_weather_entries WHERE city_id = ? AND date LIKE ?"
        cursor = connection.cursor()
        cursor.execute(query, (city_id, f"{year}%"))
        result = cursor.fetchone()
        print(f"Average Annual Temperature: {result[0]:.2f}")
    except sqlite3.OperationalError as ex:
        print(ex)


def average_seven_day_precipitation(connection, city_id, start_date):
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = start_date_obj + timedelta(days=7)
        end_date = end_date_obj.strftime("%Y-%m-%d")

        query = "SELECT AVG(precipitation) FROM daily_weather_entries WHERE city_id = ? AND date BETWEEN ? AND ?"
        cursor = connection.cursor()
        cursor.execute(query, (city_id, start_date, end_date))
        result = cursor.fetchone()
        print(f"Average 7-Day Precipitation: {result[0]:.2f}")
    except sqlite3.OperationalError as ex:
        print(ex)

def average_mean_temp_by_city(connection, city_id, date_from, date_to):
    try:
        query = "SELECT AVG(mean_temp) FROM daily_weather_entries WHERE city_id = ? AND date BETWEEN ? AND ?"
        cursor = connection.cursor()
        cursor.execute(query, (city_id, date_from, date_to))
        result = cursor.fetchone()
        print(f"Average Mean Temp by City: {result[0]:.2f}")
    except sqlite3.OperationalError as ex:
        print(ex)

def average_annual_precipitation_by_country(connection, city_id, year):
    try:
        query = """
        SELECT AVG(precipitation) 
        FROM daily_weather_entries 
        WHERE city_id = ? AND strftime('%Y', date) = ?
        """
        cursor = connection.cursor()
        cursor.execute(query, (city_id, year))
        result = cursor.fetchone()
        if result[0] is not None:
            print(f"Average Annual Precipitation by Country: {result[0]:.2f}")
        else:
            print("No data found for the specified city and year.")
    except sqlite3.OperationalError as ex:
        print(ex)


connection = sqlite3.connect(r"C:\Users\shahz\Downloads\CIS4044-N-ICA\CIS4044-N-ICA (1)\CIS4044-N-ICA\db\CIS4044-N-SDI-OPENMETEO-PARTIAL.db")

select_all_countries(connection)
select_all_cities(connection)
average_annual_temperature(connection, 1, 2022)
city_id = 1
start_date = "2020-01-01"
average_seven_day_precipitation(connection, city_id, start_date)
city_id = 1
date_from = "2020-01-01"
date_to = "2020-01-31"
average_mean_temp_by_city(connection, city_id, date_from, date_to)

city_id = 2
date_from = "2020-01-01"
date_to = "2020-01-31"
average_mean_temp_by_city(connection, city_id, date_from, date_to)
# Specify the country ID and year
country_id = 1
year = "2020"

# Call the function
average_annual_precipitation_by_country(connection, country_id, year)