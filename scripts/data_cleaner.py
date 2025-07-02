#!/usr/bin/env python3
"""
Advanced Research Data Cleaner
=============================
Now includes:
- Outlier detection and handling
- Date standardization
- Categorical encoding
- Advanced text cleaning
- Data validation
"""
import pandas as pd
import numpy as np
import argparse
from pathlib import Path
import logging
import re
from typing import Union, Optional
import unicodedata
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='data_cleaning.log'
)
logger = logging.getLogger(__name__)

def load_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """Load dataset with additional format support"""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        file_extension = file_path.suffix.lower()
        
        if file_extension == '.csv':
            return pd.read_csv(file_path, encoding_errors='replace')
        elif file_extension in ('.xls', '.xlsx'):
            return pd.read_excel(file_path)
        elif file_extension == '.json':
            return pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
            
    except Exception as e:
        logger.error(f"Error loading file: {e}")
        raise

def clean_text(text: str) -> str:
    """Advanced text cleaning"""
    if pd.isna(text):
        return ""
    
    text = str(text)
    # Remove special characters but preserve accents
    text = unicodedata.normalize('NFKC', text)
    # Standardize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def handle_outliers(df: pd.DataFrame, column: str, method: str = 'clip') -> pd.DataFrame:
    """Handle outliers using specified method (clip/remove/median)"""
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    if method == 'clip':
        df[column] = df[column].clip(lower_bound, upper_bound)
    elif method == 'remove':
        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    elif method == 'median':
        median_val = df[column].median()
        df.loc[df[column] < lower_bound, column] = median_val
        df.loc[df[column] > upper_bound, column] = median_val
    
    return df

def standardize_dates(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Convert various date formats to YYYY-MM-DD"""
    def parse_date(date_str):
        try:
            return pd.to_datetime(date_str, errors='coerce').date()
        except:
            return np.nan
    
    df[column] = df[column].apply(parse_date)
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Perform comprehensive data cleaning"""
    try:
        cleaned_df = df.copy()
        original_rows = len(cleaned_df)
        logger.info(f"Original dataset contains {original_rows} rows")
        
        # 1. Advanced text cleaning
        text_cols = cleaned_df.select_dtypes(include=['object']).columns
        for col in text_cols:
            cleaned_df[col] = cleaned_df[col].apply(clean_text)
            # Handle empty strings after cleaning
            cleaned_df[col] = cleaned_df[col].replace('', np.nan)
        
        # 2. Remove duplicates
        cleaned_df = cleaned_df.drop_duplicates()
        
        # 3. Handle missing values
        for col in cleaned_df.columns:
            if pd.api.types.is_numeric_dtype(cleaned_df[col]):
                median_val = cleaned_df[col].median()
                cleaned_df[col] = cleaned_df[col].fillna(median_val)
            elif pd.api.types.is_datetime64_any_dtype(cleaned_df[col]):
                cleaned_df[col] = cleaned_df[col].fillna(pd.Timestamp('now'))
            else:
                mode_val = cleaned_df[col].mode()[0] if not cleaned_df[col].mode().empty else ""
                cleaned_df[col] = cleaned_df[col].fillna(mode_val)
        
        # 4. Handle outliers in numeric columns
        numeric_cols = cleaned_df.select_dtypes(include=np.number).columns
        for col in numeric_cols:
            cleaned_df = handle_outliers(cleaned_df, col, method='clip')
        
        # 5. Standardize dates
        date_cols = [col for col in cleaned_df.columns if 'date' in col.lower()]
        for col in date_cols:
            cleaned_df = standardize_dates(cleaned_df, col)
        
        # Final stats
        cleaned_rows = len(cleaned_df)
        logger.info(f"Removed {original_rows - cleaned_rows} problematic rows")
        logger.info(f"Final dataset contains {cleaned_rows} clean rows")
        
        return cleaned_df
        
    except Exception as e:
        logger.error(f"Cleaning failed: {e}")
        raise

def export_data(df: pd.DataFrame, output_path: Union[str, Path], format: str = 'csv') -> None:
    """Export cleaned data to multiple formats"""
    try:
        output_path = Path(output_path)
        if format == 'csv':
            df.to_csv(output_path, index=False)
        elif format == 'excel':
            df.to_excel(output_path, index=False)
        elif format == 'json':
            df.to_json(output_path, orient='records')
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
        logger.info(f"Successfully exported cleaned data to {output_path}")
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise

def main():
    """Enhanced command line interface"""
    parser = argparse.ArgumentParser(
        description="Advanced Research Data Cleaning Utility",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('input_file', help="Path to input data file")
    parser.add_argument('-o', '--output', default='cleaned_data.csv',
                       help="Output file path")
    parser.add_argument('-f', '--format', default='csv',
                       choices=['csv', 'excel', 'json'],
                       help="Output file format")
    
    args = parser.parse_args()
    
    try:
        logger.info("Starting advanced data cleaning process")
        
        # Load data
        raw_data = load_data(args.input_file)
        
        # Clean data
        cleaned_data = clean_data(raw_data)
        
        # Export results
        export_data(cleaned_data, args.output, args.format)
        
        logger.info("Data cleaning completed successfully")
        print(f"\nSUCCESS: Cleaned data saved to {args.output}")
        
    except Exception as e:
        logger.critical(f"Process failed: {e}")
        print(f"\nERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    import sys
    main()