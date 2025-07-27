import mysql.connector
import pandas as pd
import streamlit as st
import os
from typing import List, Dict, Any, Optional

class DatabaseConnection:
    """Handle MySQL database connections and operations"""
    
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '3306')),
            'database': os.getenv('DB_NAME', 'customersdb'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', 'password'),
            'charset': 'utf8mb4',
            'autocommit': True
        }
        self.connection = None
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            return True
        except mysql.connector.Error as e:
            st.error(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def test_connection(self) -> bool:
        """Test if database connection is working"""
        try:
            if not self.connect():
                return False
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception as e:
            st.error(f"Connection test failed: {e}")
            return False
        finally:
            self.disconnect()
    
    def execute_query(self, query: str, params: tuple = None) -> pd.DataFrame:
        """Execute a SELECT query and return results as DataFrame"""
        try:
            if not self.connect():
                return pd.DataFrame()
            
            df = pd.read_sql(query, self.connection, params=params)
            return df
        except Exception as e:
            st.error(f"Query execution error: {e}")
            return pd.DataFrame()
        finally:
            self.disconnect()
    
    def get_all_tables(self) -> List[str]:
        """Get list of all tables in the database"""
        query = "SHOW TABLES"
        df = self.execute_query(query)
        if df.empty:
            return []
        return df.iloc[:, 0].tolist()
    
    def get_table_data(self, table_name: str, limit: int = 1000, offset: int = 0) -> pd.DataFrame:
        """Get data from a specific table with pagination"""
        query = f"SELECT * FROM `{table_name}` LIMIT %s OFFSET %s"
        return self.execute_query(query, (limit, offset))
    
    def get_table_count(self, table_name: str) -> int:
        """Get total number of records in a table"""
        query = f"SELECT COUNT(*) as count FROM `{table_name}`"
        df = self.execute_query(query)
        return df.iloc[0, 0] if not df.empty else 0
    
    def get_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Get column information for a table"""
        query = f"DESCRIBE `{table_name}`"
        df = self.execute_query(query)
        if df.empty:
            return []
        
        columns = []
        for _, row in df.iterrows():
            columns.append({
                'Field': row['Field'],
                'Type': row['Type'],
                'Null': row['Null'],
                'Key': row['Key'],
                'Default': row['Default'],
                'Extra': row['Extra']
            })
        return columns
    
    def get_primary_key(self, table_name: str) -> str:
        """Get primary key column name for a table"""
        columns = self.get_table_columns(table_name)
        for col in columns:
            if col['Key'] == 'PRI':
                return col['Field']
        return 'N/A'
    
    def search_table(self, table_name: str, search_term: str, column: str = None) -> pd.DataFrame:
        """Search for records in a table"""
        if column:
            query = f"SELECT * FROM `{table_name}` WHERE `{column}` LIKE %s"
            return self.execute_query(query, (f"%{search_term}%",))
        else:
            # Search all text columns
            columns = self.get_table_columns(table_name)
            text_columns = [col['Field'] for col in columns if 'varchar' in col['Type'] or 'text' in col['Type']]
            
            if not text_columns:
                return pd.DataFrame()
            
            conditions = [f"`{col}` LIKE %s" for col in text_columns]
            query = f"SELECT * FROM `{table_name}` WHERE {' OR '.join(conditions)}"
            params = tuple([f"%{search_term}%"] * len(text_columns))
            return self.execute_query(query, params)
    
    def get_foreign_keys(self, table_name: str) -> List[Dict[str, str]]:
        """Get foreign key relationships for a table"""
        query = """
        SELECT 
            COLUMN_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = %s 
        AND TABLE_NAME = %s 
        AND REFERENCED_TABLE_NAME IS NOT NULL
        """
        df = self.execute_query(query, (self.config['database'], table_name))
        
        if df.empty:
            return []
        
        foreign_keys = []
        for _, row in df.iterrows():
            foreign_keys.append({
                'column': row['COLUMN_NAME'],
                'referenced_table': row['REFERENCED_TABLE_NAME'],
                'referenced_column': row['REFERENCED_COLUMN_NAME']
            })
        return foreign_keys
    
    def get_table_relationships(self) -> List[Dict[str, str]]:
        """Get all foreign key relationships in the database"""
        query = """
        SELECT 
            TABLE_NAME,
            COLUMN_NAME,
            REFERENCED_TABLE_NAME,
            REFERENCED_COLUMN_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = %s 
        AND REFERENCED_TABLE_NAME IS NOT NULL
        """
        df = self.execute_query(query, (self.config['database'],))
        
        if df.empty:
            return []
        
        relationships = []
        for _, row in df.iterrows():
            relationships.append({
                'from_table': row['TABLE_NAME'],
                'from_column': row['COLUMN_NAME'],
                'to_table': row['REFERENCED_TABLE_NAME'],
                'to_column': row['REFERENCED_COLUMN_NAME']
            })
        return relationships
    
    def get_column_stats(self, table_name: str, column_name: str) -> Dict[str, Any]:
        """Get statistics for a numeric column"""
        query = f"""
        SELECT 
            COUNT(*) as count,
            MIN(`{column_name}`) as min_val,
            MAX(`{column_name}`) as max_val,
            AVG(`{column_name}`) as avg_val,
            STDDEV(`{column_name}`) as std_val
        FROM `{table_name}`
        WHERE `{column_name}` IS NOT NULL
        """
        df = self.execute_query(query)
        if df.empty:
            return {}
        
        row = df.iloc[0]
        return {
            'count': int(row['count']),
            'min': float(row['min_val']) if row['min_val'] is not None else None,
            'max': float(row['max_val']) if row['max_val'] is not None else None,
            'avg': float(row['avg_val']) if row['avg_val'] is not None else None,
            'std': float(row['std_val']) if row['std_val'] is not None else None
        }
