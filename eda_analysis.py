import pandas as pd

def centralized_column_analysis(df):
    """Perform detailed analysis on each column in the DataFrame."""
    analysis = {}
    for column in df.columns:
        analysis[column] = {
            'dtype': df[column].dtype,
            'unique_values': df[column].nunique(),
            'missing_values': df[column].isnull().sum(),
            'mean': df[column].mean() if df[column].dtype in ['int64', 'float64'] else None,
            'median': df[column].median() if df[column].dtype in ['int64', 'float64'] else None,
        }
    return analysis

def unified_duplicate_detection(df):
    """Identify and return duplicate rows in the DataFrame."""
    return df[df.duplicated()]

def list_analysis(data_list):
    """Analyze characteristics of a list, such as length and unique items."""
    return {
        'length': len(data_list),
        'unique_items': len(set(data_list)),
        'duplicates': [item for item in set(data_list) if data_list.count(item) > 1]
    }

def reusable_aggregation_patterns(df, group_by_column, agg_dict):
    """Perform aggregation on the DataFrame based on specified group and aggregation."""
    return df.groupby(group_by_column).agg(agg_dict)