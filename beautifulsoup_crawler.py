import requests
from bs4 import BeautifulSoup
import time

def scrape_beautiful_soup(url: str):
    # Start the timer
    start_time = time.time()

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    response = session.get(url)
    
    soup = BeautifulSoup(response.content, 'html.parser')

    # Stop the timer
    end_time = time.time()
    # Calculate the elapsed time
    elapsed_time = end_time - start_time

    return {
        'raw_data': str(soup),
        'elapsed_time': elapsed_time
    }
