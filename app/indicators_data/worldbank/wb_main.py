from data_extraction import wb_api
from data_processing import wb_final_data


def wb_main():
    try:
        wb_api.main()
    except Exception as e:
        print(f"Error: {e}")
    
    try:
        wb_final_data.main()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    wb_main()