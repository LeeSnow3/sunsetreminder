import os
import requests
from twilio.rest import Client

LAT = "35.91"
LON = "-79.05"

# We request the daily sunset time AND the hourly cloud breakdowns
URL = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={LAT}&longitude={LON}&"
    f"hourly=cloud_cover,cloud_cover_low,cloud_cover_high,cloud_cover_mid&"
    f"daily=sunset&timezone=auto"
)

try:
    response = requests.get(URL)
    data = response.json()
    
    # 1. Get the sunset time
    sunset_raw = data['daily']['sunset'][0]  # "2026-05-22T20:15"
    sunset_time = sunset_raw.split('T')[1]    # "20:15"
    sunset_hour_str = sunset_raw.split(':')[0] + ":00" # Match the hourly forecast format ("2026-05-22T20:00")

    # 2. Find the index in the hourly array that matches our sunset hour
    hourly_times = data['hourly']['time']
    sunset_index = hourly_times.index(sunset_hour_str)
    
    # 3. Pull cloud metrics for that exact hour
    total_clouds = data['hourly']['cloud_cover'][sunset_index]
    low_clouds = data['hourly']['cloud_cover_low'][sunset_index]
    mid_clouds = data['hourly']['cloud_cover_mid'][sunset_index]
    high_clouds = data['hourly']['cloud_cover_high'][sunset_index]
    
    # 4. Write some fun logic to evaluate the sunset potential
    if low_clouds > 70:
        condition = "It's looking pretty overcast down low, so the horizon might be blocked. ☁️"
    elif high_clouds > 40 and low_clouds < 20:
        condition = "Perfect conditions! High, wispy clouds are forecast—expect some beautiful pinks and purples! 🎨🌅"
    elif total_clouds < 10:
        condition = "Clear, crisp skies. A classic, unobstructed view! ☀️"
    else:
        condition = f"Scattered cloud cover ({total_clouds}%). Could be an interesting mix!"

    # 5. Format the text message
    message_body = (
        f"Hi Mom! Today's sunset is at {sunset_time}.\n\n"
        f"Sky Report: {condition}\n"
        f"(Clouds - Low: {low_clouds}%, Mid: {mid_clouds}%, High: {high_clouds}%)"
    )
    print(message_body)  # For testing purposes, print the message instead of sending it
    
    """     # Send via Twilio (using your GitHub environment variables)
    client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])
    message = client.messages.create(
        body=message_body,
        from_=os.environ['TWILIO_PHONE_NUMBER'],
        to=os.environ['MOM_PHONE_NUMBER']
    )
    print("Text sent successfully!")
    """
except Exception as e:
    print(f"Error: {e}")

