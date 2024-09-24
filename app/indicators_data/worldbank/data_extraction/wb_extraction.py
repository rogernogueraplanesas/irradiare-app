import requests
import zipfile
import os


def create_directories(paths: list[str]) -> None:
    """
    Create directories if they do not already exist.

    Args:
        paths (list[str]): List of directory paths to create.

    Returns:
        None
    """
    for path in paths:
        os.makedirs(path, exist_ok=True)


def download_zip_file(url: str, zip_path: str) -> None:
    """
    Download a ZIP file from the specified URL and save it to the given path.

    Args:
        url (str): The URL to download the ZIP file from.
        zip_path (str): The path where the downloaded ZIP file will be saved.

    Returns:
        None
    """
    response = requests.get(url)
    with open(zip_path, 'wb') as f:
        f.write(response.content)


def extract_zip_file(zip_path: str, extract_to: str, file_names: list[str]) -> None:
    """
    Extract specific files from a ZIP file to the specified directory.

    Args:
        zip_path (str): The path to the ZIP file.
        extract_to (str): The directory to extract the files into.
        file_names (list[str]): List of filenames to extract from the ZIP file.

    Returns:
        None
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file_name in file_names:
            zip_ref.extract(file_name, extract_to)


def main() -> None:
    """
    Main function to execute the download and extraction process.

    Returns:
        None
    """
    # URL of the WORLD BANK API from which a ZIP file including data+metadata is downloaded
    url = "https://api.worldbank.org/v2/en/country/PRT?downloadformat=csv&_gl=1*d5zsxg*_gcl_au*MTA2OTI2NjE1My4xNzI1NzE5Mzgy"

    # Paths for storing downloaded and extracted files
    complementary_path = "app/indicators_data/worldbank/wb_data/wb_comp_files"
    zip_path = os.path.join(complementary_path, "files.zip")
    data_path = "app/indicators_data/worldbank/wb_data/raw"
    metadata_path = "app/indicators_data/worldbank/wb_metadata"

    # Create necessary directories
    create_directories([complementary_path, data_path, metadata_path])

    # Download the ZIP file
    download_zip_file(url, zip_path)

    # Extract the data and the metadata CSV files
    extract_zip_file(zip_path, data_path, ['API_PRT_DS2_en_csv_v2_3412148.csv'])
    extract_zip_file(zip_path, metadata_path, ['Metadata_Indicator_API_PRT_DS2_en_csv_v2_3412148.csv'])

    print("Process completed.")


if __name__ == "__main__":
    main()

