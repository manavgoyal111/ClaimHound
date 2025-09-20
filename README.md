# Tweet Prediction Analyzer

A Python-based Streamlit web app to extract, analyze, and visualize predictions from tweets using LangExtract.

---

## Features

- Extract predictions from tweet datasets (CSV files) using LangExtract.
- View, filter, and validate predictions interactively.
- Visualize prediction statistics and trends.
- LLM verification integration for predictions.
- Export validated predictions.

---

## Prerequisites

- Python 3.9+
- Streamlit
- LangExtract Python SDK
- pandas, plotly

---

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/tweet-prediction-analyzer.git
cd tweet-prediction-analyzer
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with the following variables:

```env
INPUT_FOLDER=path/to/csv/folder
LANGEXTRACT_API_KEY=your_langextract_api_key
```

- `INPUT_FOLDER`: Path to the folder containing your tweet CSV files.
- `LANGEXTRACT_API_KEY`: API key for LangExtract.

---

## CSV File Structure

Your tweet CSV should have the following columns:

```
id,tweetText,tweetURL,type,tweetAuthor,handle,replyCount,quoteCount,retweetCount,likeCount,views,bookmarkCount,createdAt,allMediaURL,videoURL
```

- `id`: Unique tweet identifier
- `tweetText`: Content of the tweet
- `tweetURL`: URL of the tweet
- `type`: Type of tweet (optional)
- `tweetAuthor`: Name of the author
- `handle`: Twitter handle
- `replyCount`, `quoteCount`, `retweetCount`, `likeCount`, `views`, `bookmarkCount`: Tweet engagement metrics
- `createdAt`: Timestamp of the tweet (format `YYYY-MM-DD HH:MM:SS`)
- `allMediaURL`, `videoURL`: Media links

---

## Running the App Locally

```bash
streamlit run app.py
```

- Open your browser at `http://localhost:8501`.
- Use the sidebar to manage data, run extraction, and view analytics.

---

## Project Structure

```
tweet-prediction-analyzer/
│
├── app.py                  # Main Streamlit app
├── main.py                 # TweetPredictionAnalyzer class and extraction logic
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── README.md               # Documentation
├── outputs/                # Folder for predictions and JSON files
└── data/                   # CSV files (tweets)
```

---

## License

MIT License
