import csv
import os


def merge_data_metadata(raw_data_folder, metadata_folder):
    for root, _, files in os.walk(raw_data_folder):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    file_name = os.path.splitext(file)[0]

                    with open(file_path, mode='r', encoding='utf-8') as input_file:
                        reader = csv.reader(input_file)
                        rows = list(reader)