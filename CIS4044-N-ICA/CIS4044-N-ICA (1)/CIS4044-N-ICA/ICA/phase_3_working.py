import sqlite3
import requests
import tkinter as tk
from tkinter import ttk, messagebox


# Step 1: Fetch Weather Data from API
def fetch_weather_data(latitude, longitude, start_date, end_date, timezone):
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?latitude={latitude}"
        f"&longitude={longitude}&start_date={start_date}&end_date={end_date}"
        f"&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,precipitation_sum"
        f"&timezone={timezone}"
    )
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


# Step 2: Add or Retrieve Country
def get_or_add_country(conn, country_name, timezone):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM countries WHERE name = ? AND timezone = ?",
        (country_name, timezone),
    )
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute(
        "INSERT INTO countries (name, timezone) VALUES (?, ?)",
        (country_name, timezone),
    )
    conn.commit()
    return cursor.lastrowid


# Step 3: Add or Retrieve City
def get_or_add_city(conn, city_name, latitude, longitude, country_id):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM cities WHERE name = ?", (city_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute(
        "INSERT INTO cities (name, latitude, longitude, country_id) VALUES (?, ?, ?, ?)",
        (city_name, latitude, longitude, country_id),
    )
    conn.commit()
    return cursor.lastrowid


# Step 4: Store Weather Data
def store_weather_data(conn, city_id, weather_data):
    cursor = conn.cursor()
    for i in range(len(weather_data["daily"]["time"])):
        date = weather_data["daily"]["time"][i]
        temp_max = weather_data["daily"]["temperature_2m_max"][i]
        temp_min = weather_data["daily"]["temperature_2m_min"][i]
        temp_mean = weather_data["daily"]["temperature_2m_mean"][i]
        precipitation = weather_data["daily"]["precipitation_sum"][i]
        cursor.execute(
            "SELECT id FROM daily_weather_entries WHERE city_id = ? AND date = ?",
            (city_id, date),
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO daily_weather_entries "
                "(date, min_temp, max_temp, mean_temp, precipitation, city_id) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (date, temp_min, temp_max, temp_mean, precipitation, city_id),
            )
    conn.commit()


# Main GUI Function
def main():
    def submit():
        city_name = city_entry.get()
        country_name = country_entry.get()
        latitude = float(latitude_entry.get())
        longitude = float(longitude_entry.get())
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()
        timezone = timezone_entry.get()
        conn = sqlite3.connect(r"C:\Users\shahz\Downloads\CIS4044-N-ICA\CIS4044-N-ICA (1)\CIS4044-N-ICA\db\CIS4044-N-SDI-OPENMETEO-PARTIAL.db")
        try:
            messagebox.showinfo("Info", "Fetching weather data...")
            weather_data = fetch_weather_data(latitude, longitude, start_date, end_date, timezone)
            messagebox.showinfo("Info", "Updating database...")
            country_id = get_or_add_country(conn, country_name, timezone)
            city_id = get_or_add_city(conn, city_name, latitude, longitude, country_id)
            store_weather_data(conn, city_id, weather_data)
            messagebox.showinfo("Success", "Weather data successfully added to the database!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            conn.close()

    # Root Window
    root = tk.Tk()
    root.title("Weather Data Storage")
    root.geometry("500x500")
    root.configure(bg="#eaf4f4")

    # Title Label
    title_label = tk.Label(
        root,
        text="Weather Data Storage",
        font=("Helvetica", 20, "bold"),
        bg="#eaf4f4",
        fg="#204051",
    )
    title_label.pack(pady=20)

    # Form Frame
    form_frame = ttk.Frame(root, padding="15")
    form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    # Style Configuration
    style = ttk.Style()
    style.configure("TLabel", font=("Arial", 12), padding=5)
    style.configure("TEntry", font=("Arial", 12), padding=5)
    style.configure("TButton", font=("Arial", 12, "bold"), background="#00a8cc")

    # Input Fields
    ttk.Label(form_frame, text="City:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
    city_entry = ttk.Entry(form_frame, width=30)
    city_entry.grid(row=0, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Country:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
    country_entry = ttk.Entry(form_frame, width=30)
    country_entry.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Latitude:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
    latitude_entry = ttk.Entry(form_frame, width=30)
    latitude_entry.grid(row=2, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Longitude:").grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
    longitude_entry = ttk.Entry(form_frame, width=30)
    longitude_entry.grid(row=3, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Start Date (YYYY-MM-DD):").grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
    start_date_entry = ttk.Entry(form_frame, width=30)
    start_date_entry.grid(row=4, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="End Date (YYYY-MM-DD):").grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
    end_date_entry = ttk.Entry(form_frame, width=30)
    end_date_entry.grid(row=5, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Timezone (e.g., US/Central):").grid(row=6, column=0, sticky=tk.W, padx=10, pady=5)
    timezone_entry = ttk.Entry(form_frame, width=30)
    timezone_entry.grid(row=6, column=1, padx=10, pady=5)

    # Submit Button
    submit_button = ttk.Button(root, text="Submit", command=submit)
    submit_button.pack(pady=20)

    # Run the Application
    root.mainloop()


if __name__ == "__main__":
    main()
