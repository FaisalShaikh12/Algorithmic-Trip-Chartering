import heapq
from collections import defaultdict

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
    
    # Sort trips by start time
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
            print(f"Air Taxi {best_air_taxi['id']} is assigned to trip from {start_location} to {end_location} starting at {adjusted_start_time} and ending at {end_time}")
            best_air_taxi['location'] = end_location
            best_air_taxi['battery_level'] -= required_battery
            best_air_taxi['availability_time'] = end_time  # Ensure availability time is updated to the end time of the trip
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
            print("Debug info:")
            for air_taxi in air_taxis:
                travel_time_to_start = calculate_travel_time(air_taxi['location'], start_location)
                arrival_time = max(current_time, air_taxi['availability_time']) + travel_time_to_start
                required_battery = calculate_required_battery(air_taxi['location'], start_location, end_location)
                print(f"Air Taxi {air_taxi['id']} - Location: {air_taxi['location']}, Battery: {air_taxi['battery_level']}, Availability: {air_taxi['availability_time']}, Travel Time: {travel_time_to_start}, Arrival Time: {arrival_time}, Required Battery: {required_battery}")
    
    return air_taxi_schedule

def simulate_air_taxi_operations(air_taxis, trips, vertiports, battery_threshold, battery_capacity, charging_rate, duration_in_minutes):
    current_time = 0
    completed_trips = []

    while current_time < duration_in_minutes:
        print(f"Time: {current_time}")
        available_trips = [trip for trip in trips if trip['start_time'] == current_time and trip not in completed_trips]
        
        if available_trips:
            schedule = assign_air_taxis_greedy(air_taxis, available_trips, vertiports, battery_threshold, battery_capacity, charging_rate, current_time)
            for air_taxi_id, assigned_trips in schedule.items():
                for trip in assigned_trips:
                    print(f"Air Taxi {air_taxi_id} is assigned to trip from {trip['start_location']} to {trip['end_location']} starting at {trip['start_time']} and ending at {trip['end_time']}")
                    completed_trips.append(trip)
        for air_taxi in air_taxis:
            print(f"Air Taxi {air_taxi['id']} has battery level {air_taxi['battery_level']} and is at location {air_taxi['location']} with availability time {air_taxi['availability_time']}")

        current_time += 1

air_taxis = [
    {'id': 'AT1', 'location': (1, 1), 'battery_level': 100, 'availability_time': 0},
    {'id': 'AT2', 'location': (2, 2), 'battery_level': 100, 'availability_time': 0},
    {'id': 'AT3', 'location': (3, 3), 'battery_level': 100, 'availability_time': 0}
]
trips = [
    {'start_time': 5, 'end_time': 10, 'start_location': (2, 2), 'end_location': (3, 3)},
    {'start_time': 15, 'end_time': 20, 'start_location': (1, 1), 'end_location': (4, 4)},
    {'start_time': 25, 'end_time': 30, 'start_location': (2, 2), 'end_location': (5, 5)},
    {'start_time': 35, 'end_time': 40, 'start_location': (4, 4), 'end_location': (6, 6)}
]
vertiports = [(0, 0), (5, 5), (10, 10)]
battery_threshold = 20
battery_capacity = 100
charging_rate = 10  # Units of charge per minute
duration_in_minutes = 60

simulate_air_taxi_operations(air_taxis, trips, vertiports, battery_threshold, battery_capacity, charging_rate, duration_in_minutes)
