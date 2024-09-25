# Quick Start
A brief guide for setting up and executing the application.
<br>
- **Step 1**: Create and activate a virtual environment (venv) in the project's folder (irradiare-app).<br>
  
- **Step 2**: Install the required dependencies by executing the following command in the terminal:


```
pip install -r requirements.txt
```

<br>

- **Step 3**: Navigate to the [indicators_data](/app/indicators_data) folder.
  
- **Step 4**: Initiate the data extraction and transformation process by entering the following command in the terminal:

```
python data_main.py
```

<br>

- **Step 5**: Follow the prompts provided in the terminal. The only manual step in this process involves the Eurostat data retrieval, which requires user confirmation to proceed after completing the indicated tasks. Detailed instructions for this step can be found [here](/app/indicators_data), along with the rest of the execution process dedicated to Eurostat indicators data.

- *Note that the duration of the process may vary depending on your computer's specifications.*

- **Step 6**: Upon completion, all necessary files for database insertion will be generated.

- **Step 7**: Change the directory to the database [database (db)](/app/db) folder.
  
- **Step 8**: Execute the following command to create and populate the database:

```
python fill_sqlite_db.py
```

<br>

- **Important Consideration**: The selection of indicators for this project has not been finalized. While all indicators are relevant to socio-economic and environmental matters, many may not significantly contribute to the company's projects tracking. Consequently, the volume of data retrieved and processed could be substantial, potentially consuming terabytes of storage until only the essential indicators are retained. Reducing the number of involved indicators will streamline the database filling process.

- **Step 9**: Once the database is loaded, navigate back to the main project folder [irradiare-app](/irradiare-app).

- **Step 10**: Start the Uvicorn server for the FastAPI project with the following command:

```
uvicorn app.api.main:app --reload
```

<br>

- For more information regarding the API and its interaction with the database, please refer to the documentation [here](/app/docs/api-guide).

- If all steps were executed successfully, the application should now be running, allowing users to retrieve data as needed.
