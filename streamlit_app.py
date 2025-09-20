import os
import json
import csv
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

# Load environment variables
load_dotenv()
input_folder = os.getenv("INPUT_FOLDER", "data")


# Function to convert selected CSV to JSON
def convert_csv_to_json(csv_file):
    input_path = os.path.join(input_folder, csv_file)
    output_path = "tweets.json"

    with open(input_path, mode="r", encoding="utf-8-sig") as csv_file_obj:
        csv_reader = csv.DictReader(csv_file_obj)
        data = [row for row in csv_reader]

    with open(output_path, mode="w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

    return output_path


# Streamlit UI
st.sidebar.header("📂 CSV to JSON Converter")
csv_files = [f for f in os.listdir(input_folder) if f.endswith(".csv")]

if csv_files:
    selected_file = st.sidebar.selectbox("Select CSV File", csv_files)

    if st.sidebar.button("Convert to JSON"):
        try:
            output_file = convert_csv_to_json(selected_file)
            st.success(
                f"✅ Successfully converted '{selected_file}' to '{output_file}'"
            )
        except Exception as e:
            st.error(f"❌ Conversion failed: {e}")
else:
    st.sidebar.warning(f"No CSV files found in '{input_folder}'")


# Load predictions and tweets
@st.cache_data
def load_data(predictions_file="predictions.json", tweets_file="tweets.json"):
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
    st.set_page_config(page_title="Tweet Prediction Analyzer", layout="wide")
    st.title("🔮 Tweet Prediction Analyzer")

    predictions, tweets = load_data()

    if not predictions:
        st.warning("No predictions available. Ensure 'predictions.json' exists.")
        return

    stats = calculate_stats(predictions)

    # Sidebar stats
    with st.sidebar:
        st.header("📊 Summary Stats")
        st.metric("Total Predictions", stats["total"])
        st.metric("Validated", stats["validated"])
        st.metric("Correct", stats["correct"])
        st.metric("Accuracy", f"{stats['accuracy']:.1f}%")

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
            # Validation status pie chart
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
            # Accuracy chart
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


# Give option to select file from data folder in left navbar
# Inprove extraction
# Get MIT licence
# Handle media also
# Add subcription model to see all predictions
