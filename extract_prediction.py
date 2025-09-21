import os
import json
from dotenv import load_dotenv
from collections import defaultdict
import textwrap
import langextract as lx

# Load environment variables
load_dotenv()

input_file = "tweets.json"
output_file = "predictions.json"
output_html = "predictions_viz.html"


def create_prediction_examples():
    """Create few-shot examples for prediction extraction"""
    examples = [
        lx.data.ExampleData(
            text="The actual bots are Pakistani. The Chinese and Russians don't care this much about America. They outsource to Pakistanis and Bangladeshis who America supports foolishly thinking using them they can control India forgetting that for 1000 years they tried to control 🇮🇳 and failed.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="economics",
                    extraction_text="outsource to Pakistanis and Bangladeshis",
                    attributes={
                        "location": "Global",
                        "prediction": "America funds Pakistanis and Bangladeshis bots.",
                        "justification": "To control India.",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="politics",
                    extraction_text="control India",
                    attributes={
                        "location": "Global",
                        "prediction": "America is trying to control India using Pakistanis and Bangladeshis.",
                        "justification": "They tried for 1000 years, so foolishly still trying.",
                    },
                ),
            ],
        ),
        lx.data.ExampleData(
            text="Yesterday's gruesome beheading of Indian American motel owner is so sick and stomach churning to see.\n\nBut not at all that shocking, given we all knew what was coming and is only going to increase - the hate crimes against Indian ethnic people in the US.\n\nSuch violence is only going to increase because influential Indian Americans sit quietly not speaking out when one of their people is attacked like say Jews, Muslims, Blacks, and east Asians do.\n\nAll the SV Tech Bros and Indian American millionaires are quiet on this murder of a fellow entrepreneur, but are speaking out against Charlie Kirk's gruesome shooting as that's the mainstream America's topic.\n\nMr. Chandra was killed just because he asked someone to translate what the murderer was saying about using a washing machine instead of directly listening to him it seems. \n\nMy heart goes out to Chandra ji's family who witnessed it. Can't imagine what they are going through right now.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="politics",
                    extraction_text="the hate crimes against Indian",
                    attributes={
                        "location": "america",
                        "prediction": "The hate crimes against Indian ethnic people in the US is going to increase",
                        "justification": "Influential Indian Americans sit quietly not speaking out when one of their people is attacked",
                    },
                )
            ],
        ),
        lx.data.ExampleData(
            text="The US is soon going to put Europe into a war with Russia it doesn't need to fight. By March of next year, there's great chance of a EU-Russia conflict without US involvement as part of NATO.\n\nThey tried using Ukraine as a proxy to pull Russia into a war and weaken it. Russia did get very occupied in the war but doesn't seem weakened. \n\nThey tried stopping the war and bringing Russia into western fold to focus against China. Russia is not taking any deals forced on it with arrogance.\n\nSo now they want to make all of Europe their proxy to fight Russia. They even have a time limit: March 2026. \n\nThey get three birds in one stone of this conflict:\n\n1) Russia severely contained fighting big European powers directly. \n2) Europe totally wasted and a dependent vassal of the US. \n3) The economic mess this war creates weakening China badly, creating perfect conditions for a revolution to overthrow the CCP. \n\nNow tell me, is my analysis far fetched conspiracy or a prediction that will come true?",
            extractions=[
                lx.data.Extraction(
                    extraction_class="war",
                    extraction_text="Europe into a war with Russia",
                    attributes={
                        "location": "europe",
                        "prediction": "The US is soon going to put Europe into a war with Russia",
                        "justification": "Russia severely contained fighting directly. Europe totally wasted. The economic mess this war creates weakening China badly.",
                    },
                ),
                lx.data.Extraction(
                    extraction_class="war",
                    extraction_text="conditions for a revolution to overthrow the CCP",
                    attributes={
                        "location": "china",
                        "prediction": "EU-Russia conflict without US involvement will weaken china creating conditions to overthrow CCP.",
                        "justification": "The economic mess this war creates weakens China badly.",
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
        You are an information extraction system.
        Given a tweet (or a short text post), extract all significant author claims, ideas, predictions, or analytic points.
        The author may use logical reasoning, intuition, conspiracy theories, cashflow or astrology-based reasoning, or reference past events to make their points.
        
        INSTRUCTIONS:
        - List every main claim, idea, or prediction the author expresses—including predictions, causal analysis, statements based on intuition, conspiracy theories, or claims about past, present, or future.
        - For each point, extract:
            - Domain/class (e.g. politics, economics, war, astrology, technology, history, etc.)
            - The main claim/point/idea/prediction as a clear summary.
            - The justification or reasoning the author gives (if any)—why are they making this claim?
            - Location/Entity (if multiple then comma-separated, e.g. USA, India, Global, China, Europe, etc.)
        """
    )
    return prompt


def process_tweets(input_file=input_file, output_file=output_file):
    """Process tweets and extract predictions"""

    # Load tweets from JSON file
    with open(input_file, "r", encoding="utf-8") as f:
        tweets = json.load(f)
    print(f"Loaded {len(tweets)} tweets from {input_file}")
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
        try:
            print(f"Processing tweet {i+1}/{len(tweets)} (ID: {tweet_id})")
            result = lx.extract(
                text_or_documents=tweet_text,
                prompt_description=prompt,
                examples=examples,
                model_id="gemini-1.5-flash",  # starcoder2:3b, gpt-4o, gemini-2.0-flash-lite
                # model_url="http://localhost:11434",
                # fence_output=True,
                # use_schema_constraints=False,
            )
            # Normalize result to list of documents
            documents = []
            if isinstance(result, lx.data.AnnotatedDocument):
                documents = [result]
            elif isinstance(result, list):
                documents = result
            if documents:
                for document in documents:
                    if hasattr(document, "extractions"):
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
                                "location": extraction.attributes.get("location", ""),
                                "prediction": extraction.attributes.get(
                                    "prediction", ""
                                ),
                                "justification": extraction.attributes.get(
                                    "justification", ""
                                ),
                                "original_tweet": {
                                    "id": tweet_id,
                                    "text": tweet_text,
                                    "author": tweet.get("tweetAuthor", ""),
                                    "handle": tweet.get("handle", ""),
                                    "created_at": tweet.get("createdAt", ""),
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


def create_visualization(predictions_file=output_file, output_html=output_html):
    """
    Create a LangExtract HTML visualization for all predictions in predictions_file.
    Handles multiple extractions across multiple tweets/documents.
    """
    try:
        # Load predictions
        with open(predictions_file, "r", encoding="utf-8") as f:
            predictions = json.load(f)
        if not predictions:
            print("No predictions found to visualize.")
            return

        # Group predictions by tweet ID
        tweet_groups = defaultdict(list)
        for pred in predictions:
            tweet_id = pred.get("original_tweet", {}).get(
                "id", f"doc_{pred.get('document_id')}"
            )
            tweet_groups[tweet_id].append(pred)

        documents = []
        for tweet_id, preds in tweet_groups.items():
            text = preds[0]["original_tweet"].get("text", "")
            if not text:
                continue

            extractions = []
            for idx, pred in enumerate(preds):
                extraction_text = pred.get("extraction_text", "")
                char_start = pred.get("charInterval", {}).get("start", 0)
                char_end = pred.get("charInterval", {}).get("end", len(extraction_text))
                char_interval = lx.data.CharInterval(char_start, char_end)
                alignment_status_str = pred.get("alignmentStatus") or "MATCH_EXACT"
                alignment_status = getattr(
                    lx.data.AlignmentStatus,
                    alignment_status_str.upper(),
                    lx.data.AlignmentStatus.MATCH_EXACT,
                )
                extraction_attrs = {
                    "location": pred.get("location", ""),
                    "prediction": pred.get("prediction", ""),
                    "justification": pred.get("justification", ""),
                }
                extraction = lx.data.Extraction(
                    extraction_class=pred.get("extraction_class", "Other").capitalize(),
                    extraction_text=extraction_text,
                    char_interval=char_interval,
                    alignment_status=alignment_status,
                    extraction_index=idx,
                    attributes=extraction_attrs,
                )
                extractions.append(extraction)
            doc = lx.data.AnnotatedDocument(text=text, extractions=extractions)
            documents.append(doc)
        if not documents:
            print("No valid documents to visualize.")
            return

        # Save all documents to JSONL
        jsonl_file = os.path.splitext(predictions_file)[0] + ".jsonl"
        lx.io.save_annotated_documents(documents, output_name=jsonl_file)
        print(f"Saved JSONL for visualization: {jsonl_file}")
        # Generate HTML visualization
        html_content = lx.visualize("test_output/" + jsonl_file)
        with open(output_html, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"✅ Visualization created successfully: {output_html}")
        print(f"📄 JSONL source saved: {jsonl_file}")
    except Exception as e:
        print(f"❌ Error creating visualization: {str(e)}")


def extract_predictions(input_file=input_file, output_file=output_file):
    """Process tweets and return extracted predictions as a list"""
    process_tweets(input_file, output_file)
    # create_visualization()
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            predictions = json.load(f)
        return predictions
    return []


if __name__ == "__main__":
    extracted = extract_predictions()
    print(f"Extracted {len(extracted)} predictions")
