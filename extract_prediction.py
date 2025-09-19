import os
import json
from dotenv import load_dotenv
from langextract import schema, Example, extract

# Load environment variables
load_dotenv()

# Input JSON (converted tweet.json) and output file paths
input_path = os.getenv("TWEET_JSON", "tweet.json")
output_path = os.getenv("PREDICTIONS_JSON", "predictions.json")

# Define schema for predictions
prediction_schema = schema.Schema(
    name="PredictionSchema",
    description="Schema to capture predictions made in tweets",
    fields=[
        ("yearMade", "string", "The year the prediction was made"),
        ("yearExpected", "string", "The year the event is expected to happen"),
        ("measurable", "boolean", "Whether the prediction is measurable or not"),
        ("prediction", "string", "The content of the prediction"),
        ("domain", "string", "The domain or topic of the prediction (e.g., technology, politics)"),
        ("location", "string", "The location or context where the prediction applies"),
        ("justification", "string", "Any reasoning or justification provided for the prediction"),
        ("certainty", "boolean", "The certainty expressed in the prediction (strong vs speculative)"),
    ],
)

# Few-shot examples to guide extraction
examples = [
    Example(
        input="@archieposts Yes unknown gunmen stopped 100 mini pahalgams. You seem to be totally dumb",
        output={
            "yearMade": "2025",
            "yearExpected": "2025",
            "prediction": "Unknown gunmen stopped 100 mini pahalgams type attacks.",
            "measurable": False,
            "domain": "social",
            "location": "Pahalgam",
            "justification": None,
            "certainty": True,
        },
    ),
    Example(
        input="💥Essentially what was hit in operation sindoor? It wasn't pakistan. It was the US which was hit by Bharat. You have to understand that at this point all nations are reversing the two bucket theory which kept the dollar going.",
        output={
            "yearMade": "2025",
            "yearExpected": "2025",
            "prediction": "India targeted US in operation sindoor.",
            "measurable": False,
            "domain": "war",
            "location": "global",
            "justification": "All nations are reversing two bucket theory.",
            "certainty": True,
        },
    ),
]

# Read tweets
with open(input_path, "r", encoding="utf-8") as f:
    tweets = json.load(f)

# Extract predictions
tweet_predictions = []
for tweet in tweets:
    tweet_text = tweet.get("tweetText", "")
    if not tweet_text.strip():
        continue
    prediction = extract(
        schema=prediction_schema,
        input=tweet_text,
        examples=examples
    )
    if prediction:
        tweet_predictions.append({
            "tweetURL": tweet.get("tweetURL"),
            "tweetText": tweet_text,
            "extractedPrediction": prediction
        })

# Save predictions
with open(output_path, "w", encoding="utf-8") as out_file:
    json.dump(tweet_predictions, out_file, indent=4, ensure_ascii=False)
print(f"Extracted {len(tweet_predictions)} predictions and saved to {output_path}")