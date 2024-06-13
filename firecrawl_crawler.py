from firecrawl import FirecrawlApp
from dotenv import load_dotenv
import os
import time

def scrape_firecrawl(url: str):
    load_dotenv()
    
    # Start the timer
    start_time = time.time()

    # Initialize the FirecrawlApp with your API key
    app = FirecrawlApp(api_key=os.getenv('FIRECRAWL_API_KEY'))
    
    # Scrape a single URL
    scraped_data = app.scrape_url(url, {'pageOptions': {'onlyMainContent': True}})
    
    # Stop the timer
    end_time = time.time()
    # Calculate the elapsed time
    elapsed_time = end_time - start_time
    
    # Check if 'markdown' key exists in the scraped data
    if 'markdown' in scraped_data:
        return {
            'raw_data': scraped_data['markdown'],
            'elapsed_time': elapsed_time
        }
    else:
        raise KeyError("The key 'markdown' does not exist in the scraped data.")