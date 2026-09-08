"""
01_download_data.py
Simple script to download housing data from Kaggle and save to data/raw/

USAGE:
    python src/01_download_data.py corrieaar/apartment-rental-offers-in-germany
    python src/01_download_data.py https://example.com/data.csv
"""

import os
import sys
import shutil
import logging

# Set up logging to show progress messages
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Path to where we'll save the data
DATA_RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")


def ensure_data_dir():
    """Create the data/raw directory if it doesn't exist."""
    os.makedirs(DATA_RAW_DIR, exist_ok=True)


def download_kaggle_dataset(dataset_name: str) -> str:
    """
    Download a dataset from Kaggle using kagglehub.

    Args:
        dataset_name: Kaggle dataset name like "username/dataset-name"

    Returns:
        Path where the dataset was saved
    """
    try:
        import kagglehub
    except ImportError:
        logger.error("kagglehub not installed. Run: pip install kagglehub")
        sys.exit(1)

    logger.info(f"Downloading Kaggle dataset: {dataset_name}")

    # Download the dataset (saves to a temp location)
    temp_path = kagglehub.dataset_download(dataset_name)

    if not temp_path:
        raise RuntimeError(f"Failed to download {dataset_name}")

    # If it's a directory with multiple files, copy all files to data/raw
    if os.path.isdir(temp_path):
        logger.info(f"Copying dataset files to {DATA_RAW_DIR}")

        # Copy all files from the temp directory to data/raw
        for filename in os.listdir(temp_path):
            src_file = os.path.join(temp_path, filename)
            dst_file = os.path.join(DATA_RAW_DIR, filename)

            if os.path.isdir(src_file):
                # If it's a subdirectory, copy recursively
                if os.path.exists(dst_file):
                    shutil.rmtree(dst_file)
                shutil.copytree(src_file, dst_file)
            else:
                # If it's a file, copy it
                shutil.copy2(src_file, dst_file)

            logger.info(f"Copied: {filename}")

        return DATA_RAW_DIR

    # If it's a single file, copy it to data/raw
    else:
        filename = os.path.basename(temp_path)
        final_path = os.path.join(DATA_RAW_DIR, filename)
        shutil.copy2(temp_path, final_path)

        logger.info(f"File saved to: {final_path}")
        return final_path


def download_file_url(url: str) -> str:
    """
    Download a file from a direct URL.

    Args:
        url: Direct download URL

    Returns:
        Path where the file was saved
    """
    import requests

    # Get filename from URL
    filename = url.split('/')[-1]
    if not filename:
        filename = "downloaded_file"

    target_path = os.path.join(DATA_RAW_DIR, filename)

    logger.info(f"Downloading from URL: {url}")
    logger.info(f"Saving to: {target_path}")

    # Download the file
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()  # Check for errors

    # Save to file
    with open(target_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    logger.info(f"Download complete! File size: {os.path.getsize(target_path):,} bytes")
    return target_path


def main():
    """Main function that runs when script is executed."""
    ensure_data_dir()

    # Check if user provided a data source
    if len(sys.argv) < 2:
        logger.error("No data source provided!")
        logger.info("Usage examples:")
        logger.info("  python src/01_download_data.py corrieaar/apartment-rental-offers-in-germany")
        logger.info("  python src/01_download_data.py https://example.com/data.csv")
        sys.exit(1)

    source = sys.argv[1]

    # Decide if it's a Kaggle dataset or URL
    if source.startswith("http://") or source.startswith("https://"):
        # It's a direct URL
        download_file_url(source)
    else:
        # Assume it's a Kaggle dataset name
        download_kaggle_dataset(source)

    logger.info("✅ Data download complete!")


if __name__ == "__main__":
    main()
