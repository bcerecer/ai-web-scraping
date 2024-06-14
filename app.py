from beautifulsoup_crawler import scrape_beautiful_soup
from crewai_crawler import scrape_crewai
from firecrawl_crawler import scrape_firecrawl
from datetime import datetime
from dotenv import load_dotenv
from jina_crawler import scrape_jina
from openai import OpenAI
import os
import pandas as pd 
import json 
import tiktoken
import re
import csv

def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def get_url_and_fields():
    print("Select the website you want to scrape:")
    print("1. Redfin (San Francisco Real Estate)")
    print("2. OpenAI ChatGPT Pricing")
    print("3. Custom URL")
    choice = input("\nEnter the number corresponding to your choice: ")

    if choice == '1':
        url = 'https://www.redfin.com/city/17151/CA/San-Francisco'
        fields = ["Address", "Real Estate Agency", "Price", "Beds", "Baths", "Sqft", "Home Type", "Listing Age", "Picture of home URL", "Listing URL"]
    elif choice == '2':
        url = 'https://openai.com/chatgpt/pricing/'
        fields = ["Pricing"]
    elif choice == '3':
        url = input("Enter the custom URL you want to scrape: ")
        if not is_valid_url(url):
            print("The provided URL is not valid.")
            return None, None
        fields = input("What fields would you like to scrape from the website (separate them with a comma)? ").split(',')
    else:
        print("Invalid choice. Exiting.")
        return None, None

    return url, fields

def save_raw_data(raw_data, timestamp, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    raw_output_path = os.path.join(output_folder, f'rawData_{timestamp}.md')
    with open(raw_output_path, 'w', encoding='utf-8') as f:
        f.write(raw_data)
    print(f"Raw data saved to {raw_output_path}")

def openai_formatted_data(crawler, data, system_message, user_message):
    # Check if the data exceeds 10,000 words
    if len(data.split()) > 10000:
        print(f"Invalid raw data for {crawler}, raw data is over 10k tokens!")
        return None

    load_dotenv()
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"{user_message} + \n\n From the provided text: {data}"}
        ]
    )

    if response and response.choices:
        formatted_data = response.choices[0].message.content.strip()
        print(f"Formatted data received from API: {formatted_data}")
        try:
            parsed_json = json.loads(formatted_data)
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            print(f"Formatted data that caused the error: {formatted_data}")
            raise ValueError("The formatted data could not be decoded into JSON.")
        return parsed_json
    else:
        raise ValueError("The OpenAI API response did not contain the expected choices data.")


def save_formatted_data(formatted_data, timestamp, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, f'sorted_data_{timestamp}.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(formatted_data, f, indent=4)
    print(f"Formatted data saved to {output_path}")

def save_csv_data(raw_data, openai_formatted_data, output_folder):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_raw_data(raw_data, timestamp, output_folder)
    if openai_formatted_data is not None: 
        save_formatted_data(openai_formatted_data, timestamp, output_folder)
    else:
        print("Didn't have any formatted data to save!")

def count_tokens(input_string: str) -> int:
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(input_string)
    return len(tokens)

def calculate_cost(input_string: str, cost_per_million_tokens: float = 5) -> float:
    num_tokens = count_tokens(input_string)
    total_cost = (num_tokens / 1_000_000) * cost_per_million_tokens
    return total_cost

def add_csv_row(crawler_name, crawler_data, formatted_data):
    raw_data = crawler_data['raw_data']
    completion_time = crawler_data['elapsed_time']
    cost = (calculate_cost(raw_data))
    # Extract examples using OpenAI
    raw_data_example = raw_data # should extract only first instance of raw_data
    formatted_data_example = formatted_data # should extract only first instance of formatted_data
    # Add a row with the following data
    row = [crawler_name, completion_time, cost, '', '', raw_data_example, formatted_data_example]
    # Append the row to the CSV file
    with open('output/comparison.csv', 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(row)

def create_comparison_csv():
    # Create CSV with first row having the headers
    headers = ["Crawler Name", "Completion Time", "Cost", "UX", "Flexibility", "Raw Data Example", "Formatted Data Example"]

    with open('output/comparison.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(headers)

if __name__ == "__main__":
    url, fields = get_url_and_fields()
    if not url or not fields:
        print("No valid URL and fields provided. Exiting program.")
    else:
        try:
            system_message = """You are an intelligent text extraction and conversion assistant. Your task is to extract structured information from the given text and convert it into a pure JSON format. The JSON should contain only the structured data extracted from the text, with no additional commentary, explanations, or extraneous information. You could encounter cases where you can't find the data of the fields you have to extract or the data will be in a foreign language. Please process the following text and provide the output in pure JSON format with no words before or after the JSON:"""
            user_message = f"Extract the following information {fields} "
            print(f"Scraping {url} for fields: {fields}")
            # Firecrawl
            crawler = 'firecrawl'
            firecrawl_result = scrape_firecrawl(url)
            firecrawl_formatted_data = openai_formatted_data(crawler, firecrawl_result['raw_data'], system_message, user_message)
            save_csv_data(firecrawl_result['raw_data'], firecrawl_formatted_data, f'output/{crawler}')
            # Jina AI
            crawler = 'jina'
            jina_result = scrape_jina(url)
            jina_formatted_data = openai_formatted_data(crawler, jina_result['raw_data'], system_message, user_message)
            save_csv_data(jina_result['raw_data'], jina_formatted_data, f'output/{crawler}')
            # Beautiful Soup
            crawler = 'beautiful-soup'
            beautiful_soup_result = scrape_beautiful_soup(url)
            beautiful_soup_formatted_data = openai_formatted_data(crawler, beautiful_soup_result['raw_data'], system_message, user_message)
            save_csv_data(beautiful_soup_result['raw_data'], beautiful_soup_formatted_data, f'output/{crawler}')
            # CrewAI
            crawler = 'crewai'
            crewai_result = scrape_crewai(url, f"{user_message} from the url: {url}", system_message)
            save_csv_data(crewai_result['raw_data'], crewai_result['raw_data'], f'output/{crawler}')
            # Create comparison csv
            create_comparison_csv()
            add_csv_row("Firecrawl", firecrawl_result, firecrawl_formatted_data)
            add_csv_row("Jina AI", jina_result, jina_formatted_data)
            add_csv_row("Beautiful Soup", beautiful_soup_result, beautiful_soup_formatted_data)
            add_csv_row("CrewAI", crewai_result, crewai_result['raw_data'])
        except Exception as e:
            print(f"An error occurred: {e}")
