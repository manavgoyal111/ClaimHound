import os
import csv
import json


def convert_csv_to_json(csv_file):
    input_path = os.path.join(csv_file)
    output_path = "tweets.json"

    with open(input_path, mode="r", encoding="utf-8-sig") as csv_file_obj:
        csv_reader = csv.DictReader(csv_file_obj)
        data = [row for row in csv_reader]

    with open(output_path, mode="w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

    return output_path
