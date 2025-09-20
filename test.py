import os
import re
import json
from datetime import datetime
from dotenv import load_dotenv
import textwrap
import langextract as lx

load_dotenv()

# 1. Define a concise prompt
prompt = textwrap.dedent(
    """
    Extract predictions about future events from the text.

    A prediction is a statement about what will happen, might happen, or is expected to happen in the future.

    Rules:
    - Only extract actual predictions, not opinions about past/present events
    - Use exact text from the source for extraction_text
    - Set yearMade to the current year (2025) unless specified otherwise
    - Set yearExpected to the year when the predicted event should occur
    - Set measurable to True if the prediction can be objectively verified
    - Set certainty to True if the prediction is stated with confidence, False if speculative
    - Set confidence score (0.0-1.0) based on how likely this is to be a genuine prediction
    - Categorize domain: technology, politics, economics, social, war, sports, climate, etc.
    - Include any reasoning/justification provided for the prediction
    - If no predictions are found, return empty extractions list
    """
)

# 2. Provide a high-quality example to guide the model
examples = [
    lx.data.ExampleData(
        text=(
            "Nations are reversing the two bucket theory which kept the dollar going. This will change everything."
        ),
        extractions=[
            lx.data.Extraction(
                extraction_class="economics",
                extraction_text="reversing the two bucket theory",
                attributes={
                    "location": "global",
                    "prediction": "two bucket theory kept dollar going",
                },
            )
        ],
    ),
    lx.data.ExampleData(
        text=(
            "I think the stock market might crash next year due to inflation concerns, but I'm not sure."
        ),
        extractions=[
            lx.data.Extraction(
                extraction_class="economics",
                extraction_text="stock market might crash",
                attributes={
                    "location": "india",
                    "prediction": "stock market might crash",
                    "justification": "crash due to inflation",
                },
            )
        ],
    ),
    lx.data.ExampleData(
        text="By 2030, electric vehicles will comprise 50% of all new car sales globally. The infrastructure is rapidly expanding.",
        extractions=[
            lx.data.Extraction(
                extraction_class="commerce",
                extraction_text="electric vehicles will comprise 50% of all new car sales globally",
                attributes={
                    "location": "global",
                    "prediction": "electric vehicles will comprise 50% of all new car sales globally",
                    "justification": "The infrastructure is rapidly expanding",
                    "yearExpected": "2030",
                    "measurable": True,
                },
            )
        ],
    ),
    lx.data.ExampleData(
        text="💥Nations are reversing the two bucket theory which kept the dollar going. This will change everything.",
        extractions=[
            lx.data.Extraction(
                extraction_class="economics",
                extraction_text="Nations reversing two bucket theory will change everything",
                attributes={
                    "location": "global",
                    "prediction": "Dollar will go down",
                    "justification": "Two bucket theory kept dollar going, which is being reversed",
                    "measurable": False,
                },
            )
        ],
    ),
]

# 3. Run the extraction on your input text
input_text = "Technology cannot eat itself.\n\nYou need a real human to buy products and services to make profits.\n\nIn a scenario where companies will fail to employ masses citing tech automation, the masses will NOT BUY their products and prefer to barter with neighbor or empower some nearby entrepreneur."
result = lx.extract(
    text_or_documents=input_text,
    prompt_description=prompt,
    examples=examples,
    model_id="gemini-2.5-pro",
)
print(result)
