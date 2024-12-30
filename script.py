import requests
import json

# Function to make the POST request
def fetch_award_data(agency, recepient):
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"  # Replace with the actual API endpoint URL

    # Request payload
    payload = {
        "subawards": False,
        "limit": 100,
        "page": 10,
        "filters": {
            "award_type_codes": ["A", "B", "C"],
            "time_period": [{"start_date": "2018-10-01", "end_date": "2019-09-30"}]
        },
        "fields": [
            "Award ID",
            "Recipient Name",
            "Start Date",
            "End Date",
            "Award Amount",
            "Awarding Agency",
            "Awarding Sub Agency",
            "Contract Award Type",
            "Award Type",
            "Funding Agency",
            "Funding Sub Agency"
        ]
    }

    # Add the agency filter dynamically
    payload["fields"]["Awarding Agency"] = agency
    payload["fields"]["Recipient Name"] = recepient

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Make the API call
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        # Check the status code
        if response.status_code == 200:
            print("API Response:")
            print(json.dumps(response.json(), indent=4))
        else:
            print(f"Error: Received status code {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"An error occurred: {e}")

# Main function to get user input and call the API
if __name__ == "__main__":
    agency = input("Enter the agency: ")
    recepient = input("Enter the recepient: ")
    fetch_award_data(agency, recepient)
