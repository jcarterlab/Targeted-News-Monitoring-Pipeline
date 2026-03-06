# 📰 Targeted-News-Analysis-Pipeline

A Python pipeline that scrapes news websites and uses a large language model to identify and summarize news stories relevant to a specific entity and risk type.

The system is designed for targeted monitoring of news events, allowing organizations to detect emerging risks such as supply chain disruptions, regulatory changes or geopolitical events.


## 🔍 Overview

The pipeline performs the following steps:

1. Scrapes headlines from a list of news sources
2. Filters headlines and batches them for LLM processing
3. Uses a Gemini model to identify risk-relevant headlines
4. Scrapes full article text for selected stories
5. Generates summaries of the relevant events

This approach allows large volumes of news to be processed efficiently while focusing only on stories relevant to a specific risk profile.


## 💻 Example Use

Monitoring news for events relevant to:

- Entity: a logistics firm
- Risk type: port disruption events
- Confidence threshold: 95%

The model evaluates batches of headlines and returns the indices of those considered relevant.

Example response:

```python
[3, 7, 12]
```

These indices are validated and used to select rows from the headline dataset.


## 🗂️ Project Structure

```
targeted-news-analysis-pipeline
│
├── main.py
├── config.py
├── links.csv
│
└── risk_pipeline
    ├── scrape_headlines.py
    ├── identify_risk_headlines.py
    ├── scrape_stories.py
    ├── summarise_stories.py
    └── prompts.py
```

## 🚀 Getting Started

### Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```


### Environment Variables

Create a .env file in the project root containing your Gemini API key:

```bash
GEMINI_API_KEY=your_api_key_here
```


### Running the Pipeline

Run the pipeline with:

```python
python main.py
```


## 📃 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](https://github.com/jcarterlab/Targeted-News-Analysis-Pipeline/blob/main/LICENSE) file for details.