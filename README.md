# Tweet Prediction Analyzer

A Streamlit-based Python application to extract, analyze, and visualize tweet predictions using LangExtract and other analytics.

---

## Features

- Extract predictions from tweets.
- View predictions along with metadata (author, date, tweet link, engagement metrics).
- Validate predictions manually.
- LLM verification of predictions.
- Interactive analytics dashboard:

  - Prediction validation status
  - Prediction accuracy
  - Predictions over time
  - Top authors

- Search and browse all tweets.
- Export validated predictions as CSV.

---

## Requirements

- Python 3.10+
- Streamlit
- Plotly
- Pandas
- LangExtract (Gemini-powered extraction library)

Install dependencies using pip:

```bash
pip install streamlit plotly pandas langextract
```

---

## File Structure

```
project_folder/
├── app.py                  # Streamlit app
├── main.py                 # Core extraction & analysis logic
├── tweets.json             # Raw tweet data
├── predictions.json        # Extracted predictions
├── predictions_viz.html    # Optional LangExtract HTML visualization
└── README.md               # Documentation
```

---

## How to Run

1. Ensure all required files (`tweets.json`, `predictions.json`) exist.
2. Run the Streamlit app:

```bash
streamlit run app.py
```

3. Your default browser will open at `http://localhost:8501` displaying the app.

---

## Usage

### Sidebar Options

- **Data Management**

  - Re-extract predictions
  - Run LLM verification
  - View LLM vs manual verification results

- **Metrics & Charts**

  - Total predictions
  - Validated / unvalidated
  - Accuracy

### Main Tabs

- **Browse Predictions**: Filter, sort, and validate predictions.
- **Analytics**: View interactive charts and timeline.
- **All Tweets**: Browse all tweets with search and engagement metrics.
- **Settings**: Configuration, keywords, and export data options.

---

## Notes

- Predictions extraction relies on LangExtract examples and prompt configuration.
- Visualization uses Plotly and Streamlit for interactivity.
- Manual validation and LLM verification updates are reflected immediately.

---

## Author

Created by Your Name

---

## License

MIT License
