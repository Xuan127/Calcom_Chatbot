import requests

# Define the API endpoint
url = "https://api.cal.com/v1/bookings?apiKey=cal_live_767d038da060f887e1d230a9031e6412"

# Replace with your actual API key
api_key = "cal_live_767d038da060f887e1d230a9031e6412"

# Booking details (replace with actual data)
payload = {
  "eventTypeId": 1181131,
  "start": "2024-10-30T06:00:00.000Z",
  "responses": {
    "name": "Shan Yu Xuan",
    "email": "shanyuxuan2001@gmail.com",
    "location": {
      "value": "inPerson",
      "optionValue": ""
    }
  },
  "metadata": {},
  "timeZone": "Europe/London",
  "language": "en",
  "title": "Debugging between Syed Ali Shahbaz and Hello Hello",
  "status": "PENDING"
}

# Set up headers with authentication
headers = {}

# Send the POST request
response = requests.post(url, headers=headers, json=payload)

# Check and print the response
if response.status_code == 200:
    print("Booking created:", response.json())
else:
    print(f"Error {response.status_code}: {response.text}")
