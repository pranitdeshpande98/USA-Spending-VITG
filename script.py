import requests
import json
from tabulate import tabulate  # Install with `pip install tabulate`

# Function to make the POST request
def fetch_award_data(agency_name):
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

    # Request payload
    payload = {
        "fields": [
            "Award ID",
            "Recipient Name",
            "Award Amount",
            "Total Outlays",
            "Description",
            "Contract Award Type"
        ],
        "filters": {
            "time_period": [{"start_date": "2007-10-01", "end_date": "2025-09-30"}],
            "agencies": [
                {
                    "type": "awarding",
                    "tier": "subtier",
                    "name": agency_name
                }
            ],
            "award_type_codes": ["A", "B", "C", "D"]
        },
        "limit": 100,
        "order": "desc",
        "page": 1,
        "sort": "Award Amount",
        "subawards": False
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Make the API call
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        # Check the status code
        if response.status_code == 200:
            data = response.json().get("results", [])
            if data:
                # Process and display results in a clean table
                table_data = [
                    [
                        item.get("Award ID", "N/A"),
                        item.get("Recipient Name", "N/A"),
                        f"${item.get('Award Amount', 0) or 0:,.2f}",
                        f"${item.get('Total Outlays', 0) or 0:,.2f}",
                        item.get("Description", "N/A"),
                        item.get("Contract Award Type", "N/A")
                    ]
                    for item in data
                ]
                print(tabulate(table_data, headers=["Award ID", "Recipient Name", "Award Amount", 
                                                    "Total Outlays", "Description", "Contract Type"], tablefmt="pretty"))
            else:
                print("No results found for the given agency.")
        else:
            print(f"Error: Received status code {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
    except json.JSONDecodeError:
        print("Failed to parse JSON response.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Main function to get user input and call the API
if __name__ == "__main__":
    agency_name = input("Enter the awarding agency name: ")
    fetch_award_data(agency_name)
