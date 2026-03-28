# Data Wrangler and Visualizer
An interactive Streamlit web application for uploading, 
cleaning, exploring, visualizing, and exporting datasets. 
Designed for data wrangling coursework.

## The link
https://data-wrangling-coursework.streamlit.app/


## Features

# --- Upload datasets in CSV, Excel (.xlsx), or JSON formats
# --- Dataset overview:
    Shape (rows & columns)
    Column names and data types
    Missing values
    Duplicate rows
    Summary stats
# --- Data cleaning and preparation:
    Handle missing values
    Remove duplicates
    Rename columns
    Feature engineering (e.g., binning)
# --- Visualization:
    Histogram
    Box plot
    Scatter plot
    Line chart
    Bar chart
    Correlation heatmap
    Filtering by categorical and numeric columns
# --- Export ready data and reports


## Project strcuture
.
├── app.py
├── tabs/
│   ├── upload_and_overview.py
│   ├── cleaning_and_prep.py
│   ├── visualization.py
│   └── export_and_report.py
|
|   ├── transformation report/   *(consists of report files from the recorded and uloaded session run)*
|   ├── datasets/                *(include several sample datasets - games.csv was used in the uploaded video)*


# General idea / workflow
1. User uploads a data from the sidebar
2. The app stores data in session_state
3. User navigates to Cleaning page and performs necessary actions
4. Visualizations helps to build plots
5. Lastly, Export page helps to download the ready materials togather with log history in JSON file


## How to run
streamlit run app.py


## Notes
Large datasets may take time to process, but caching helps improve performance
Visualization tools dynamically adapt to column types
The app resets state when a new file is uploaded
