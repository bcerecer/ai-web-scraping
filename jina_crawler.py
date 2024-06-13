import requests
import time

def scrape_jina(url: str) -> str:
  # Start the timer
  start_time = time.time()

  response = requests.get("https://r.jina.ai/" + url)

  # Stop the timer
  end_time = time.time()
  # Calculate the elapsed time
  elapsed_time = end_time - start_time

  return {
      'raw_data': response.text,
      'elapsed_time': elapsed_time
  }
