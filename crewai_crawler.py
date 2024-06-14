import time
from crewai import Agent, Crew, Process, Task
from crewai_tools import ScrapeWebsiteTool
from dotenv import load_dotenv

def scraper_agent(system_message) -> Agent:
    scrape_tool = ScrapeWebsiteTool()
    return Agent(
        role="Website Scraper",
        goal="Scrape the tiers and prices for the url",
        backstory=system_message,
        tools=[scrape_tool],
        allow_delegation=False,
    )

def scrape_content_task(agent: Agent, user_message) -> Task:
    return Task(
        description=user_message,
        expected_output="JSON with fields from scraped url.",
        agent=agent,
    )

def scrape_crewai(url, user_message, system_message):
    load_dotenv()

    start_time = time.time()
    scraper = scraper_agent(system_message)
    scrape_content = scrape_content_task(scraper, user_message)

    crew = Crew(
        agents=[scraper],
        tasks=[scrape_content],
        process=Process.sequential,
    )

    inputs = {
        "topic": user_message,
        "url": url,
        "suggestion": system_message,
    }

    result = crew.kickoff(inputs=inputs)

    # Stop the timer
    end_time = time.time()
    # Calculate the elapsed time
    elapsed_time = end_time - start_time

    return {
            'raw_data': result,
            'elapsed_time': elapsed_time
        }
