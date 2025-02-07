import requests
import json
from datetime import datetime
from textwrap import wrap
from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text
from rich.panel import Panel
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from statistics import mean, median, stdev
from rich.layout import Layout
import google.generativeai as genai


def format_currency(amount):
    """Format currency values with appropriate suffixes (K, M, B)"""
    if amount is None or amount == 0:
        return "$0"
    
    if amount >= 1_000_000_000:
        return f"${amount/1_000_000_000:.1f}B"
    elif amount >= 1_000_000:
        return f"${amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount/1_000:.1f}K"
    else:
        return f"${amount:,.2f}"

def truncate_text(text, max_length=50):
    """Truncate text and add ellipsis if needed"""
    if not text or text == "N/A":
        return "N/A"
    return text[:max_length] + "..." if len(text) > max_length else text

def calculate_statistics(data):
    """Calculate various statistics from the award data"""
    if not data:
        return None
    
    # Convert data to pandas DataFrame for easier analysis
    df = pd.DataFrame(data)
    
    # Basic financial statistics
    award_amounts = [x.get('Award Amount', 0) or 0 for x in data]
    stats = {
        'total_awards': len(data),
        'total_value': sum(award_amounts),
        'average_award': mean(award_amounts),
        'median_award': median(award_amounts),
        'std_dev': stdev(award_amounts) if len(award_amounts) > 1 else 0,
        'max_award': max(award_amounts),
        'min_award': min(x for x in award_amounts if x > 0),
    }
    
    # Contract type analysis
    contract_types = Counter(item.get('Contract Award Type', 'Unknown') for item in data)
    stats['contract_types'] = dict(contract_types)
    
    # Top recipients
    recipient_totals = {}
    for item in data:
        recipient = item.get('Recipient Name', 'Unknown')
        amount = item.get('Award Amount', 0) or 0
        recipient_totals[recipient] = recipient_totals.get(recipient, 0) + amount
    
    stats['top_recipients'] = dict(sorted(recipient_totals.items(), 
                                        key=lambda x: x[1], 
                                        reverse=True)[:5])
    
    return stats

def create_visualizations(data, agency_name):
    """Create and save visualizations of the award data"""
    plt.style.use('classic')  # Using classic style instead of seaborn
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(15, 10))
    fig.suptitle(f'Award Analysis for {agency_name}', fontsize=16)
    
    # 1. Contract Types Distribution
    plt.subplot(2, 2, 1)
    contract_types = Counter(item.get('Contract Award Type', 'Unknown') for item in data)
    plt.pie(contract_types.values(), labels=contract_types.keys(), autopct='%1.1f%%')
    plt.title('Distribution of Contract Types')
    
    # 2. Award Amounts Distribution
    plt.subplot(2, 2, 2)
    award_amounts = [x.get('Award Amount', 0) or 0 for x in data]
    plt.hist(award_amounts, bins=20, color='skyblue', edgecolor='black')
    plt.title('Distribution of Award Amounts')
    plt.xlabel('Award Amount ($)')
    plt.ylabel('Frequency')
    
    # 3. Top Recipients
    plt.subplot(2, 2, (3, 4))
    recipient_totals = {}
    for item in data:
        recipient = item.get('Recipient Name', 'Unknown')
        amount = item.get('Award Amount', 0) or 0
        recipient_totals[recipient] = recipient_totals.get(recipient, 0) + amount
    
    top_recipients = dict(sorted(recipient_totals.items(), 
                               key=lambda x: x[1], 
                               reverse=True)[:10])
    
    # Truncate long recipient names for better visualization
    truncated_names = [truncate_text(name, 30) for name in top_recipients.keys()]
    
    plt.barh(truncated_names, list(top_recipients.values()), color='lightgreen')
    plt.title('Top 10 Recipients by Total Award Value')
    plt.xlabel('Total Award Value ($)')
    
    # Adjust layout to prevent text overlap
    plt.tight_layout()
    
    # Save the figure with high DPI for better quality
    plt.savefig('award_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()



def analyze_with_llm(text):
  """Analyzes text using Gemini LLM and returns a dictionary with sentiment, summary, and error message (if any)."""
  genai.configure(api_key="")  # Replace with your actual API key
  try:
    model = genai.GenerativeModel(model_name="gemini-pro")
    response = model.generate_content(text)
    return response.text
  except Exception as e:
    print(f"Error generating response: {e}")
    return "An error occurred while generating the response."
  

def print_statistics(stats, console):
    """Print formatted statistics"""



      # Create a summary of the statistics for LLM interaction
    statistics_summary = f"The analysis found {stats['total_awards']} contracts awarded." \
                     f" The total value of these contracts is {format_currency(stats['total_value'])}, " \
                     f"with an average award of {format_currency(stats['average_award'])} " \
                     f"and a median award of {format_currency(stats['median_award'])}. " \
                     f"The largest contract awarded was for {format_currency(stats['max_award'])}, " \
                     f"while the smallest was for {format_currency(stats['min_award'])}. " \
                     f"The most common contract type was {max(stats['contract_types'], key=stats['contract_types'].get)}." \
                     f" The top recipient was {list(stats['top_recipients'].keys())[0]} " \
                     f"with a total award value of {format_currency(list(stats['top_recipients'].values())[0])}."

  # Generate LLM responses
    sentiment_response = analyze_with_llm(f"Analyze the sentiment of the following statement: '{statistics_summary}'")
    summary_response = analyze_with_llm(f"Summarize the following statement in a concise and informative manner: '{statistics_summary}'")

    console.print(f"\n[bold green]Gemini LLM Analysis:")
    console.print(f"Sentiment Analysis:\n{sentiment_response}")
    console.print(f"Summary:\n{summary_response}")


    # Create a layout for statistics
    layout = Layout()
    layout.split_column(
        Layout(name="title"),
        Layout(name="main"),
        Layout(name="details")
    )
    
    # Financial Statistics Table
    financial_table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    financial_table.add_column("Metric", style="cyan")
    financial_table.add_column("Value", style="green")
    
    financial_table.add_row("Total Number of Awards", str(stats['total_awards']))
    financial_table.add_row("Total Value", format_currency(stats['total_value']))
    financial_table.add_row("Average Award", format_currency(stats['average_award']))
    financial_table.add_row("Median Award", format_currency(stats['median_award']))
    financial_table.add_row("Largest Award", format_currency(stats['max_award']))
    financial_table.add_row("Smallest Award", format_currency(stats['min_award']))
    financial_table.add_row("Standard Deviation", format_currency(stats['std_dev']))
    
    # Contract Types Table
    contract_table = Table(title="Contract Types Distribution", 
                         box=box.ROUNDED, 
                         show_header=True, 
                         header_style="bold magenta")
    contract_table.add_column("Contract Type", style="cyan")
    contract_table.add_column("Count", style="green")
    contract_table.add_column("Percentage", style="yellow")
    
    total_contracts = sum(stats['contract_types'].values())
    for contract_type, count in stats['contract_types'].items():
        percentage = (count / total_contracts) * 100
        contract_table.add_row(
            contract_type,
            str(count),
            f"{percentage:.1f}%"
        )
    
    # Top Recipients Table
    recipient_table = Table(title="Top 5 Recipients", 
                          box=box.ROUNDED, 
                          show_header=True, 
                          header_style="bold magenta")
    recipient_table.add_column("Recipient", style="cyan")
    recipient_table.add_column("Total Awards", style="green")
    
    for recipient, amount in stats['top_recipients'].items():
        recipient_table.add_row(
            truncate_text(recipient, 40),
            format_currency(amount)
        )
    
    # Print all tables
    console.print("\n[bold cyan]===== Statistical Analysis =====")
    console.print(Panel(financial_table, title="Financial Statistics"))
    console.print(Panel(contract_table, title="Contract Types"))
    console.print(Panel(recipient_table, title="Top Recipients"))
    console.print("\n[bold green]Visualizations have been saved to 'award_analysis.png'")

    console.print("\n[bold blue]Ask a question about the award data:")
    while True:
        user_question = input("Enter your question (or 'exit' to quit): ")
        if user_question.lower() == 'exit':
            break
        question_prompt = f"Answer the following question based on the provided information: '{statistics_summary}'. Question: '{user_question}'"
        answer = analyze_with_llm(question_prompt)
        console.print(f"Answer: {answer}")

def fetch_award_data(agency_name, recipients, recipient_locations):
    """Fetch and display award data in a formatted table with statistics"""
    url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
    if agency_name == "":
        agency_name = "Centers for Medicare and Medicaid Services"
    payload = {
        "fields": [
            "Award ID",
            "Recipient Name",
            "Award Amount",
            "Total Outlays",
            "Description",
            "Contract Award Type",
            "Period of Performance Start Date",
            "Period of Performance Current End Date"
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
            "award_type_codes": ["A", "B", "C", "D"],
            "recipient_search_text": recipients,
            "recipient_locations":recipient_locations
        },
        "limit": 100,
        "order": "desc",
        "page": 1,
        "sort": "Award Amount",
        "subawards": False
    }

    headers = {"Content-Type": "application/json"}
    console = Console()

    try:
        # Make the API call
        with console.status("[bold green]Fetching data..."):
            response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            data = response.json().get("results", [])
            if data:
                # Create and style the table
                table = Table(
                    title=f"\nContract Awards for {agency_name}",
                    box=box.ROUNDED,
                    header_style="bold cyan",
                    padding=(0, 1),
                    show_lines=True
                )

                # Add columns
                table.add_column("Award ID", style="white", no_wrap=True)
                table.add_column("Recipient", style="green")
                table.add_column("Amount", justify="right", style="yellow")
                table.add_column("Description", style="blue")
                table.add_column("Type", style="magenta")
                table.add_column("Duration", style="cyan")

                # Add rows
                for item in data:
                    # Format dates
                    start_date = datetime.strptime(item.get("Period of Performance Start Date", ""), "%Y-%m-%d").strftime("%m/%d/%Y") if item.get("Period of Performance Start Date") else "N/A"
                    end_date = datetime.strptime(item.get("Period of Performance Current End Date", ""), "%Y-%m-%d").strftime("%m/%d/%Y") if item.get("Period of Performance Current End Date") else "N/A"
                    
                    table.add_row(
                        item.get("Award ID", "N/A"),
                        truncate_text(item.get("Recipient Name", "N/A"), 30),
                        format_currency(item.get("Award Amount")),
                        truncate_text(item.get("Description", "N/A"), 50),
                        truncate_text(item.get("Contract Award Type", "N/A"), 20),
                        f"{start_date}\nto\n{end_date}"
                    )

                # Print main table
                console.print(f"\nFound {len(data)} contract awards for {agency_name}")
                console.print(table)
                
                # Calculate and print statistics
                stats = calculate_statistics(data)
                print_statistics(stats, console)
                
                # Create visualizations
                create_visualizations(data, agency_name)
                
            else:
                console.print(f"\nNo results found for {agency_name}", style="bold red")
        else:
            console.print(f"Error: Received status code {response.status_code}", style="bold red")
            console.print(response.text)
            
    except requests.exceptions.RequestException as e:
        console.print(f"Network error: {e}", style="bold red")
    except json.JSONDecodeError:
        console.print("Failed to parse JSON response.", style="bold red")
    except Exception as e:
        console.print(f"An unexpected error occurred: {e}", style="bold red")

if __name__ == "__main__":
    agency_name = input("Enter the awarding agency name: ")
    recipient_name = input("Enter the receipient name (optional): ") 
    recipient_state = input("Enter the recipient state (optional): ")
    recipient_country = input("Enter the recipient country (optional): ")

    if recipient_name:
        recipients = [recipient_name]
    else:
        recipients = ["VITG Corp"]
   
    recipient_locations = []
    if recipient_state and recipient_country:
        recipient_locations = [{
            "state": recipient_state,
            "country": recipient_country
        }]
    else:
        recipient_locations = [{
            "state": "MD", 
            "country": "USA"
        }]

    fetch_award_data(agency_name, recipients, recipient_locations) 