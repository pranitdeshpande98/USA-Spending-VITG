import json
import requests
from tabulate import tabulate

# Constants for the API
API_BASE_URL = "https://api.usaspending.gov"
API_ENDPOINT = "/api/v2/search/spending_by_award/"
DEFAULT_FIELDS = [
    "Award ID",
    "Recipient Name",
    "Award Amount",
    "Total Outlays",
    "Description",
    "Contract Award Type",
    "def_codes",
    "COVID-19 Obligations",
    "COVID-19 Outlays",
    "Infrastructure Obligations",
    "Infrastructure Outlays",
    "Awarding Agency",
    "Awarding Subagency",
    "Base Obligation Date",
    "Last Modified Date"
]
DEFAULT_LIMIT = 100


def fetch_awards(filters):
    """
    Fetch awards from the USAspending API using provided filters.
    """
    url = f"{API_BASE_URL}{API_ENDPOINT}"
    payload = {
        "filters": filters,
        "fields": DEFAULT_FIELDS,
        "limit": DEFAULT_LIMIT,
        "page": 1
    }

    # Make the API request
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data.get("results", [])
    else:
        return {"error": f"API error: {response.status_code}", "details": response.text}


def get_filters():
    """
    Gather filter inputs from the user.
    """
    print("Welcome to the Award Search Tool!")

    # Input agency name
    agency_name = input("Enter the Awarding Agency Name (default: Department of Defense): ") or "Department of Defense"

    # Input award type codes
    award_type_codes = input("Enter Award Type Codes (comma-separated, e.g., A,B,C,D; default: A,B,C,D): ") or "A,B,C,D"
    award_type_codes = [code.strip() for code in award_type_codes.split(",")]

    # Optional filters
    filters = {
        "agencies": [
            {
                "type": "awarding",
                "tier": "subtier",
                "name": agency_name
            }
        ],
        "award_type_codes": award_type_codes
    }

    # Input fiscal year
    fiscal_year = input("Enter Fiscal Year (e.g., 2023, or leave blank to skip): ")
    if fiscal_year:
        filters["time_period"] = [{"start_date": f"{fiscal_year}-01-01", "end_date": f"{fiscal_year}-12-31"}]

    # Input recipient name
    recipient_name = input("Enter Recipient Name (or leave blank to skip): ")
    if recipient_name:
        filters["recipient_search_text"] = [recipient_name]

    return filters


def format_number(value):
    """
    Formats a large number into a readable format with commas.
    """
    try:
        if value is not None:
            return f"{float(value):,.2f}"
        return "N/A"
    except (ValueError, TypeError):
        return "N/A"


def print_awards_table(awards):
    """
    Prints the awards in a tabular format.
    """
    if not awards:
        print("No awards found.")
        return

    # Extract relevant fields for the table
    headers = [
        "Award ID", "Recipient Name", "Award Amount", "Total Outlays",
        "Description", "Contract Award Type", "def_codes",
        "COVID-19 Obligations", "COVID-19 Outlays", "Infrastructure Obligations",
        "Infrastructure Outlays", "Awarding Agency", "Awarding Subagency",
        "Base Obligation Date", "Last Modified Date"
    ]
    rows = [
        [
            award.get("Award ID", "N/A"),
            award.get("Recipient Name", "N/A"),
            f"${award.get("Award Amount", 0) or 0:,.2f}",
            f"${award.get("Total Outlays", 0) or 0:,.2f}",
            award.get("Description", "N/A"),
            award.get("Contract Award Type", "N/A"),
            award.get("def_codes", "N/A"),
            f"${award.get("COVID-19 Obligations", 0) or 0:,.2f}",
            f"${award.get("COVID-19 Outlays", 0) or 0:,.2f}",
            f"${award.get("Infrastructure Obligations", 0) or 0:,.2f}",
            f"${award.get("Infrastructure Outlays", 0) or 0:,.2f}",
            award.get("Awarding Agency", "N/A"),
            award.get("Awarding Subagency", "N/A"),
            award.get("Base Obligation Date", "N/A"),
            award.get("Last Modified Date", "N/A")
        ]
        for award in awards
    ]

    # Print table
    print("\n--- Awards Table ---")
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    print("\n--- End of Awards Table ---")


def main():
    """
    Main function to run the award search tool.
    """
    filters = get_filters()
    print("\nFetching awards...")

    # Fetch awards
    awards = fetch_awards(filters)

    # Display results
    if isinstance(awards, list) and awards:
        print_awards_table(awards)
    else:
        print("No awards found or an error occurred.")
        if isinstance(awards, dict) and "error" in awards:
            print(f"Error Details: {awards['details']}")


if __name__ == "__main__":
    main()
