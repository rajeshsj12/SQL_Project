import pandas as pd
import json
import csv
import io
from datetime import datetime
import zipfile
import logging

class ExportUtils:
    def __init__(self):
        """
        Initialize export utilities
        """
        self.logger = logging.getLogger(__name__)
    
    def to_csv(self, data, include_index=False):
        """
        Convert DataFrame to CSV format
        """
        try:
            if isinstance(data, pd.DataFrame):
                return data.to_csv(index=include_index)
            else:
                # Handle other data types
                df = pd.DataFrame(data)
                return df.to_csv(index=include_index)
                
        except Exception as e:
            self.logger.error(f"Error converting to CSV: {str(e)}")
            return f"Error: {str(e)}"
    
    def to_json(self, data, orient='records', indent=2):
        """
        Convert DataFrame to JSON format
        """
        try:
            if isinstance(data, pd.DataFrame):
                return data.to_json(orient=orient, indent=indent, date_format='iso')
            else:
                # Handle other data types
                return json.dumps(data, indent=indent, default=str)
                
        except Exception as e:
            self.logger.error(f"Error converting to JSON: {str(e)}")
            return f'{{"error": "{str(e)}"}}'
    
    def to_excel(self, data, sheet_name='Sheet1'):
        """
        Convert DataFrame to Excel format (bytes)
        """
        try:
            output = io.BytesIO()
            
            if isinstance(data, pd.DataFrame):
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    data.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                # Convert to DataFrame first
                df = pd.DataFrame(data)
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            return output.getvalue()
            
        except Exception as e:
            self.logger.error(f"Error converting to Excel: {str(e)}")
            # Return empty Excel file with error message
            error_df = pd.DataFrame({'Error': [str(e)]})
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                error_df.to_excel(writer, sheet_name='Error', index=False)
            return output.getvalue()
    
    def to_xml(self, data, root_name='data', row_name='record'):
        """
        Convert DataFrame to XML format
        """
        try:
            if isinstance(data, pd.DataFrame):
                return data.to_xml(root_name=root_name, row_name=row_name)
            else:
                # Convert to DataFrame first
                df = pd.DataFrame(data)
                return df.to_xml(root_name=root_name, row_name=row_name)
                
        except Exception as e:
            self.logger.error(f"Error converting to XML: {str(e)}")
            return f"<error>{str(e)}</error>"
    
    def to_html(self, data, table_id='data-table', classes='table table-striped'):
        """
        Convert DataFrame to HTML table format
        """
        try:
            if isinstance(data, pd.DataFrame):
                return data.to_html(table_id=table_id, classes=classes, escape=False, index=False)
            else:
                # Convert to DataFrame first
                df = pd.DataFrame(data)
                return df.to_html(table_id=table_id, classes=classes, escape=False, index=False)
                
        except Exception as e:
            self.logger.error(f"Error converting to HTML: {str(e)}")
            return f"<p>Error: {str(e)}</p>"
    
    def create_export_package(self, data_dict, format_type='mixed'):
        """
        Create a zip package with multiple export formats
        """
        try:
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                for name, data in data_dict.items():
                    if isinstance(data, pd.DataFrame) and not data.empty:
                        # Add CSV file
                        csv_data = self.to_csv(data)
                        zip_file.writestr(f"{name}_{timestamp}.csv", csv_data)
                        
                        # Add JSON file
                        json_data = self.to_json(data)
                        zip_file.writestr(f"{name}_{timestamp}.json", json_data)
                        
                        # Add Excel file if format allows
                        if format_type in ['mixed', 'excel']:
                            excel_data = self.to_excel(data)
                            zip_file.writestr(f"{name}_{timestamp}.xlsx", excel_data)
                
                # Add metadata file
                metadata = {
                    'export_timestamp': datetime.now().isoformat(),
                    'export_format': format_type,
                    'files_included': list(data_dict.keys()),
                    'total_files': len(data_dict)
                }
                
                zip_file.writestr(f"metadata_{timestamp}.json", 
                                json.dumps(metadata, indent=2))
            
            return zip_buffer.getvalue()
            
        except Exception as e:
            self.logger.error(f"Error creating export package: {str(e)}")
            return None
    
    def validate_data_for_export(self, data):
        """
        Validate data before export
        """
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'info': {}
        }
        
        try:
            if isinstance(data, pd.DataFrame):
                # Check for empty DataFrame
                if data.empty:
                    validation_result['warnings'].append('DataFrame is empty')
                
                # Check for very large datasets
                if len(data) > 100000:
                    validation_result['warnings'].append(f'Large dataset ({len(data)} rows) - export may take time')
                
                # Check for problematic column names
                problematic_columns = []
                for col in data.columns:
                    if not isinstance(col, str):
                        problematic_columns.append(col)
                    elif any(char in col for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
                        problematic_columns.append(col)
                
                if problematic_columns:
                    validation_result['warnings'].append(f'Problematic column names: {problematic_columns}')
                
                # Check for mixed data types
                mixed_type_columns = []
                for col in data.columns:
                    if data[col].apply(type).nunique() > 1:
                        mixed_type_columns.append(col)
                
                if mixed_type_columns:
                    validation_result['warnings'].append(f'Columns with mixed data types: {mixed_type_columns}')
                
                # Add basic info
                validation_result['info'] = {
                    'rows': len(data),
                    'columns': len(data.columns),
                    'memory_usage_mb': data.memory_usage(deep=True).sum() / 1024 / 1024,
                    'null_values': data.isnull().sum().sum()
                }
                
            else:
                validation_result['warnings'].append('Data is not a pandas DataFrame - will attempt conversion')
            
            return validation_result
            
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f'Validation error: {str(e)}')
            return validation_result
    
    def optimize_for_export(self, data, max_rows=None, max_memory_mb=None):
        """
        Optimize DataFrame for export
        """
        try:
            if not isinstance(data, pd.DataFrame):
                return data
            
            optimized_data = data.copy()
            
            # Limit rows if specified
            if max_rows and len(optimized_data) > max_rows:
                optimized_data = optimized_data.head(max_rows)
                self.logger.info(f"Truncated data to {max_rows} rows for export")
            
            # Check memory usage
            if max_memory_mb:
                memory_usage_mb = optimized_data.memory_usage(deep=True).sum() / 1024 / 1024
                if memory_usage_mb > max_memory_mb:
                    # Calculate rows to keep within memory limit
                    rows_to_keep = int(len(optimized_data) * (max_memory_mb / memory_usage_mb))
                    optimized_data = optimized_data.head(rows_to_keep)
                    self.logger.info(f"Reduced data to {rows_to_keep} rows to stay within memory limit")
            
            # Optimize data types
            for col in optimized_data.columns:
                if optimized_data[col].dtype == 'object':
                    # Try to convert to more efficient types
                    try:
                        # Try numeric conversion
                        converted = pd.to_numeric(optimized_data[col], errors='ignore')
                        if not converted.equals(optimized_data[col]):
                            optimized_data[col] = converted
                    except:
                        pass
            
            return optimized_data
            
        except Exception as e:
            self.logger.error(f"Error optimizing data for export: {str(e)}")
            return data
    
    def get_export_summary(self, data):
        """
        Get summary information about export data
        """
        try:
            if isinstance(data, pd.DataFrame):
                summary = {
                    'total_rows': len(data),
                    'total_columns': len(data.columns),
                    'memory_usage_mb': round(data.memory_usage(deep=True).sum() / 1024 / 1024, 2),
                    'estimated_csv_size_mb': round(len(self.to_csv(data)) / 1024 / 1024, 2),
                    'column_types': data.dtypes.value_counts().to_dict(),
                    'null_values': data.isnull().sum().sum(),
                    'duplicate_rows': data.duplicated().sum()
                }
                
                return summary
            else:
                return {'error': 'Data is not a pandas DataFrame'}
                
        except Exception as e:
            return {'error': str(e)}
