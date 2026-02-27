import time
from risk_pipeline.prompts import summarization_prompt, executive_summary_prompt


# ----------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------

def return_story_texts_batches(story_texts, llm_story_words_batch_size):
    """
    Groups story texts into batches within a specified maximum batch word size.
    """
    batches = []
    current_batch = []
    words_counter = 0

    for story in story_texts:

        if not isinstance(story, str) or not story.strip():
            continue
        story_words = len(story.split())

        if story_words >= llm_story_words_batch_size:
            if current_batch:
                batches.append(' '.join(current_batch))
                current_batch = []
                words_counter = 0
            print(f'New batch created: {story_words} words')
            batches.append(story)
            continue

        if words_counter + story_words <= llm_story_words_batch_size:
            current_batch.append(story)
            words_counter += story_words
        else:
            joined_current_batch = ' '.join(current_batch)
            print(f'New batch created: {len(joined_current_batch.split())} words')
            batches.append(joined_current_batch)
            current_batch = [story]
            words_counter = story_words

    if current_batch:
        joined_current_batch = ' '.join(current_batch)
        print(f'New batch created: {len(joined_current_batch.split())} words')
        batches.append(joined_current_batch)

    print(f'\nTotal batches: {len(batches)}\n')
    return batches



# ----------------------------------------------------------------------
# RISK SUMMARISATION FUNCTIONS 
# ----------------------------------------------------------------------

def summarise_story_texts_batches(
        client,
        llm_retry_attempts,
        llm_wait_time,
        story_text_batches, 
        today_date, 
        entity_description, 
        risk_type
    ):
    """
    Generates a summary for each batch of story text using an LLM.
    """
    summaries = []

    for i, story_text in enumerate(story_text_batches):

        prompt = summarization_prompt(
            today_date, 
            entity_description, 
            risk_type, 
            story_text
        )

        for attempt in range(1, llm_retry_attempts + 1):
            try:
                summary = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    contents=prompt
                )
                
                if not summary.text:
                    raise ValueError("Error: empty summary text")
                
                print(f'New summary generated: {len(summary.text.split())} words')
                summaries.append(summary.text)
                break

            except Exception as e:
                if attempt < llm_retry_attempts:
                    time.sleep(llm_wait_time * attempt)
                    print(f'Error: LLM call failed on attempt {attempt}/{llm_retry_attempts}')
                    print(f'Error type: {type(e).__name__}')
                    print(f'Error message: {e}')
                else:
                    print(f'Error: LLM call failed for batch {i} after {llm_retry_attempts} attempts: {e}')

    print(f'\nTotal summary words: {len(" ".join(summaries).split())}\n')
    return summaries


def summarise_stories(
        client,
        llm_retry_attempts,
        llm_wait_time,
        llm_story_words_batch_size,
        story_texts, 
        today_date, 
        entity_description, 
        risk_type
    ):
    """
    Generates a single executive summary based on multiple summaries.
    """
    story_text_batches = return_story_texts_batches(story_texts, llm_story_words_batch_size)

    summaries = summarise_story_texts_batches(
        client,
        llm_retry_attempts,
        llm_wait_time,
        story_text_batches, 
        today_date, 
        entity_description, 
        risk_type
    )

    combined_summaries = "\n\n".join(summaries)

    prompt = executive_summary_prompt(today_date, entity_description, risk_type, combined_summaries)

    for attempt in range(1, llm_retry_attempts + 1):
        try:
            executive_summary = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt
            )

            if executive_summary.text:
                return executive_summary.text
            else:
                print('Error: no executive summary text available - retrying')
            
        except Exception as e:
            if attempt < llm_retry_attempts:
                time.sleep(llm_wait_time * attempt)
                print(f'Error: LLM call failed on attempt {attempt}/{llm_retry_attempts}')
                print(f'Error type: {type(e).__name__}')
                print(f'Error message: {e}')
            else:
                print(f'Error: LLM call failed for executive summary after {llm_retry_attempts} attempts: {e}')
            
