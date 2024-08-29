from data_extraction import ine_api
from data_processing import ine_merge_data, ine_final_data


def ine_main():
    try:
        ine_api.main()
    except Exception as e:
        print(f"Error: {e}")
    
    try:
        ine_merge_data.main()
    except Exception as e:
        print(f"Error: {e}")

    try:
        ine_final_data.main()
    except Exception as e:
        print(f"Error: {e}")
        

if __name__ == "__main__":
    ine_main()