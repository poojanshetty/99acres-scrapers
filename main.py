"""Dataset access helpers for the 99acres Bengaluru project."""

from pathlib import Path

import kagglehub


DATASET = "rohan2662/99acres-bengaluru-dataset"
CLEANED_FILENAME = "bengaluru-properties-99acres.xlsx"
RAW_FILENAME = "bengaluru-properties-99acres(Uncleaned_data) (1).xlsx"


def download_dataset() -> Path:
    """Download the dataset once, or return KaggleHub's existing cached copy."""
    cache_root = Path.home() / ".cache/kagglehub/datasets" / DATASET / "versions"
    cached_versions = sorted(cache_root.glob("*/"), reverse=True)
    if cached_versions:
        print(f"Using cached dataset: {cached_versions[0]}")
        return cached_versions[0]

    print("Preparing the 99acres Bengaluru dataset...")
    dataset_path = Path(kagglehub.dataset_download(DATASET))
    print(f"Dataset ready at: {dataset_path}")
    return dataset_path


def cleaned_dataset_file() -> Path:
    """Return the path to the cleaned Excel export in the Kaggle dataset."""
    file_path = download_dataset() / CLEANED_FILENAME
    if not file_path.exists():
        raise FileNotFoundError(f"Could not find {CLEANED_FILENAME} in the downloaded dataset.")
    return file_path


def raw_dataset_file() -> Path:
    """Return the path to the original, uncleaned Excel export."""
    file_path = download_dataset() / RAW_FILENAME
    if not file_path.exists():
        raise FileNotFoundError(f"Could not find {RAW_FILENAME} in the downloaded dataset.")
    return file_path


def main() -> None:
    print(cleaned_dataset_file())


if __name__ == "__main__":
    main()
