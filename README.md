# 🔮 Tweet Prediction Analyzer

A Python application that extracts, analyzes, and validates prediction statements from tweet data using rule-based NLP and an interactive Streamlit UI.

## ✨ Features

- **Smart Prediction Detection**: Uses rule-based logic + spaCy NLP to identify prediction statements
- **LLM-Powered Verification**: Automatically verify if predictions came true using OpenAI GPT, Anthropic Claude, or Google Gemini
- **Interactive UI**: Streamlit-based interface for browsing and validating predictions
- **Comprehensive Analytics**: Statistics, charts, and timeline analysis with LLM vs manual comparison
- **Manual Validation**: Easy-to-use interface for marking predictions as correct/incorrect
- **Batch Processing**: Verify hundreds of predictions automatically with rate limiting
- **Data Export**: Export validated predictions to CSV
- **Configurable**: All settings managed via .env file

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project files
git clone <repository-url>
cd tweet-prediction-analyzer

# Run the automated setup
python setup.py
```

Or install manually:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configuration

Copy `.env.template` to `.env` and update the CSV path:
```bash
cp .env.template .env
# Edit .env file to point to your CSV file
```

### 3. Prepare Your CSV

Ensure your CSV file has these columns:
- `id` - Tweet ID
- `tweetText` - Tweet content (required)
- `tweetURL` - Link to tweet
- `type` - Tweet type
- `tweetAuthor` - Author name
- `handle` - Twitter handle
- `replyCount` - Number of replies
- `quoteCount` - Number of quotes
- `retweetCount` - Number of retweets
- `likeCount` - Number of likes
- `views` - View count
- `bookmarkCount` - Bookmark count
- `createdAt` - Tweet date/time
- `allMediaURL` - Media URLs
- `videoURL` - Video URL

### 4. Set Up LLM Verification (Optional)

Choose your preferred LLM provider and add the API key to your `.env` file:

**For OpenAI GPT:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key-here
LLM_MODEL=gpt-4  # or gpt-3.5-turbo for cheaper option
```

**For Anthropic Claude:**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-anthropic-key-here
LLM_MODEL=claude-3-sonnet-20240229
```

**For Google Gemini:**
```bash
LLM_PROVIDER=google
GOOGLE_API_KEY=your-google-api-key-here
LLM_MODEL=gemini-pro
```

### 5. Extract Predictions

```bash
python main.py
```

This will:
- Read your CSV file
- Extract all predictions using NLP
- Save results to `output/predictions.json` and `output/all_tweets.json`

### 5. Launch the UI

```bash
streamlit run streamlit_app.py
```

Open your browser to `http://localhost:8501` to access the interactive interface.

## 📁 Project Structure

```
tweet-prediction-analyzer/
├── main.py                 # Core prediction extraction logic
├── streamlit_app.py       # Interactive Streamlit UI
├── setup.py              # Automated setup script
├── requirements.txt      # Python dependencies
├── .env.template        # Environment variables template
├── .env                 # Your configuration (create from template)
├── output/              # Generated JSON files
│   ├── predictions.json # Extracted predictions
│   └── all_tweets.json  # All tweets data
└── README.md           # This file
```

## 🔍 How Prediction Detection Works

The app uses multiple approaches to identify predictions:

### 1. Keyword Detection
Looks for words like: `will`, `predict`, `expect`, `forecast`, `I think`, `believe`, etc.

### 2. Pattern Matching
Uses regex patterns to identify:
- Future tense constructions
- Time-based predictions
- Probability statements

### 3. Advanced NLP (Optional)
If spaCy is installed, also analyzes:
- Part-of-speech tagging
- Named entity recognition
- Syntactic patterns

### 4. Confidence Scoring
Assigns confidence scores based on:
- **Certain** (0.9): "will", "definitely", "guaranteed"
- **Probable** (0.7): "likely", "probably", "should"
- **Possible** (0.5): "might", "could", "think"

## 🤖 LLM Verification

### How It Works

The LLM verification system analyzes each prediction to determine if it came true:

1. **Context Analysis**: Reviews the prediction text and timeframe
2. **Evidence Evaluation**: Assesses available information (can be enhanced with web search)
3. **Outcome Classification**:
   - **CORRECT**: Prediction clearly came true
   - **INCORRECT**: Prediction was proven wrong  
   - **CANNOT_DETERMINE**: Too early, too vague, or insufficient evidence

### Supported LLM Providers

| Provider | Models | Cost (approx) | Setup |
|----------|--------|---------------|--------|
| **OpenAI** | gpt-4, gpt-3.5-turbo | ~$0.01/prediction | Get API key from [OpenAI](https://platform.openai.com) |
| **Anthropic** | claude-3-sonnet, claude-3-haiku | ~$0.008/prediction | Get API key from [Anthropic](https://console.anthropic.com) |
| **Google** | gemini-pro, gemini-pro-vision | ~$0.005/prediction | Get API key from [Google AI Studio](https://makersuite.google.com) |

### Configuration Options

```bash
# Basic LLM setup
LLM_PROVIDER=openai               # openai, anthropic, or google
LLM_MODEL=gpt-4                   # Model name
OPENAI_API_KEY=your-key-here      # API key

# Advanced settings
LLM_MAX_RETRIES=3                 # Retry failed requests
LLM_DELAY=1.5                     # Seconds between API calls
SKIP_MANUALLY_VERIFIED=true       # Skip already validated predictions

# Optional: Web search for context (requires SerpAPI)
USE_WEB_SEARCH=true
SERPAPI_KEY=your-serpapi-key
```

### Example LLM Analysis

**Input Prediction:**
> "I predict Bitcoin will hit $100k by end of 2024"

**LLM Output:**
```json
{
  "result": "INCORRECT", 
  "confidence": 0.85,
  "reasoning": "Bitcoin reached a peak of ~$73k in 2024 but did not reach $100k by year end. The prediction had a specific price target and timeline that was not met.",
  "key_facts": [
    "Bitcoin peaked at ~$73,737 in March 2024",
    "End of 2024: Bitcoin trading around $42k-45k", 
    "Prediction specified $100k target not achieved"
  ],
  "time_factor": "Sufficient time has passed to evaluate this prediction",
  "evidence_quality": "HIGH"
}
```

## 📊 Using the Streamlit UI

### Browse Predictions Tab
- View all extracted predictions with LLM verification results
- Filter by status, author, or verification result
- Sort by various criteria including LLM confidence
- Mark predictions as correct/incorrect with one click
- View detailed LLM reasoning and key facts

### Analytics Dashboard Tab
- View prediction statistics and accuracy metrics
- Compare LLM vs manual verification results
- Interactive charts and visualizations
- Timeline analysis of prediction frequency
- Author performance analysis with LLM insights

### All Tweets Tab
- Browse complete tweet dataset
- Search functionality
- Paginated view for large datasets

### Settings Tab
- View current configuration
- Export validated predictions to CSV
- Review prediction keywords and patterns

## ⚙️ Configuration Options

Edit your `.env` file to customize:

```bash
# Required
CSV_PATH=path/to/your/tweets.csv
OUTPUT_DIR=output

# Optional
MIN_CONFIDENCE=0.3
USE_ADVANCED_NLP=true
CUSTOM_KEYWORDS=will,predict,expect,custom_keyword
DATE_FORMAT=%Y-%m-%d %H:%M:%S
```

## 🔄 Complete Workflow

1. **Extract**: Run `python main.py` to process your CSV and identify predictions
2. **Verify**: Run `python verify_predictions.py` or use the UI's LLM verification
3. **Browse**: Use the Streamlit UI to explore predictions and LLM analysis
4. **Validate**: Manually review and correct any uncertain cases
5. **Analyze**: View statistics comparing LLM vs manual verification
6. **Export**: Download validated data for further analysis

### Batch Processing Large Datasets

For processing thousands of predictions:

```bash
# Process in smaller batches with delays
python verify_predictions.py --batch-size 20 --delay 2.0

# Use cheaper model for initial screening
python verify_predictions.py --provider openai --model gpt-3.5-turbo

# Skip manually verified predictions
python verify_predictions.py --skip-manual
```

## 🛠️ Advanced Usage

### Custom Prediction Keywords

Add your own keywords to the `.env` file:
```bash
CUSTOM_KEYWORDS=will,predict,expect,my_custom_keyword
```

### Batch Processing

For large datasets, you can run extraction in batches:
```python
from main import TweetPredictionAnalyzer

analyzer = TweetPredictionAnalyzer()
# Process your data
analyzer.run_extraction()
```

### API Integration

The core analyzer can be imported and used programmatically:
```python
from main import TweetPredictionAnalyzer

analyzer = TweetPredictionAnalyzer()
predictions = analyzer.load_predictions()

# Update predictions programmatically
analyzer.update_prediction('tweet_id', validated=True, outcome=True)
```

## 📈 Output Format

### Predictions JSON
```json
[
  {
    "id": "tweet_id",
    "date": "2024-01-15",
    "content": "I predict Bitcoin will hit $100k...",
    "author": "John Crypto",
    "handle": "@johncrypto",
    "url": "https://twitter.com/example/1",
    "validated": false,
    "outcome": null,
    "confidence": 0.9,
    "metrics": {
      "replies": 5,
      "retweets": 12,
      "likes": 45,
      "views": 1200
    }
  }
]
```

### All Tweets JSON
```json
[
  {
    "id": "tweet_id",
    "date": "2024-01-15",
    "content": "Tweet content...",
    "author": "Author Name",
    "handle": "@handle",
    "url": "https://twitter.com/example/1",
    "metrics": { ... }
  }
]
```

## 🧪 Testing

Test with the included sample data:
```bash
# Use sample_tweets.csv created by setup.py
CSV_PATH=sample_tweets.csv python main.py
streamlit run streamlit_app.py
```

## 🐛 Troubleshooting

### Common Issues

**spaCy model not found:**
```bash
python -m spacy download en_core_web_sm
```

**CSV parsing errors:**
- Ensure your CSV has the required columns
- Check date format in your CSV matches expectations
- Verify file encoding (UTF-8 recommended)

**Streamlit UI not loading:**
```bash
pip install --upgrade streamlit
streamlit run streamlit_app.py --server.port 8501
```

**No predictions found:**
- Check if your tweets contain predictive language
- Review and adjust prediction keywords in the code
- Ensure CSV_PATH in .env points to the correct file

## 📝 Requirements

- Python 3.8+
- pandas, streamlit, spacy, plotly (see requirements.txt)
- Optional: spaCy English model for advanced NLP

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use and modify as needed.

## 🙋 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the code comments for implementation details
3. Create an issue if you find bugs or have feature requests

---

**Happy predicting! 🔮**