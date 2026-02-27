import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# ----------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------

def filter_non_headlines(elements):
    """
    Filters a list of elements to remove short, likely non-headline texts.
    """
    try: 
        return [x for x in elements if len(x.text.strip()) >= 25]
    except Exception:
        return []

    

def extract_text(element):
    """
    Returns stripped text from a given element.
    """
    try: 
        return element.text.strip()
    except Exception:
        return None



def extract_link(element, base_url):
    """
    Extracts a link from a BeautifulSoup element.
    Converts relative URLs to absolute URLs.
    """
    try:
        href = element.get("href")
        if not href:
            return None

        return urljoin(base_url, href)

    except Exception:
        return None



# ----------------------------------------------------------------------
# SCRAPING FUNCTIONS
# ----------------------------------------------------------------------

def get_headline_elements(page_url, request_timeout, tag):
    """
    Fetches a webpage and returns all elements matching the given tag.
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; RiskPipelineBot/1.0)"
    }

    try:
        response = requests.get(page_url, headers=headers, timeout=request_timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        return soup.find_all(tag)

    except requests.exceptions.RequestException as e:
        print(f"Error: request failed for {page_url}: {e}")
        return []
    


def create_headlines_dataframe(page_url, request_timeout, tag, base_url, story_tag, story_class):

    """
    Returns a pandas dataframe with headline texts and url links for a single link in links_df.csv. 
    """

    elements = get_headline_elements(page_url, request_timeout, tag)
    filtered_elements = filter_non_headlines(elements)

    texts, links = [], []
    for element in filtered_elements: 
        text = extract_text(element)
        link = extract_link(element, base_url)

        if text and link:
            texts.append(text)
            links.append(link)

    print(f'Headlines returned: {len(texts)}')

    headlines = pd.DataFrame({
        'Headline': texts,
        'Link': links,
        'story_tag': [story_tag for x in texts],
        'story_class': [story_class for x in texts]
    })

    return headlines



def scrape_headlines(request_timeout):
    """
    Returns a pandas dataframe with headline texts and url links for each row in link_df.csv. 
    """
    # reads in the links csv file
    try:
        links_data = pd.read_csv('links.csv', encoding='utf-8')
    except FileNotFoundError:
        raise RuntimeError('links.csv not found')
    
    # raises an error if links csv empty 
    if links_data.empty:
        raise RuntimeError('links.csv is empty')
    
    print(f'\nLinks to be scraped: {len(links_data)}\n')

    # scrapes each link and stores the headlines as a pandas dataframe
    headlines_dfs = []

    for row in links_data.itertuples(index=False):
        try:
            headlines_dfs.append(
                create_headlines_dataframe(
                    row.page_url, 
                    request_timeout,
                    row.tag, 
                    row.base_url,
                    row.story_tag,
                    row.story_class
                )
            )

        except Exception as e:
            print(f"Error: failed processing {row.page_url}: {e}")
            continue
        
    # returns a concatenated headlines dataframe for all links
    if not headlines_dfs:
        raise RuntimeError('no headlines dataframes were created')

    headlines_df = pd.concat(headlines_dfs, ignore_index=True)

    if headlines_df.empty:
        raise RuntimeError("No headlines were extracted from any source")
    
    print(f'\nTotal headlines: {len(headlines_df)}\n')

    return headlines_df