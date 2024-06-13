from scrapegraphai.graphs import SmartScraperGraph
from dotenv import load_dotenv
import os
import time

def scrape_scrapegraph(url: str):
    load_dotenv()
    # Initialize the Scrapegraph with your API key
    openai_key = os.getenv("OPENAI_APIKEY")

    graph_config = {
        "llm": {
            "api_key": openai_key,
            "model": "gpt-3.5-turbo",
        },
    }

    # Start the timer
    start_time = time.time()

    # Create the SmartScraperGraph instance and run it
    print("Before smart_scraper_graph")
    smart_scraper_graph = SmartScraperGraph(
        prompt="get the pricing for each plan",
        source={url},
        config=graph_config,
    )

    result = smart_scraper_graph.run()
    houses = ' '.join(result['houses'])

    # Stop the timer
    end_time = time.time()
    # Calculate the elapsed time
    elapsed_time = end_time - start_time

    return {
        'raw_data': houses,
        'elapsed_time': elapsed_time
    }

    return result