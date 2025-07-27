import pandas as pd
import streamlit as st
from typing import Dict, Any, List
import plotly.express as px
import plotly.graph_objects as go

def format_number(num: int) -> str:
    """Format large numbers with appropriate suffixes"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(num)

def get_table_info(columns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract useful information from table column definitions"""
    info = {
        'total_columns': len(columns),
        'primary_keys': [],
        'foreign_keys': [],
        'nullable_columns': [],
        'auto_increment': [],
        'data_types': {}
    }
    
    for col in columns:
        # Primary keys
        if col['Key'] == 'PRI':
            info['primary_keys'].append(col['Field'])
        
        # Foreign keys
        if col['Key'] == 'MUL':
            info['foreign_keys'].append(col['Field'])
        
        # Nullable columns
        if col['Null'] == 'YES':
            info['nullable_columns'].append(col['Field'])
        
        # Auto increment
        if 'auto_increment' in str(col['Extra']).lower():
            info['auto_increment'].append(col['Field'])
        
        # Data types
        data_type = col['Type'].split('(')[0]  # Remove size specification
        if data_type in info['data_types']:
            info['data_types'][data_type] += 1
        else:
            info['data_types'][data_type] = 1
    
    return info

def create_distribution_chart(df: pd.DataFrame, column: str, chart_type: str = 'histogram') -> go.Figure:
    """Create distribution chart for a column"""
    if chart_type == 'histogram':
        fig = px.histogram(df, x=column, title=f'Distribution of {column}')
    elif chart_type == 'box':
        fig = px.box(df, y=column, title=f'Box Plot of {column}')
    else:
        fig = px.violin(df, y=column, title=f'Violin Plot of {column}')
    
    return fig

def create_correlation_matrix(df: pd.DataFrame) -> go.Figure:
    """Create correlation matrix heatmap for numeric columns"""
    numeric_df = df.select_dtypes(include=['number'])
    
    if numeric_df.empty:
        return None
    
    correlation_matrix = numeric_df.corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.columns,
        colorscale='RdBu',
        zmid=0
    ))
    
    fig.update_layout(
        title='Correlation Matrix',
        xaxis_tickangle=-45
    )
    
    return fig

def create_time_series_chart(df: pd.DataFrame, date_column: str, value_column: str = None) -> go.Figure:
    """Create time series chart"""
    if value_column:
        fig = px.line(df, x=date_column, y=value_column, 
                     title=f'{value_column} over Time')
    else:
        # Count records over time
        df_grouped = df.groupby(df[date_column].dt.date).size().reset_index(name='count')
        fig = px.line(df_grouped, x=date_column, y='count', 
                     title=f'Records Count over Time')
    
    return fig

def identify_column_types(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Identify column types for better visualization"""
    column_types = {
        'numeric': [],
        'categorical': [],
        'datetime': [],
        'text': [],
        'id': []
    }
    
    for col in df.columns:
        col_lower = col.lower()
        
        # ID columns
        if 'id' in col_lower:
            column_types['id'].append(col)
        # Datetime columns
        elif df[col].dtype in ['datetime64[ns]', 'object']:
            if df[col].dtype == 'object':
                try:
                    pd.to_datetime(df[col].dropna().iloc[:100])  # Test first 100 rows
                    column_types['datetime'].append(col)
                except:
                    if df[col].nunique() < len(df) * 0.5:  # Less than 50% unique values
                        column_types['categorical'].append(col)
                    else:
                        column_types['text'].append(col)
            else:
                column_types['datetime'].append(col)
        # Numeric columns
        elif df[col].dtype in ['int64', 'float64', 'int32', 'float32']:
            if df[col].nunique() < 10 and df[col].max() < 100:  # Likely categorical
                column_types['categorical'].append(col)
            else:
                column_types['numeric'].append(col)
        # Text/categorical
        else:
            if df[col].nunique() < len(df) * 0.5:
                column_types['categorical'].append(col)
            else:
                column_types['text'].append(col)
    
    return column_types

def export_to_csv(df: pd.DataFrame, filename: str) -> bytes:
    """Convert DataFrame to CSV bytes for download"""
    return df.to_csv(index=False).encode('utf-8')

def export_to_excel(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to Excel bytes for download"""
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    return output.getvalue()

def create_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Create summary statistics for DataFrame"""
    summary = df.describe(include='all').transpose()
    
    # Add additional statistics
    summary['null_count'] = df.isnull().sum()
    summary['null_percentage'] = (df.isnull().sum() / len(df) * 100).round(2)
    summary['unique_count'] = df.nunique()
    summary['unique_percentage'] = (df.nunique() / len(df) * 100).round(2)
    
    return summary
