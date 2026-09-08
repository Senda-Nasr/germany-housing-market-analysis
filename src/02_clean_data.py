"""
02_clean_data.py
Cleans raw housing data: removes duplicates, fixes missing values, standardizes columns,
handles outliers, and saves a clean dataset to data/processed/.

Usage:
    python src/02_clean_data.py
"""

import os
import sys
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "immo_data.csv")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")
CLEAN_PATH = os.path.join(PROCESSED_DIR, "immo_data_clean.csv")


def load_data() -> pd.DataFrame:
    """Load raw CSV data."""
    logger.info(f"Loading data from: {RAW_PATH}")
    df = pd.read_csv(RAW_PATH)
    logger.info(f"Loaded {len(df):,} rows with {len(df.columns)} columns")
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate rows based on scoutId (unique listing ID)."""
    before = len(df)
    if 'scoutId' in df.columns:
        df = df.drop_duplicates(subset=['scoutId'], keep='first')
    else:
        df = df.drop_duplicates(keep='first')
    after = len(df)
    logger.info(f"Removed {before - after:,} duplicate rows ({after:,} remaining)")
    return df


def remove_impossible_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows with impossible/outlier values that are clearly data errors.
    """
    before = len(df)

    # baseRent must be positive and reasonable (€10 to €10,000/month)
    df = df[(df['baseRent'] >= 10) & (df['baseRent'] <= 10_000)]

    # totalRent must be positive and reasonable (€10 to €15,000/month)
    if 'totalRent' in df.columns:
        df = df[(df['totalRent'] >= 10) & (df['totalRent'] <= 15_000)]

    # livingSpace must be reasonable (10 m² to 500 m²)
    df = df[(df['livingSpace'] >= 10) & (df['livingSpace'] <= 500)]

    # noRooms must be reasonable (1 to 20)
    df = df[(df['noRooms'] >= 1) & (df['noRooms'] <= 20)]

    # serviceCharge should be reasonable (€0 to €2,000)
    if 'serviceCharge' in df.columns:
        df = df[(df['serviceCharge'].isna()) | ((df['serviceCharge'] >= 0) & (df['serviceCharge'] <= 2_000))]

    # heatingCosts should be reasonable (€0 to €2,000)
    if 'heatingCosts' in df.columns:
        df = df[(df['heatingCosts'].isna()) | ((df['heatingCosts'] >= 0) & (df['heatingCosts'] <= 2_000))]

    after = len(df)
    logger.info(f"Removed {before - after:,} rows with impossible values ({after:,} remaining)")
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values column by column with appropriate strategies.
    """
    logger.info("Handling missing values...")
    null_report = []

    # --- Columns with very high null rates (>60%) — drop these columns entirely ---
    # These are mostly telecom/electricity details not core to housing analysis
    high_null_cols = [
        'telekomHybridUploadSpeed',  # 83% null
        'electricityBasePrice',      # 83% null
        'electricityKwhPrice',       # 83% null
        'energyEfficiencyClass',     # 71% null
        'lastRefurbish',             # 70% null
        'heatingCosts',              # 68% null
        'noParkSpaces',              # 65% null
    ]
    existing_high_null = [c for c in high_null_cols if c in df.columns]
    df = df.drop(columns=existing_high_null)
    logger.info(f"Dropped {len(existing_high_null)} columns with >60% nulls: {existing_high_null}")

    # --- Columns with moderate nulls — fill with sensible defaults ---

    # yearConstructed: fill with median year per region (geo_bln = state)
    if 'yearConstructed' in df.columns:
        null_count = df['yearConstructed'].isna().sum()
        if 'geo_bln' in df.columns:
            df['yearConstructed'] = df.groupby('geo_bln')['yearConstructed'].transform(
                lambda x: x.fillna(x.median())
            )
        # If still null (e.g. region had no data), fill with overall median
        df['yearConstructed'] = df['yearConstructed'].fillna(df['yearConstructed'].median())
        null_report.append(('yearConstructed', null_count, 'filled with median (by state)'))

    # yearConstructedRange: same as yearConstructed
    if 'yearConstructedRange' in df.columns:
        null_count = df['yearConstructedRange'].isna().sum()
        if 'geo_bln' in df.columns:
            df['yearConstructedRange'] = df.groupby('geo_bln')['yearConstructedRange'].transform(
                lambda x: x.fillna(x.median())
            )
        df['yearConstructedRange'] = df['yearConstructedRange'].fillna(df['yearConstructedRange'].median())
        null_report.append(('yearConstructedRange', null_count, 'filled with median (by state)'))

    # floor: fill with median
    if 'floor' in df.columns:
        null_count = df['floor'].isna().sum()
        df['floor'] = df['floor'].fillna(df['floor'].median())
        null_report.append(('floor', null_count, 'filled with median'))

    # numberOfFloors: fill with median
    if 'numberOfFloors' in df.columns:
        null_count = df['numberOfFloors'].isna().sum()
        df['numberOfFloors'] = df['numberOfFloors'].fillna(df['numberOfFloors'].median())
        null_report.append(('numberOfFloors', null_count, 'filled with median'))

    # thermalChar: fill with median
    if 'thermalChar' in df.columns:
        null_count = df['thermalChar'].isna().sum()
        df['thermalChar'] = df['thermalChar'].fillna(df['thermalChar'].median())
        null_report.append(('thermalChar', null_count, 'filled with median'))

    # serviceCharge: fill with median per state
    if 'serviceCharge' in df.columns:
        null_count = df['serviceCharge'].isna().sum()
        if 'geo_bln' in df.columns:
            df['serviceCharge'] = df.groupby('geo_bln')['serviceCharge'].transform(
                lambda x: x.fillna(x.median())
            )
        df['serviceCharge'] = df['serviceCharge'].fillna(df['serviceCharge'].median())
        null_report.append(('serviceCharge', null_count, 'filled with median (by state)'))

    # totalRent: fill with baseRent + serviceCharge (if both available)
    if 'totalRent' in df.columns:
        null_count = df['totalRent'].isna().sum()
        # Where totalRent is null but baseRent and serviceCharge exist, estimate
        mask = df['totalRent'].isna() & df['baseRent'].notna() & df['serviceCharge'].notna()
        df.loc[mask, 'totalRent'] = df.loc[mask, 'baseRent'] + df.loc[mask, 'serviceCharge']
        # For remaining nulls, fill with baseRent * 1.2 (rough estimate)
        remaining_mask = df['totalRent'].isna() & df['baseRent'].notna()
        df.loc[remaining_mask, 'totalRent'] = df.loc[remaining_mask, 'baseRent'] * 1.2
        # Last resort: fill with median
        df['totalRent'] = df['totalRent'].fillna(df['totalRent'].median())
        null_report.append(('totalRent', null_count, 'filled with baseRent + serviceCharge or estimate'))

    # --- Categorical columns: fill with 'unknown' or mode ---

    # heatingType: fill with mode
    if 'heatingType' in df.columns:
        null_count = df['heatingType'].isna().sum()
        mode_val = df['heatingType'].mode().iloc[0] if not df['heatingType'].mode().empty else 'unknown'
        df['heatingType'] = df['heatingType'].fillna(mode_val)
        null_report.append(('heatingType', null_count, f'filled with mode: {mode_val}'))

    # telekomTvOffer: fill with 'unknown'
    if 'telekomTvOffer' in df.columns:
        null_count = df['telekomTvOffer'].isna().sum()
        df['telekomTvOffer'] = df['telekomTvOffer'].fillna('unknown')
        null_report.append(('telekomTvOffer', null_count, 'filled with unknown'))

    # telekomUploadSpeed: fill with median
    if 'telekomUploadSpeed' in df.columns:
        null_count = df['telekomUploadSpeed'].isna().sum()
        df['telekomUploadSpeed'] = df['telekomUploadSpeed'].fillna(df['telekomUploadSpeed'].median())
        null_report.append(('telekomUploadSpeed', null_count, 'filled with median'))

    # firingTypes: fill with 'unknown'
    if 'firingTypes' in df.columns:
        null_count = df['firingTypes'].isna().sum()
        df['firingTypes'] = df['firingTypes'].fillna('unknown')
        null_report.append(('firingTypes', null_count, 'filled with unknown'))

    # condition: fill with 'unknown'
    if 'condition' in df.columns:
        null_count = df['condition'].isna().sum()
        df['condition'] = df['condition'].fillna('unknown')
        null_report.append(('condition', null_count, 'filled with unknown'))

    # interiorQual: fill with 'unknown'
    if 'interiorQual' in df.columns:
        null_count = df['interiorQual'].isna().sum()
        df['interiorQual'] = df['interiorQual'].fillna('unknown')
        null_report.append(('interiorQual', null_count, 'filled with unknown'))

    # petsAllowed: fill with 'unknown'
    if 'petsAllowed' in df.columns:
        null_count = df['petsAllowed'].isna().sum()
        df['petsAllowed'] = df['petsAllowed'].fillna('unknown')
        null_report.append(('petsAllowed', null_count, 'filled with unknown'))

    # houseNumber: fill with 'unknown'
    if 'houseNumber' in df.columns:
        null_count = df['houseNumber'].isna().sum()
        df['houseNumber'] = df['houseNumber'].fillna('unknown')
        null_report.append(('houseNumber', null_count, 'filled with unknown'))

    # streetPlain: fill with 'unknown'
    if 'streetPlain' in df.columns:
        null_count = df['streetPlain'].isna().sum()
        df['streetPlain'] = df['streetPlain'].fillna('unknown')
        null_report.append(('streetPlain', null_count, 'filled with unknown'))

    # typeOfFlat: fill with mode
    if 'typeOfFlat' in df.columns:
        null_count = df['typeOfFlat'].isna().sum()
        mode_val = df['typeOfFlat'].mode().iloc[0] if not df['typeOfFlat'].mode().empty else 'unknown'
        df['typeOfFlat'] = df['typeOfFlat'].fillna(mode_val)
        null_report.append(('typeOfFlat', null_count, f'filled with mode: {mode_val}'))

    # description: fill with placeholder
    if 'description' in df.columns:
        null_count = df['description'].isna().sum()
        df['description'] = df['description'].fillna('no_description')
        null_report.append(('description', null_count, 'filled with no_description'))

    # facilities: fill with placeholder
    if 'facilities' in df.columns:
        null_count = df['facilities'].isna().sum()
        df['facilities'] = df['facilities'].fillna('no_facilities')
        null_report.append(('facilities', null_count, 'filled with no_facilities'))

    # pricetrend: fill with 0 (no trend)
    if 'pricetrend' in df.columns:
        null_count = df['pricetrend'].isna().sum()
        df['pricetrend'] = df['pricetrend'].fillna(0)
        null_report.append(('pricetrend', null_count, 'filled with 0'))

    # Print summary
    logger.info("Missing value handling summary:")
    for col, count, strategy in null_report:
        logger.info(f"  {col}: {count:,} nulls → {strategy}")

    return df


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column formats and create useful derived fields.
    """
    logger.info("Standardizing columns...")

    # Convert date column to datetime
    if 'date' in df.columns:
        # Dates look like 'Feb20', 'Sep18' etc. — parse as monthly periods
        df['date'] = pd.to_datetime(df['date'], format='%b%y', errors='coerce')
        logger.info(f"Parsed date column: {df['date'].min()} to {df['date'].max()}")

    # Ensure boolean columns are proper bool type
    bool_cols = ['newlyConst', 'balcony', 'hasKitchen', 'cellar', 'lift', 'garden']
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype(bool)

    # Create price_per_m2 feature (rent per square meter)
    if 'baseRent' in df.columns and 'livingSpace' in df.columns:
        df['price_per_m2'] = (df['baseRent'] / df['livingSpace']).round(2)
        # Cap at reasonable values (€5 to €100 per m²)
        df['price_per_m2'] = df['price_per_m2'].clip(5, 100)
        logger.info("Created price_per_m2 feature")

    # Create total_price_per_m2
    if 'totalRent' in df.columns and 'livingSpace' in df.columns:
        df['total_price_per_m2'] = (df['totalRent'] / df['livingSpace']).round(2)
        df['total_price_per_m2'] = df['total_price_per_m2'].clip(5, 150)
        logger.info("Created total_price_per_m2 feature")

    # Clean up state names (replace underscores with spaces)
    if 'regio1' in df.columns:
        df['state'] = df['regio1'].str.replace('_', ' ').str.strip()
        logger.info("Created clean 'state' column from regio1")

    # Clean up city names
    if 'regio2' in df.columns:
        df['city'] = df['regio2'].str.replace('_', ' ').str.strip()
        logger.info("Created clean 'city' column from regio2")

    # Create property size category
    if 'livingSpace' in df.columns:
        bins = [0, 30, 50, 80, 120, 200, 500]
        labels = ['very_small', 'small', 'medium', 'large', 'very_large', 'luxury']
        df['size_category'] = pd.cut(df['livingSpace'], bins=bins, labels=labels)
        logger.info("Created size_category feature")

    # Create room count category
    if 'noRooms' in df.columns:
        bins = [0, 1, 2, 3, 4, 6, 20]
        labels = ['studio', '1_bedroom', '2_bedroom', '3_bedroom', '4_bedroom', '5_plus_bedroom']
        df['room_category'] = pd.cut(df['noRooms'], bins=bins, labels=labels)
        logger.info("Created room_category feature")

    return df


def final_cleanup(df: pd.DataFrame) -> pd.DataFrame:
    """
    Final cleanup: drop any remaining rows with nulls in critical columns,
    reset index, and ensure consistent ordering.
    """
    before = len(df)

    # Critical columns that must not be null
    critical_cols = ['baseRent', 'livingSpace', 'noRooms', 'geo_bln', 'regio1']
    existing_critical = [c for c in critical_cols if c in df.columns]
    df = df.dropna(subset=existing_critical)
    after = len(df)
    logger.info(f"Dropped {before - after:,} rows with nulls in critical columns")

    # Reset index
    df = df.reset_index(drop=True)

    return df


def save_clean_data(df: pd.DataFrame) -> None:
    """Save the cleaned dataset to the processed directory."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)
    file_size = os.path.getsize(CLEAN_PATH) / (1024 * 1024)  # MB
    logger.info(f"Saved clean data to: {CLEAN_PATH}")
    logger.info(f"Final shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    logger.info(f"File size: {file_size:.2f} MB")


def main():
    """Main cleaning pipeline."""
    logger.info("=" * 60)
    logger.info("STARTING DATA CLEANING PIPELINE")
    logger.info("=" * 60)

    # Step 1: Load
    df = load_data()

    # Step 2: Remove duplicates
    df = remove_duplicates(df)

    # Step 3: Remove impossible values
    df = remove_impossible_values(df)

    # Step 4: Handle missing values
    df = handle_missing_values(df)

    # Step 5: Standardize columns and create features
    df = standardize_columns(df)

    # Step 6: Final cleanup
    df = final_cleanup(df)

    # Step 7: Save
    save_clean_data(df)

    # Summary
    logger.info("=" * 60)
    logger.info("CLEANING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Original rows: 268,850")
    logger.info(f"Final rows:    {len(df):,}")
    logger.info(f"Removed:       {268_850 - len(df):,} rows ({(268_850 - len(df)) / 268_850 * 100:.1f}%)")
    logger.info(f"Columns:       {df.shape[1]}")
    logger.info(f"Null values remaining: {df.isnull().sum().sum():,}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
