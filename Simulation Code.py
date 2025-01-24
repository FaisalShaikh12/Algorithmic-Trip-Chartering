import tkinter as tk
from tkinter import ttk
from collections import defaultdict
import random

# Algorithm functions
def calculate_travel_time(location1, location2):
    return abs(location1[0] - location2[0]) + abs(location1[1] - location2[1])

def calculate_required_battery(current_location, start_location, end_location):
    distance_to_start = abs(current_location[0] - start_location[0]) + abs(current_location[1] - start_location[1])
    distance_trip = abs(start_location[0] - end_location[0]) + abs(start_location[1] - end_location[1])
    total_distance = distance_to_start + distance_trip
    return total_distance

def find_nearest_vertiport(current_location, vertiports):
    min_distance = float('inf')
    nearest_vertiport = None
    for vertiport in vertiports:
        distance = calculate_travel_time(current_location, vertiport)
        if distance < min_distance:
            min_distance = distance
            nearest_vertiport = vertiport
    return nearest_vertiport

def calculate_charging_time(current_battery_level, battery_capacity, charging_rate):
    return (battery_capacity - current_battery_level) / charging_rate

def assign_air_taxis_greedy(air_taxis, trips, vertiports, battery_threshold, battery_capacity, charging_rate, current_time):
    air_taxi_schedule = defaultdict(list)
    assigned_trips = set()
    
    trips.sort(key=lambda trip: trip['start_time'])
    
    for trip in trips:
        trip_id = (trip['start_time'], trip['end_time'], trip['start_location'], trip['end_location'])
        if trip_id in assigned_trips:
            continue
        
        start_time = trip['start_time']
        end_time = trip['end_time']
        start_location = trip['start_location']
        end_location = trip['end_location']
        
        best_air_taxi = None
        closest_arrival_time = float('inf')
        
        for air_taxi in air_taxis:
            travel_time_to_start = calculate_travel_time(air_taxi['location'], start_location)
            arrival_time = max(current_time, air_taxi['availability_time']) + travel_time_to_start
            required_battery = calculate_required_battery(air_taxi['location'], start_location, end_location)
            
            if arrival_time <= end_time and air_taxi['battery_level'] >= required_battery:
                if arrival_time < closest_arrival_time:
                    closest_arrival_time = arrival_time
                    best_air_taxi = air_taxi
        
        if best_air_taxi:
            adjusted_start_time = max(start_time, closest_arrival_time)
            best_air_taxi['location'] = end_location
            best_air_taxi['battery_level'] -= required_battery
            best_air_taxi['availability_time'] = end_time
            air_taxi_schedule[best_air_taxi['id']].append(trip)
            assigned_trips.add(trip_id)
            
            if best_air_taxi['battery_level'] < battery_threshold:
                nearest_vertiport = find_nearest_vertiport(end_location, vertiports)
                charging_time = calculate_charging_time(best_air_taxi['battery_level'], battery_capacity, charging_rate)
                best_air_taxi['location'] = nearest_vertiport
                best_air_taxi['availability_time'] += charging_time
                best_air_taxi['battery_level'] = battery_capacity
        else:
            print(f"No available air taxi for trip from {start_location} to {end_location} starting at {start_time} and ending at {end_time}")
    
    return air_taxi_schedule

def simulate_air_taxi_operations(air_taxis, trips, vertiports, battery_threshold, battery_capacity, charging_rate, duration_in_minutes):
    current_time = 0
    completed_trips = []

    while current_time < duration_in_minutes:
        available_trips = [trip for trip in trips if trip['start_time'] == current_time and trip not in completed_trips]
        
        if available_trips:
            schedule = assign_air_taxis_greedy(air_taxis, available_trips, vertiports, battery_threshold, battery_capacity, charging_rate, current_time)
            for air_taxi_id, assigned_trips in schedule.items():
                for trip in assigned_trips:
                    completed_trips.append(trip)

        current_time += 1
    return air_taxis, completed_trips

# Tkinter GUI setup
def start_application():
    def on_run_button_click():
        canvas.delete("all")
        result_label.config(text="")
        
        canvas_width = 720  # Adjust canvas width to fit the range
        canvas_height = 720 + 5 * 40  # Adjust canvas height to fit the range and additional 5 units lower
        scale = 40  # Adjusted scale to ensure everything fits within the canvas
        min_x, max_x = -2, 15
        min_y, max_y = -2, 9

        # Randomize air taxi locations
        air_taxis = [
            {'id': 'AT1', 'location': (random.randint(0, 10), random.randint(0, 10)), 'battery_level': 100, 'availability_time': 0},
            {'id': 'AT2', 'location': (random.randint(0, 10), random.randint(0, 10)), 'battery_level': 100, 'availability_time': 0},
            {'id': 'AT3', 'location': (random.randint(0, 10), random.randint(0, 10)), 'battery_level': 100, 'availability_time': 0}
        ]
        
        # Randomize trip coordinates
        trips = []
        for i in range(5):  # Generate 5 random trips
            start_time = random.randint(0, 50)
            end_time = start_time + random.randint(5, 15)
            start_location = (random.randint(0, 10), random.randint(0, 10))
            end_location = (random.randint(0, 10), random.randint(0, 10))
            trips.append({'start_time': start_time, 'end_time': end_time, 'start_location': start_location, 'end_location': end_location})
        
        vertiports = [(0, 0), (5, 5), (10, 10)]
        battery_threshold = 20
        battery_capacity = 100
        charging_rate = 10
        duration_in_minutes = 60
        
        air_taxis, completed_trips = simulate_air_taxi_operations(air_taxis, trips, vertiports, battery_threshold, battery_capacity, charging_rate, duration_in_minutes)
        
        result_text = "Simulation Results:\n\n"
        for air_taxi in air_taxis:
            result_text += f"Air Taxi {air_taxi['id']} - Location: {air_taxi['location']}, Battery Level: {air_taxi['battery_level']}, Availability Time: {air_taxi['availability_time']}\n"
        result_text += "\nCompleted Trips:\n"
        for trip in completed_trips:
            result_text += f"Trip from {trip['start_location']} to {trip['end_location']} starting at {trip['start_time']} and ending at {trip['end_time']}\n"
        
        result_label.config(text=result_text)
        visualize_operations(canvas, air_taxis, completed_trips, min_x, max_x, min_y, max_y, canvas_height, scale)

    def visualize_operations(canvas, air_taxis, completed_trips, min_x, max_x, min_y, max_y, canvas_height, scale):
        canvas.delete("all")
        
        shift_y = 9  # Shift the grid by 9 units down
        
        # Draw grid and labels
        for i in range(min_x, max_x + 1):
            canvas.create_line((i - min_x)*scale, 0, (i - min_x)*scale, (max_y - min_y + 1 + shift_y)*scale, fill="lightgray")
            canvas.create_text((i - min_x)*scale, (max_y - min_y + 1 + shift_y)*scale + 10, text=str(i), fill="black")  # X-axis labels
        for i in range(min_y, max_y + 1):
            canvas.create_line(0, canvas_height - (i - min_y + shift_y)*scale, (max_x - min_x + 1)*scale, canvas_height - (i - min_y + shift_y)*scale, fill="lightgray")
            canvas.create_text(-10, canvas_height - (i - min_y + shift_y)*scale, text=str(i), fill="black", anchor=tk.E)  # Y-axis labels

        # Mark the origin
        canvas.create_oval((0 - min_x)*scale-5, canvas_height-(0 - min_y + shift_y)*scale-5, (0 - min_x)*scale+5, canvas_height-(0 - min_y + shift_y)*scale+5, fill="red")
        canvas.create_text((0 - min_x)*scale + 10, canvas_height-(0 - min_y + shift_y)*scale - 10, text="Origin (0,0)", fill="red", anchor=tk.W)

        # Draw air taxis
        for air_taxi in air_taxis:
            x, y = air_taxi['location']
            canvas.create_oval((x - min_x)*scale-5, canvas_height-(y - min_y + shift_y)*scale-5, (x - min_x)*scale+5, canvas_height-(y - min_y + shift_y)*scale+5, fill="blue")
            canvas.create_text((x - min_x)*scale, canvas_height-(y - min_y + shift_y)*scale-10, text=air_taxi['id'], fill="blue")
        
        # Draw trips
        for trip in completed_trips:
            x1, y1 = trip['start_location']
            x2, y2 = trip['end_location']
            canvas.create_line((x1 - min_x)*scale, canvas_height-(y1 - min_y + shift_y)*scale, (x2 - min_x)*scale, canvas_height-(y2 - min_y + shift_y)*scale, fill="red")
            canvas.create_oval((x1 - min_x)*scale-3, canvas_height-(y1 - min_y + shift_y)*scale-3, (x1 - min_x)*scale+3, canvas_height-(y1 - min_y + shift_y)*scale+3, fill="green")
            canvas.create_text((x1 - min_x)*scale, canvas_height-(y1 - min_y + shift_y)*scale-10, text=f"Start ({x1},{y1})", fill="green")
            canvas.create_oval((x2 - min_x)*scale-3, canvas_height-(y2 - min_y + shift_y)*scale-3, (x2 - min_x)*scale+3, canvas_height-(y2 - min_y + shift_y)*scale+3, fill="orange")
            canvas.create_text((x2 - min_x)*scale, canvas_height-(y2 - min_y + shift_y)*scale-10, text=f"End ({x2},{y2})", fill="orange")

    # Create the main window
    root = tk.Tk()
    root.title("Air Taxi Operation Simulation")

    # Create and place widgets
    run_button = tk.Button(root, text="Run Simulation", command=on_run_button_click, font=("Helvetica", 14))
    run_button.pack(pady=20)
    
    result_label = tk.Label(root, text="", font=("Helvetica", 12), justify=tk.LEFT)
    result_label.pack(pady=20)
    
    canvas = tk.Canvas(root, width=1080, height=1080, bg="white")  # Adjusted height to fit additional Y-axis units
    canvas.pack(pady=20)

    # Run the Tkinter event loop
    root.mainloop()

# Start the application
start_application()