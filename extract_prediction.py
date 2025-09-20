import json
import os
import re
from datetime import datetime
from dotenv import load_dotenv
import langextract as lx
import textwrap

# Load environment variables
load_dotenv()


def create_prediction_examples():
    """Create few-shot examples for prediction extraction"""
    examples = [
        lx.data.ExampleData(
            text="By 2030, electric vehicles will comprise 50% of all new car sales globally. The infrastructure is rapidly expanding.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="business",
                    extraction_text="electric vehicles",
                    attributes={
                        "location": "global",
                        "prediction": "Electric vehicles will comprise 50% of all new car sales globally by 2030",
                        "justification": "The infrastructure is rapidly expanding",
                    },
                )
            ],
        ),
        lx.data.ExampleData(
            text="💥Nations are reversing the two bucket theory which kept the dollar going. This will change everything.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="other",
                    extraction_text="two bucket theory",
                    attributes={
                        "location": "global",
                        "prediction": "Two bucket theory will reverse",
                        "justification": "Nations are reversing",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="economics",
                    extraction_text="dollar",
                    attributes={
                        "location": "global",
                        "prediction": "Dollar going because of two bucket theory",
                        "justification": "Nations are reversing",
                    },
                ),
            ],
        ),
    ]
    return examples


def create_prediction_prompt():
    """Create the extraction prompt"""
    prompt = textwrap.dedent(
        """
    Extract predictions, claims, or statements about future events from the text.
    If multiple predictions exist in one text, extract each separately.
    
    WHAT TO EXTRACT:
    - Predictions about what will happen in the future, or what happened in past
    - Claims about ongoing changes or trends
    - Statements about expected outcomes or consequences
    
    CLASSIFICATION RULES:
    - Use "politics" for political/economic claims and policy-related statements
    - Use "economics" for market, financial, or economic predictions
    - Use "technology" for tech-related forecasts
    - Use "social" for society and culture related claims
    
    ATTRIBUTES TO DETERMINE:
    - location: Geographic scope (global, country name, region, or "unknown")
    - prediction: The actual prediction or claim
    - justification: Any reasoning or explanation provided in the text
    """
    )
    return prompt


def process_tweets(input_file="tweets.json", output_file="predictions.json"):
    """Process tweets and extract predictions"""

    # Load tweets from JSON file
    with open(input_file, "r", encoding="utf-8") as f:
        tweets = json.load(f)
    print(f"Loaded {len(tweets)} tweets from {input_file}")
    # Create prompt and examples
    prompt = create_prediction_prompt()
    examples = create_prediction_examples()
    extracted_predictions = []
    processed_count = 0
    error_count = 0
    print("Starting prediction extraction...")
    print("-" * 50)
    for i, tweet in enumerate(tweets):
        tweet_text = tweet.get("tweetText", "")
        tweet_id = tweet.get("id", "")
        created_at = tweet.get("createdAt", "")

        try:
            print(
                f"Processing tweet {i+1}/{len(tweets)} (ID: {tweet_id}): {tweet_text[:30]}..."
            )
            # Extract predictions using LangExtract
            result = lx.extract(
                text_or_documents=tweet_text,
                prompt_description=prompt,
                examples=examples,
                model_id="gemini-2.0-flash-lite",
            )
            # print(result)
            # Normalize result to list of documents
            documents = []
            if hasattr(result, "documents"):
                documents = result.documents
            elif isinstance(result, lx.data.AnnotatedDocument):
                documents = [result]
            elif isinstance(result, list):
                documents = result
            if documents:
                for document in documents:
                    if hasattr(document, "extractions") and document.extractions:
                        for extraction in document.extractions:
                            prediction = {
                                "extraction_class": extraction.extraction_class,
                                "extraction_text": extraction.extraction_text,
                                "charInterval": (
                                    {
                                        "start": getattr(
                                            extraction.char_interval, "start_pos", None
                                        ),
                                        "end": getattr(
                                            extraction.char_interval, "end_pos", None
                                        ),
                                    }
                                    if hasattr(extraction, "char_interval")
                                    and extraction.char_interval
                                    else None
                                ),
                                "alignmentStatus": (
                                    extraction.alignment_status.name
                                    if extraction.alignment_status
                                    else None
                                ),
                                "extractionIndex": getattr(
                                    extraction, "extraction_index", None
                                ),
                                "location": extraction.attributes.get("location", ""),
                                "prediction": extraction.attributes.get(
                                    "prediction", extraction.extraction_text
                                ),
                                "justification": extraction.attributes.get(
                                    "justification", ""
                                ),
                                "original_tweet": {
                                    "id": tweet_id,
                                    "text": tweet_text,
                                    "author": tweet.get("tweetAuthor", ""),
                                    "handle": tweet.get("handle", ""),
                                    "created_at": created_at,
                                    "url": tweet.get("tweetURL", ""),
                                    "likes": tweet.get("likeCount", ""),
                                    "retweets": tweet.get("retweetCount", ""),
                                    "views": tweet.get("views", ""),
                                },
                            }
                            extracted_predictions.append(prediction)
                            print(
                                f"  ✓ Extracted: [{extraction.extraction_class}] '{extraction.extraction_text}'"
                            )
                    else:
                        print(f"  - No extractions found in document")
            else:
                print(f"  - No results returned")

            processed_count += 1
        except Exception as e:
            error_count += 1
            print(f"  ❌ Error processing tweet {tweet_id}: {str(e)}")
            continue
    print("-" * 50)

    # Save results
    try:
        # Serialize safely (convert non-serializable fields)
        def safe_json(obj):
            if hasattr(obj, "__dict__"):
                return str(obj)
            if isinstance(obj, lx.data.CharInterval):
                return {"start": obj.start_pos, "end": obj.end_pos}
            if isinstance(obj, lx.data.AlignmentStatus):
                return obj.value
            return str(obj)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                extracted_predictions,
                f,
                indent=2,
                ensure_ascii=False,
                default=safe_json,
            )
        print(f"\n=== EXTRACTION COMPLETE ===")
        print(f"Total tweets processed: {processed_count}")
        print(f"Errors encountered: {error_count}")
        print(f"Predictions extracted: {len(extracted_predictions)}")
        print(f"Results saved to: {output_file}")
        # Print summary statistics
        if extracted_predictions:
            classes = {}
            locations = {}
            for pred in extracted_predictions:
                extraction_class = pred.get("extraction_class", "unknown")
                location = pred.get("location", "unknown")
                classes[extraction_class] = classes.get(extraction_class, 0) + 1
                locations[location] = locations.get(location, 0) + 1
            print(f"\n=== SUMMARY STATISTICS ===")
            print(f"Extraction classes: {classes}")
            print(f"Locations: {locations}")
            print("-" * 50)
        else:
            print("\n⚠️  No predictions were extracted. Check your examples and prompt.")
    except Exception as e:
        print(f"❌ Error saving results: {str(e)}")


def create_visualization(
    predictions_file="predictions.json", output_html="predictions_viz.html"
):
    """Create visualization of extracted predictions (optional)"""
    try:
        # Convert predictions to JSONL format for LangExtract visualization
        with open(predictions_file, "r", encoding="utf-8") as f:
            predictions = json.load(f)
        if not predictions:
            print("No predictions found to visualize.")
            return
        # Create annotated documents for visualization
        documents = []
        for pred in predictions:
            tweet_text = pred["original_tweet"]["text"]
            extraction_text = pred["extraction_text"]
            # Convert charInterval to CharInterval object
            char_start = pred.get("charInterval", {}).get("start", 0)
            char_end = pred.get("charInterval", {}).get("end", len(extraction_text))
            char_interval = lx.data.CharInterval(char_start, char_end)
            # Convert alignmentStatus string to enum
            alignment_status_str = pred.get("alignmentStatus", "MATCH_EXACT")
            alignment_status = getattr(lx.data.AlignmentStatus, alignment_status_str)
            # Create extraction
            extraction = lx.data.Extraction(
                extraction_class=pred["extraction_class"],
                extraction_text=extraction_text,
                char_interval=char_interval,
                alignment_status=alignment_status,
                extraction_index=pred.get("extractionIndex", 0),
                attributes=pred
            )
            # Create document (metadata is not supported in AnnotatedDocument)
            doc = lx.data.AnnotatedDocument(
                text=tweet_text,
                extractions=[extraction],
            )
            documents.append(doc)

        # Save as JSONL in same folder as predictions_file
        jsonl_file = os.path.splitext(predictions_file)[0] + ".jsonl"
        lx.io.save_annotated_documents(documents, output_name=jsonl_file)
        # Generate HTML visualization
        html_content = lx.visualize("test_output/" + jsonl_file)
        with open(output_html, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Visualization created: {output_html}")
    except Exception as e:
        print(f"Error creating visualization: {str(e)}")


if __name__ == "__main__":
    print("🚀 Starting Tweet Prediction Extraction")
    print("=" * 50)
    # Process tweets
    input_file = "tweets.json"
    output_file = "predictions.json"
    # Extract predictions & create visualization
    process_tweets(input_file, output_file)
    if os.path.exists(output_file):
        create_visualization(output_file)
    print("\n✅ Process completed!")
