import pandas as pd
import numpy as np
import re
import time
from risk_pipeline.prompts import headline_identification_prompt 


# ----------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------

def combine_headlines(headlines):
    """
    Combines all headlines texts into a single string separated by index numbers
    """
    indices = headlines.Headline.index

    combined_text = []
    for i, headline in enumerate(headlines.Headline):
        combined_text.extend(str(indices[i]+1) + '. ' + headline + ' ')

    return ''.join(combined_text)


def split_headlines(combined_headlines, llm_headline_batch_size):
    """
    Splits the combined headlines text into batches ready for LLM processing
    """
    split_headlines = re.split(r'(?=\b\d+\.)', combined_headlines)
    no_of_splits = int(np.ceil(len(split_headlines) / llm_headline_batch_size))

    chuncks = []
    for i in range(no_of_splits):
        start = i * llm_headline_batch_size
        end = (i+1) * llm_headline_batch_size
        chuncks.append(
            ' '.join(split_headlines[start:end])
        )
    return chuncks


def extract_index_numbers(response):
    """
    Extracts the headlines index numbers from a gemini response.
    """
    if response is None:
        print('Error: Gemini response is None')
        return []
    
    text = getattr(response, 'text', None)

    if not text:
        print('Error: Gemini returned empty response')
        return []
            
    try: 
        if "[" not in text or "]" not in text:
            print('Error: no python list found in Gemini response')
            return []
        
        inside = text.split('[', 1)[1].split(']', 1)[0]
        indices = [int(x.strip()) - 1 for x in inside.split(",") if x.strip().isdigit()]
        print('Extracted', str(len(indices)), 'indices')
        return indices
    
    except Exception:
        print('Error: unable to extract index numbers from python list:')
        print(text)
        return []



# ----------------------------------------------------------------------
# RISK HEADINE IDENTIFICATION 
# ----------------------------------------------------------------------

def return_risk_headlines(client, llm_retry_attempts, llm_wait_time, prompt, i):
    """
    Uses Gemini to return identified risk headlines for a given headlines chunk. 
    """
    
    for attempt in range(1, llm_retry_attempts + 1):

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return extract_index_numbers(response)

        except Exception as e:
            if attempt < llm_retry_attempts:
                time.sleep(llm_wait_time * attempt)
                print(f'Error: LLM call failed on attempt {attempt}/{llm_retry_attempts}')
                print(f'Error type: {type(e).__name__}')
                print(f'Error message: {e}')
            else:
                print(f'Error: LLM call failed for chunk {i} after {llm_retry_attempts} attempts: {e}')
                return []


def identify_risk_headlines(
        client, 
        headlines_df, 
        llm_retry_attempts, 
        llm_wait_time, 
        llm_headline_batch_size,
        entity_description, 
        risk_type,
        risk_confidence_threshold
    ):
    """
    Returns a data frame of potential risk headlines from a headlines data frame. 
    """
    combined_headlines = combine_headlines(headlines_df)

    chunks = split_headlines(combined_headlines, llm_headline_batch_size)

    all_indices = []
    for i, chunk in enumerate(chunks):

        prompt = headline_identification_prompt(entity_description, risk_type, risk_confidence_threshold, chunk)

        indices = return_risk_headlines(
            client,
            llm_retry_attempts,
            llm_wait_time,
            prompt,
            i
        )
        all_indices.extend(indices)

    print(f"\nTotal indices: {len(all_indices)}\n")

    return headlines_df.iloc[all_indices]
