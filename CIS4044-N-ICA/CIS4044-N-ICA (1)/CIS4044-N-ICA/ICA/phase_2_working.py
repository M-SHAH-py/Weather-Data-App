import matplotlib.pyplot as plt
import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect(r"C:\Users\shahz\Downloads\CIS4044-N-ICA\CIS4044-N-ICA (1)\CIS4044-N-ICA\db\CIS4044-N-SDI-OPENMETEO-PARTIAL.db")

# Define a function to calculate the average 7-day precipitation
def average_seven_day_precipitation(city_id, start_date):
    try:
        cursor = connection.cursor()
        query = "SELECT AVG(precipitation) FROM daily_weather_entries WHERE city_id = ? AND date BETWEEN ? AND ?"
        end_date = start_date[:4] + "-" + start_date[5:7] + "-" + str(int(start_date[8:10]) + 7)
        cursor.execute(query, (city_id, start_date, end_date))
        result = cursor.fetchone()
        return result[0] if result else None
    except sqlite3.OperationalError as ex:
        print(ex)
        return None

# Define a function to select all countries
def select_all_countries():
    try:
        cursor = connection.cursor()
        query = "SELECT * from countries"
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.OperationalError as ex:
        print(ex)
        return None

# Define a function to calculate the average annual precipitation by city
def average_annual_precipitation_by_city(city_id, year):
    try:
        cursor = connection.cursor()
        query = """SELECT AVG(precipitation) FROM daily_weather_entries WHERE city_id = ? AND strftime('%Y', date) = ?"""
        cursor.execute(query, (city_id, year))
        result = cursor.fetchone()
        return result[0] if result and result[0] is not None else None
    except sqlite3.OperationalError as ex:
        print(ex)
        return None

# Get all city IDs from the database
def get_all_city_ids():
    try:
        cursor = connection.cursor()
        query = "SELECT id FROM cities"
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]
    except sqlite3.OperationalError as ex:
        print(ex)
        return []


def get_temperature_and_precipitation_values(connection, city_id):
    try:
        query = """ 
        SELECT MIN(mean_temp), MAX(mean_temp), AVG(mean_temp), 
        MIN(precipitation), MAX(precipitation), AVG(precipitation)
        FROM daily_weather_entries 
        WHERE city_id = ?
        """
        cursor = connection.cursor()
        cursor.execute(query, (city_id,))
        result = cursor.fetchone()
        
        return result if result else None
    
    except sqlite3.OperationalError as ex:
        print(ex)
        return None

def get_city_name(connection, city_id):
    try:
        query = "SELECT name FROM cities WHERE id = ?"
        cursor = connection.cursor()
        cursor.execute(query, (city_id,))
        result = cursor.fetchone()
        
        return result[0] if result else None
    
    except sqlite3.OperationalError as ex:
        print(ex)
        return None


def get_daily_temperature_values(connection, city_id, date):
    try:
        query = """ 
            SELECT date, min_temp, max_temp 
            FROM daily_weather_entries 
            WHERE city_id = ? AND date LIKE ?
        """
        cursor = connection.cursor()
        cursor.execute(query, (city_id, f"{date}%"))
        results = cursor.fetchall()
        
        if results:
            dates = [result[0] for result in results]
            min_temperatures = [result[1] for result in results]
            max_temperatures = [result[2] for result in results]
            
            return dates, min_temperatures, max_temperatures
        else:
            return [], [], []
    
    except sqlite3.OperationalError as ex:
        print(ex)
        return [], [], []

def average_annual_precipitation_by_country(connection):

    # SQL query to calculate average yearly precipitation for all countries
    query = """
    WITH yearly_precipitation AS (
        SELECT
            co.name AS country,
            strftime('%Y', d.date) AS year,
            AVG(d.precipitation) AS avg_precipitation
        FROM
            daily_weather_entries d
        JOIN
            cities c ON d.city_id = c.id
        JOIN
            countries co ON c.country_id = co.id
        GROUP BY
            co.name, strftime('%Y', d.date)
    )
    SELECT
        country, year,
        AVG(avg_precipitation) AS avg_yearly_precipitation
    FROM
        yearly_precipitation
    GROUP BY
        country, year;
    """

    # Execute the query and convert results to a list of tuples
    cursor = connection.cursor()
    cursor.execute(query)
    results = cursor.fetchall()

    return results

# Graph 2 : Bar Chart for Set of cities
# City_ids
city_ids = get_all_city_ids()

# Generate dates in 2020
start_date = "2021-01-01"

city_names = []
precipitations = []

for city_id in city_ids:
    city_name = get_city_name(connection, city_id)
    precipitation = average_seven_day_precipitation(city_id, start_date)
    if city_name and precipitation is not None:
        city_names.append(city_name)
        precipitations.append(precipitation)

plt.bar(city_names, precipitations)
plt.xlabel('City Name')
plt.ylabel('Precipitation')
plt.title('7-Day Precipitation by City')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

# Graph 3 : Bar Chart avg yearly precipitation by country
# Bar chart for average precipitation by country
results = average_annual_precipitation_by_country(connection)
years = sorted(list(set(row[1] for row in results)))
countries = list(set(row[0] for row in results))
bar_width = 0.8 / len(countries)  # Adjust bar width based on the number of countries
positions = list(range(len(years)))

for i, country in enumerate(countries):
    country_data = [row for row in results if row[0] == country]
    country_years = [row[1] for row in country_data]
    country_precipitations = [row[2] for row in country_data]

    bar_positions = [positions[years.index(year)] + i * bar_width for year in country_years]
    plt.bar(bar_positions, country_precipitations, width=bar_width, label=country)

# Set up the x-axis with year labels positioned at the center of the groups of bars
plt.xlabel('Year')
plt.ylabel('Average Yearly Precipitation')
plt.title('Average Yearly Precipitation by Country')
plt.xticks([p + (len(countries) - 1) * bar_width / 2 for p in positions], years, rotation=45)
plt.legend(title='Country')
plt.tight_layout()
plt.show()

# Graph 4 : Min Max
city_names = []
temperature_min_values = []
temperature_max_values = []
temperature_mean_values = []
precipitation_min_values = []
precipitation_max_values = []
precipitation_mean_values = []

for city_id in city_ids:
    city_name = get_city_name(connection, city_id)
    values = get_temperature_and_precipitation_values(connection, city_id)
    
    if city_name and values:
        city_names.append(city_name)
        temperature_min_values.append(values[0])
        temperature_max_values.append(values[1])
        temperature_mean_values.append(values[2])
        precipitation_min_values.append(values[3])
        precipitation_max_values.append(values[4])
        precipitation_mean_values.append(values[5])

# Create a figure and axis object
fig, ax = plt.subplots(2, figsize=(12, 8))

# Create a grouped bar chart for temperature values
bar_width = 0.2
x = range(len(city_names))
ax[0].bar([i - bar_width for i in x], temperature_min_values, bar_width, label='Min')
ax[0].bar(x, temperature_mean_values, bar_width, label='Mean')
ax[0].bar([i + bar_width for i in x], temperature_max_values, bar_width, label='Max')
ax[0].set_title('Temperature Values')
ax[0].set_xlabel('City Name')
ax[0].set_ylabel('Temperature')
ax[0].set_xticks(x)
ax[0].set_xticklabels(city_names, rotation=90)
ax[0].legend()

# Create a grouped bar chart for precipitation values
ax[1].bar([i - bar_width for i in x], precipitation_min_values, bar_width, label='Min')
ax[1].bar(x, precipitation_mean_values, bar_width, label='Mean')
ax[1].bar([i + bar_width for i in x], precipitation_max_values, bar_width, label='Max')
ax[1].set_title('Precipitation Values')
ax[1].set_xlabel('City Name')
ax[1].set_ylabel('Precipitation')
ax[1].set_xticks(x)
ax[1].set_xticklabels(city_names, rotation=90)
ax[1].legend()

plt.tight_layout()
plt.show()

# Graph
city_id = 1
city_name = get_city_name(connection, city_id)
date = "2022-01"

dates, min_temperatures, max_temperatures = get_daily_temperature_values(connection, city_id, date)

if dates and min_temperatures and max_temperatures:
    plt.figure(figsize=(12, 6))
    plt.plot(dates, min_temperatures, label='Min Temperature')
    plt.plot(dates, max_temperatures, label='Max Temperature')
    plt.xlabel('Date')
    plt.ylabel('Temperature')
    plt.title(f'Daily Min and Max Temperature for {city_name} in {date}')
    plt.legend()
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()
else:
    print("No data found for the specified city and date.")

# Pie Chart: Average Yearly Precipitation Distribution (2020, 2021, 2022)
# Filter the data for the years 2020, 2021, and 2022
filtered_results = [row for row in results if row[1] in ['2020', '2021', '2022']]

yearly_precipitation = {}
for row in filtered_results:
    year = row[1]
    yearly_precipitation[year] = yearly_precipitation.get(year, 0) + row[2]

# Plot the pie chart
plt.figure(figsize=(8, 8))
plt.pie(
    yearly_precipitation.values(),
    labels=yearly_precipitation.keys(),
    autopct='%1.1f%%',
    startangle=140,
    colors=['#ff9999','#66b3ff','#99ff99']
)
plt.title('Average Yearly Precipitation Distribution (2020, 2021, 2022)')
plt.tight_layout()
plt.show()


# Add scatter plot: Average Temperature vs. Precipitation
city_ids = get_all_city_ids()

city_names = []
average_temperatures = []
average_precipitations = []

for city_id in city_ids:
    city_name = get_city_name(connection, city_id)
    values = get_temperature_and_precipitation_values(connection, city_id)
    if city_name and values:
        city_names.append(city_name)
        average_temperatures.append(values[2])  # Mean temperature
        average_precipitations.append(values[5])  # Mean precipitation

plt.figure(figsize=(10, 6))
plt.scatter(average_temperatures, average_precipitations, color='b', alpha=0.7)

for i, city_name in enumerate(city_names):
    plt.annotate(city_name, (average_temperatures[i], average_precipitations[i]), fontsize=8, alpha=0.7)

plt.title('Average Temperature vs. Precipitation by City')
plt.xlabel('Average Temperature')
plt.ylabel('Average Precipitation')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# Yearly trend of precipitation for a city
city_id = 1
city_name = get_city_name(connection, city_id)

query = """
    SELECT strftime('%Y', date) AS year, AVG(precipitation) 
    FROM daily_weather_entries 
    WHERE city_id = ? 
    GROUP BY strftime('%Y', date)
"""
cursor = connection.cursor()
cursor.execute(query, (city_id,))
data = cursor.fetchall()

years = [row[0] for row in data]
precipitations = [row[1] for row in data]

if years and precipitations:
    plt.figure(figsize=(12, 6))
    plt.plot(years, precipitations, marker='o', label='Average Yearly Precipitation')
    plt.xlabel('Year')
    plt.ylabel('Average Precipitation')
    plt.title(f'Yearly Trend of Precipitation for {city_name}')
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.show()
else:
    print(f"No data found for city: {city_name}.")

