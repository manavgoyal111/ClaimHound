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

# 2. Provide a high-quality example to guide the model
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

# 3. Run the extraction on your input text
input_text = "The actual bots are Pakistani. The Chinese and Russians don't care this much about America. They outsource to Pakistanis and Bangladeshis who America supports foolishly thinking using them they can control India forgetting that for 1000 years they tried to control 🇮🇳 and failed."

result = lx.extract(
    text_or_documents=input_text,
    prompt_description=prompt,
    examples=examples,
    model_id="gemini-1.5-flash",
)
print(result)
