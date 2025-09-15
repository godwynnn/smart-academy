# from django.test import TestCase

# Create your tests here.
from datetime import datetime

def convert_24_to_12_hour(time_24hr_str):
    """
    Converts a 24-hour time string (e.g., "14:30") to a 12-hour format (e.g., "02:30 PM").

    Args:
        time_24hr_str (str): The time in 24-hour format (e.g., "HH:MM").

    Returns:
        str: The time in 12-hour format with AM/PM indicator.
    """
    try:
        # Parse the 24-hour time string into a datetime object
        time_obj = datetime.strptime(time_24hr_str, "%H:%M")

        # Format the datetime object into a 12-hour string with AM/PM
        time_12hr_str = time_obj.strftime("%I:%M")
        return time_12hr_str
    except ValueError:
        return "Invalid time format. Please use HH:MM."

# Example usage:
time1 = "14:30"
time2 = "00:15"
time3 = "12:00"
time4 = "09:45"
time5 = "23:59"

print(f"'{time1}' in 12-hour format: {convert_24_to_12_hour(time1)}")
print(f"'{time2}' in 12-hour format: {convert_24_to_12_hour(time2)}")
print(f"'{time3}' in 12-hour format: {convert_24_to_12_hour(time3)}")
print(f"'{time4}' in 12-hour format: {convert_24_to_12_hour(time4)}")
print(f"'{time5}' in 12-hour format: {convert_24_to_12_hour(time5)}")
print(f"'invalid_time' in 12-hour format: {convert_24_to_12_hour('invalid_time')}")