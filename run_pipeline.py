"""Build the dashboard-ready CSV from the raw Kaggle dataset.

Run with: python run_pipeline.py
"""

from pathlib import Path

import pandas as pd

from main import raw_dataset_file
from src.data_pipeline import clean_raw_properties


OUTPUT_FILE = Path("notebooks/bengaluru_properties_cleaned_with_ratings.csv")


def main() -> None:
    raw_data = pd.read_excel(raw_dataset_file())
    final_data = clean_raw_properties(raw_data)
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    final_data.to_csv(OUTPUT_FILE, index=False)
    print(f"Created {OUTPUT_FILE} with {len(final_data)} cleaned listings.")


if __name__ == "__main__":
    main()
