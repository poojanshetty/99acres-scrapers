# Bengaluru Property Market Analysis

An end-to-end data analytics project that turns raw 99acres Bengaluru property
listings into a cleaned, interactive dashboard for comparing homes by location,
budget, area, BHK configuration, and price per square foot.

## Project motivation

Property listings are often difficult to compare because prices use mixed units
(lakhs and crores), areas use text formatting, and the same project can appear
more than once. This project demonstrates how I transform unstructured listing
data into a useful decision-support tool. A potential buyer can use the
dashboard to explore available apartments, compare locations, and identify
properties that offer better value relative to their local market.

## What this project demonstrates to recruiters

- Data acquisition using the KaggleHub API
- Exploratory data analysis (EDA) using pandas, NumPy, Matplotlib, Seaborn, and Plotly
- Data cleaning: text parsing, type conversion, missing-value handling, and duplicate detection
- Regular expressions to separate property names and ratings from raw scraped text
- Feature engineering: `price_lakhs`, `price_crores`, `area_sqft`, and `price_per_sqft`
- Data-quality validation: reconciling 412 raw records with 398 cleaned records by identifying 14 duplicates
- Interactive data storytelling and dashboard design with Streamlit and Plotly
- Reusable Python functions, dependency management, and project documentation

## Dataset

- **Source:** [99acres Bengaluru dataset on Kaggle](https://www.kaggle.com/datasets/rohan2662/99acres-bengaluru-dataset)
- **Raw listings:** 412
- **Cleaned listings:** 398
- **Removed records:** 14 exact duplicates

The final analytical dataset includes:

| Column | Description |
| --- | --- |
| `name` | Cleaned property/project name |
| `ratings` | Listing rating when available; otherwise null |
| `location` | Bengaluru locality extracted from the listing |
| `price_lakhs` | Numeric price in lakhs, used for analysis |
| `price_crores` | Numeric price in crores, for easier real-estate interpretation |
| `area_sqft` | Property area in square feet |
| `bhk` | Bedroom-Hall-Kitchen configuration |
| `price_per_sqft` | Derived measure used to compare properties fairly |

## Dashboard features

- Search by property name or location
- Filter by location, BHK, and budget
- Sort all listings by price or area, in ascending or descending order
- Summary metrics for listings, median price, and median area
- Price shown in both lakhs and crores
- Market insights for the top location, lowest-price listing, largest listing, and best local value
- A transparent local-value score that benchmarks price per square foot against each location's median
- Interactive BHK, location, and price-versus-area charts
- Searchable listings table and filtered CSV download

## Project structure

```text
99acres-scrapers/
├── app.py                                      # Streamlit dashboard
├── main.py                                     # Kaggle dataset download/cache helper
├── run_pipeline.py                              # Rebuilds the final analytical CSV
├── notebooks/
│   ├── 01_data_understanding.ipynb             # EDA and data-cleaning workflow
│   └── bengaluru_properties_cleaned_with_ratings.csv
├── requirements.txt                            # Python dependencies
├── src/data_pipeline.py                         # Reusable cleaning and feature functions
├── tests/test_data_pipeline.py                  # Automated data-quality tests
└── README.md
```

## Run locally

Clone the repository and move into the project directory:

```bash
git clone <your-repository-url>
cd 99acres-scrapers
```

Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies and start the dashboard:

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

The dashboard opens at `http://localhost:8501`. It automatically uses the
final CSV produced in the notebook. If that file is unavailable, `main.py`
uses the KaggleHub cache or downloads the public dataset. You can also upload a
CSV or Excel file through the dashboard sidebar.

## Rebuild and validate the dataset

The notebook documents the analysis, while the reusable pipeline makes the
cleaning process reproducible:

```bash
python run_pipeline.py
pytest
```

The tests validate the important cleaning rules: crore/lakh price conversion,
rating extraction, exact-duplicate removal, and price-per-square-foot calculation.

## Future improvements

- Add a map view of Bengaluru listings
- Add location-level value scores based on price per square foot
- Collect listing dates to analyse price trends over time
- Deploy the dashboard using Streamlit Community Cloud or a cloud platform
- Add automated data-quality tests for future dataset updates
