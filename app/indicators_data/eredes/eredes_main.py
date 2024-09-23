from data_extraction import eredes_data, eredes_metadata
from data_processing import eredes_merge_files, eredes_final_format


def eredes_main() -> None:
    """
    Main function to execute the Eredes data processing pipeline.

    This function calls several main functions from different modules
    responsible for data extraction, metadata handling, merging files,
    and formatting the final output. Any errors encountered during 
    execution are printed to the console.
    """
    try:
        eredes_data.main()
    except Exception as e:
        print(f"Error en eredes_data.main(): {e}")

    try:
        eredes_metadata.main()
    except Exception as e:
        print(f"Error en eredes_metadata.main(): {e}")

    try:
        eredes_merge_files.main()
    except Exception as e:
        print(f"Error en eredes_merge_files.main(): {e}")

    try:
        eredes_final_format.main()
    except Exception as e:
        print(f"Error en eredes_final_format.main(): {e}")

        

if __name__ == "__main__":
    eredes_main()
