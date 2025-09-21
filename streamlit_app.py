import os
import json
import pandas as pd
from dotenv import load_dotenv
from collections import Counter
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import plotly.graph_objects as go
from convert_to_json import convert_csv_to_json
from extract_prediction import extract_predictions

# Load environment variables
load_dotenv()

viz_file = "display.html"
input_file = "tweets.json"
output_file = "predictions.json"


# Load predictions and tweets
@st.cache_data
def load_data(predictions_file=output_file, tweets_file=input_file):
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
    st.markdown(
        """
        <style>
            header[data-testid="stHeader"] {
                background: white !important;
                color: black !important;
            }
            header[data-testid="stHeader"]::before {
                content: none;
            }
            header[data-testid="stHeader"] * {
                color: black !important;
            }
        
            .stApp {
                background-color: white !important;
                color: black !important;
            }
            section[data-testid="stSidebar"] {
                background-color: white !important;
                color: black !important;
            }
            
            button[kind="primary"], button[kind="secondary"] {
                background-color: #1E88E5 !important;
                color: white !important;
                border-radius: 8px !important;
                border: none !important;
            }
            button[kind="primary"]:hover, button[kind="secondary"]:hover {
                background-color: #1565C0 !important;
                color: white !important;
            }

            p {
                color: black;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    predictions, tweets = load_data()
    df = pd.json_normalize(predictions, sep="_")
    df["original_tweet_created_at"] = pd.to_datetime(df["original_tweet_created_at"])
    # Sidebar controls
    with st.sidebar:
        st.header("ClaimHound")
        # CSV to JSON button
        st.markdown("#### 1. Convert CSV to JSON")
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
        st.markdown("#### 2. Extract Predictions")
        if st.button("Start Extraction"):
            if not tweets:
                st.warning("No tweets available. Convert CSV first.")
            else:
                with st.spinner("Extracting predictions..."):
                    try:
                        # Instead of looping manually, call your function once
                        predictions = extract_predictions(input_file, output_file)
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
        st.warning("No predictions available.")
        return
    tab1, tab2, tab3 = st.tabs(["🔍 Predictions", "📈 Analytics", "📊 All Tweets"])
    with tab1:
        # Filter by Extraction Class
        classes = ["All"] + sorted(df["extraction_class"].dropna().unique().tolist())
        selected_class = st.selectbox("Filter by Extraction Class:", classes)
        # Filter by Location
        locations = ["All"] + sorted(df["location"].dropna().unique().tolist())
        selected_location = st.selectbox("Filter by Location:", locations)
        # Filter by Author
        authors = ["All"] + sorted(
            df["original_tweet_author"].dropna().unique().tolist()
        )
        selected_author = st.selectbox("Filter by Author:", authors)

        # Apply filters
        filtered_df = df.copy()
        if selected_class != "All":
            filtered_df = filtered_df[filtered_df["extraction_class"] == selected_class]
        if selected_location != "All":
            filtered_df = filtered_df[filtered_df["location"] == selected_location]
        if selected_author != "All":
            filtered_df = filtered_df[
                filtered_df["original_tweet_author"] == selected_author
            ]

        # Display predictions
        for idx, (_, row) in enumerate(filtered_df.iterrows(), start=1):
            readable_date = row["original_tweet_created_at"].strftime("%B %d, %Y %H:%M")
            st.markdown(
                f"{idx}. **{readable_date}** - [View Tweet]({row['original_tweet_url']})"
            )
            st.markdown(f"**Prediction:** {row['prediction']}")
            st.markdown(f"**Justification:** {row['justification']}")
            st.markdown("---")

    with tab2:
        # Display raw data
        st.subheader("Raw Data")
        st.dataframe(df)

        # Class distribution chart
        st.subheader("Extraction Class Distribution")
        class_counts = df["extraction_class"].value_counts()
        fig_class = px.pie(
            names=class_counts.index,
            values=class_counts.values,
            title="Distribution of Extraction Classes",
        )
        st.plotly_chart(fig_class, use_container_width=True)

        # Likes, Retweets, Views by Class
        st.subheader("Engagement Metrics by Extraction Class")
        metrics = (
            df.groupby("extraction_class")
            .agg(
                total_likes=pd.NamedAgg(
                    column="original_tweet_likes", aggfunc=lambda x: x.astype(int).sum()
                ),
                total_retweets=pd.NamedAgg(
                    column="original_tweet_retweets",
                    aggfunc=lambda x: x.astype(int).sum(),
                ),
                total_views=pd.NamedAgg(
                    column="original_tweet_views", aggfunc=lambda x: x.astype(int).sum()
                ),
            )
            .reset_index()
        )
        st.dataframe(metrics)

        # Bar chart for engagement metrics
        fig_metrics = px.bar(
            metrics,
            x="extraction_class",
            y=["total_likes", "total_retweets", "total_views"],
            title="Engagement Metrics by Extraction Class",
            barmode="group",
        )
        st.plotly_chart(fig_metrics, use_container_width=True)

    with tab3:
        st.subheader("Tweet Details with Predictions")
        for idx, (_, row) in enumerate(filtered_df.iterrows(), start=1):
            st.markdown(f"{idx}. [Original Tweet Link]({row['original_tweet_url']})")
            st.markdown(f"**Class:** {row['extraction_class']}")
            st.markdown(f"**Original Text:** {row['extraction_text']}")
            st.markdown(f"**Prediction:** {row['prediction']}")
            st.markdown(f"**Justification:** {row['justification']}")
            st.markdown("---")


if __name__ == "__main__":
    main()


# Improve Extraction
# Add Automatic verification
# Add already extracted tweets from various handles to select & see
# Users can vote on them (Authentication)
# Add contact & buyMeCoffee link
# Add subcription model, Live tweet analysis, Handle media in tweets, Get MIT Licence
