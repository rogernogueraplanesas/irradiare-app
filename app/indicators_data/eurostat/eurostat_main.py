from data_extraction import eurostat_client_data, eurostat_get_metadata
from data_processing import eurostat_datacodes, extract_xml_files, eurostat_join_codes, eurostat_final_data


def eurostat_main():
    try:
        eurostat_client_data.main()
    except Exception as e:
        print(f"Error: {e}")
    
    try:
        eurostat_datacodes.main()
    except Exception as e:
        print(f"Error: {e}")

    try:
        eurostat_get_metadata.main()
    except Exception as e:
        print(f"Error: {e}")

    try:
        extract_xml_files.main()
    except Exception as e:
        print(f"Error: {e}")

    try:
        eurostat_join_codes.main()
    except Exception as e:
        print(f"Error: {e}")

    try:
        eurostat_final_data.main()
    except Exception as e:
        print(f"Error: {e}")
        

if __name__ == "__main__":
    eurostat_main()