import os
import csv

# Paths to the data and metadata directories
data_path = "app/indicators_data/eredes/eredes_data/"
metadata_file_path = "app/indicators_data/eredes/eredes_metadata/metadata.csv"
merged_files = "app/indicators_data/eredes/temp_eredes_merged/"

# Lista de archivos a excluir
excluded_files = [
    "civil-parishes-portugal.csv",
    "districts-portugal.csv",
    "municipalities-portugal.csv"
]

def load_metadata(metadata_file_path):
    metadata_dict = {}
    with open(metadata_file_path, "r", encoding='utf-8') as metadata_file:
        reader = csv.reader(metadata_file, delimiter=',')
        metadata_headers = next(reader)  # Skip the header row
        for row in reader:
            src_code = row[2]
            metadata_dict[src_code] = row
    return metadata_headers, metadata_dict

def combine_data_and_metadata(data_path, metadata_headers, metadata_dict):
    for filename in os.listdir(data_path):
        if filename.endswith(".csv") and filename not in excluded_files:
            src_code = filename.replace('.csv', '')
            if src_code in metadata_dict:
                metadata_row = metadata_dict[src_code]
                file_path = os.path.join(data_path, filename)
                with open(file_path, "r", encoding='utf-8') as data_file:
                    reader = csv.reader(data_file, delimiter=';')
                    headers = next(reader)
                    combined_rows = [headers + metadata_headers]  # Combined header row
                    for row in reader:
                        combined_row = row + metadata_row
                        combined_rows.append(combined_row)
                # Write the combined rows to a new CSV file
                os.makedirs(merged_files, exist_ok=True)
                output_file_path = os.path.join(merged_files, f"temp_merged_{filename}")
                with open(output_file_path, "w", encoding='utf-8', newline='') as output_file:
                    writer = csv.writer(output_file, delimiter=';')
                    writer.writerows(combined_rows)
                print(f"Combined data written to {output_file_path}")

# Load the metadata
metadata_headers, metadata_dict = load_metadata(metadata_file_path)

# Combine data and metadata
combine_data_and_metadata(data_path, metadata_headers, metadata_dict)
