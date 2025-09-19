import os
import csv
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Input folder path from .env file
input_folder = os.getenv("INPUT_FOLDER", "data")

# List all CSV files in the input folder
csv_files = [f for f in os.listdir(input_folder) if f.endswith(".csv")]

if not csv_files:
    print("No CSV files found in input folder.")
    exit()

print("Available CSV files:")
for idx, file_name in enumerate(csv_files, start=1):
    print(f"{idx}. {file_name}")

# Ask user to choose a file
choice = input("Enter the number of the file you want to convert: ")
try:
    choice_idx = int(choice) - 1
    if choice_idx < 0 or choice_idx >= len(csv_files):
        raise ValueError("Invalid choice")
except ValueError:
    print("Invalid input. Exiting.")
    exit()

selected_file = csv_files[choice_idx]
input_path = os.path.join(input_folder, selected_file)
output_path = "tweets.json"
# Read CSV and convert to JSON
with open(input_path, mode="r", encoding="utf-8-sig") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    data = [row for row in csv_reader]

# Write JSON output
with open(output_path, mode="w", encoding="utf-8") as json_file:
    json.dump(data, json_file, indent=4, ensure_ascii=False)
print(f"Converted {selected_file} -> {output_path}")
