import requests
from bs4 import BeautifulSoup
import re


# ----------------------------------------------------------------------
# SCRAPING FUNCTIONS
# ----------------------------------------------------------------------

def return_story_elements(story_url, story_tag, story_class, request_timeout):
    """
    Fetches all elements of a specified tag from a given news story url.
    """
    try:
        response = requests.get(story_url, timeout=request_timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: request failed for {story_url}: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")

    elements = soup.find_all(story_tag, class_=story_class) if story_class else soup.find_all(story_tag)

    if not elements:
        print(f"Error: no elements found for {story_url}")

    return elements 


def normalize_story_text(response):
    """
    Returns normalized text from a response as single a string joined by spaces.
    """
    paragraphs = []

    for element in response:
        text = element.get_text(separator=' ', strip=True)
        text = text.replace('\xa0', ' ')
        text = re.sub(r'\s+', ' ', text).strip()

        if text:
            paragraphs.append(text)

    print(f'Paragraphs scraped: {len(paragraphs)}')

    return ' '.join(paragraphs) 


def return_story_text(story_url, story_tag, story_class, request_timeout):
    """
    Fetches elements and normalizes text from a single new story. 
    """
    response = return_story_elements(story_url, story_tag, story_class, request_timeout)

    return normalize_story_text(response)


def scrape_stories(risk_headlines_df, request_timeout):
    """
    Scrapes and returns normalized text for all news stories in the dataframe.
    """
    story_texts = []

    for row in risk_headlines_df.itertuples():
        story_text = return_story_text(row.Link, row.story_tag, row.story_class, request_timeout)

        if story_text:
            story_texts.append(story_text)

    total_words = sum(len(text.split()) for text in story_texts)
    print(f"\nTotal words: {total_words}\n")
    return story_texts