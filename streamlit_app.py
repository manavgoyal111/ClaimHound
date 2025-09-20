import os
import csv
import json
import subprocess
import pandas as pd
from dotenv import load_dotenv
from collections import Counter
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from convert_to_json import convert_csv_to_json
from extract_prediction import extract_predictions

# Load environment variables
load_dotenv()


# Load predictions and tweets
@st.cache_data
def load_data(predictions_file="predictions.json", tweets_file="tweets.json"):
    st.cache_data.clear()
    if os.path.exists(predictions_file):
        with open(predictions_file, "r", encoding="utf-8") as f:
            predictions = json.load(f)
    else:
        predictions = []

    if os.path.exists(tweets_file):
        with open(tweets_file, "r", encoding="utf-8") as f:
            tweets = json.load(f)
    else:
        tweets = []

    return predictions, tweets


def calculate_stats(predictions):
    total = len(predictions)
    validated = len([p for p in predictions if p.get("validated", False)])
    correct = len(
        [p for p in predictions if p.get("validated") and p.get("outcome") is True]
    )
    incorrect = len(
        [p for p in predictions if p.get("validated") and p.get("outcome") is False]
    )
    accuracy = (correct / validated * 100) if validated > 0 else 0
    return {
        "total": total,
        "validated": validated,
        "correct": correct,
        "incorrect": incorrect,
        "accuracy": accuracy,
    }


def main():
    st.set_page_config(page_title="Claim Hound", page_icon="✨", layout="wide")
    st.title("🔮 Tweet Prediction Analyzer")

    predictions, tweets = load_data()

    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Actions")

        # CSV to JSON conversion
        st.markdown("### Convert CSV to JSON")
        input_folder = os.getenv("INPUT_FOLDER", "data")
        if os.path.exists(input_folder):
            csv_files = [f for f in os.listdir(input_folder) if f.endswith(".csv")]
            selected_csv = st.selectbox("Select CSV file", csv_files)

            if st.button("Convert to JSON"):
                try:
                    output_path = convert_csv_to_json(
                        os.path.join(input_folder, selected_csv)
                    )
                    st.success(f"CSV converted successfully -> {output_path}")
                except Exception as e:
                    st.error(f"Conversion failed: {e}")
        else:
            st.warning(f"Input folder '{input_folder}' does not exist")

        # Extraction button
        st.markdown("### Extract Predictions")
        if st.button("Start Extraction"):
            if not tweets:
                st.warning("No tweets available. Convert CSV first.")
            else:
                with st.spinner("Extracting predictions..."):
                    try:
                        # Instead of looping manually, call your function once
                        predictions = extract_predictions(
                            input_file="tweets.json", output_file="predictions.json"
                        )
                        # Show progress info by displaying first few extracted predictions
                        if predictions:
                            st.success(
                                f"Extraction completed! {len(predictions)} predictions extracted."
                            )
                        else:
                            st.warning("No predictions were extracted.")
                    except Exception as e:
                        st.error(f"Extraction failed: {e}")

    # Display stats and tabs
    if not predictions:
        st.warning("No predictions available. Ensure 'predictions.json' exists.")
        return

    stats = calculate_stats(predictions)

    tab1, tab2 = st.tabs(["🔍 Browse Predictions", "📈 Analytics"])

    with tab1:
        st.header("Prediction Browser")
        for pred in predictions:
            with st.expander(
                f"{pred.get('original_tweet', {}).get('author', 'Unknown')} - {pred.get('original_tweet', {}).get('created_at', '')}"
            ):
                st.markdown(f"**Prediction:** {pred.get('prediction')}  ")
                st.markdown(
                    f"**Tweet:** {pred.get('original_tweet', {}).get('text')}  "
                )
                st.markdown(f"**Location:** {pred.get('location')}  ")
                st.markdown(f"**Justification:** {pred.get('justification')}  ")
                st.markdown(f"**Extraction Class:** {pred.get('extraction_class')}  ")
                st.markdown(f"**Certainty:** {pred.get('certainty', False)}  ")
                st.markdown(
                    f"[View Tweet]({pred.get('original_tweet', {}).get('url')})"
                )

    with tab2:
        st.header("Analytics")
        col1, col2 = st.columns(2)

        with col1:
            fig_pie = go.Figure(
                data=[
                    go.Pie(
                        labels=["Validated", "Unvalidated"],
                        values=[
                            stats["validated"],
                            stats["total"] - stats["validated"],
                        ],
                        hole=0.3,
                    )
                ]
            )
            fig_pie.update_layout(title="Validation Status")
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            if stats["validated"] > 0:
                fig_acc = go.Figure(
                    data=[
                        go.Pie(
                            labels=["Correct", "Incorrect"],
                            values=[stats["correct"], stats["incorrect"]],
                            hole=0.3,
                            marker_colors=["#00CC96", "#EF553B"],
                        )
                    ]
                )
                fig_acc.update_layout(title="Prediction Accuracy")
                st.plotly_chart(fig_acc, use_container_width=True)

        # Predictions over time
        dates = [
            pred.get("original_tweet", {}).get("created_at", "") for pred in predictions
        ]
        date_counts = Counter(dates)
        df_time = pd.DataFrame(list(date_counts.items()), columns=["Date", "Count"])
        df_time["Date"] = pd.to_datetime(df_time["Date"])
        df_time = df_time.sort_values("Date")
        fig_time = px.line(df_time, x="Date", y="Count", title="Predictions Over Time")
        st.plotly_chart(fig_time, use_container_width=True)


if __name__ == "__main__":
    main()


# Improve Extraction & UI
# Get MIT licence
# Handle media also
# Add subcription model to see all predictions otherwise only top 100
