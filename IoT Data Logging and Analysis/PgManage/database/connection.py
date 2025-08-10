import psycopg2
import psycopg2.extras
import streamlit as st
from typing import List, Dict, Any, Optional
import pandas as pd

class DatabaseConnection:
    """Handles PostgreSQL database connections and operations"""
    
    def __init__(self, host: str, port: str, user: str, password: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connection = None
        self.current_database = None
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database='postgres'  # Connect to default postgres database
            )
            conn.close()
            return True
        except Exception as e:
            st.error(f"Connection failed: {str(e)}")
            return False
    
    def get_databases(self) -> List[str]:
        """Get list of available databases"""
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database='postgres'
            )
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT datname FROM pg_database 
                WHERE datistemplate = false 
                ORDER BY datname
            """)
            
            databases = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            
            return databases
        except Exception as e:
            st.error(f"Error fetching databases: {str(e)}")
            return []
    
    def connect_to_database(self, database: str) -> bool:
        """Connect to specific database"""
        try:
            if self.connection:
                self.connection.close()
            
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=database
            )
            self.current_database = database
            return True
        except Exception as e:
            st.error(f"Error connecting to database {database}: {str(e)}")
            return False
    
    def execute_query(self, query: str, fetch: bool = True) -> Optional[pd.DataFrame]:
        """Execute SQL query and return results as DataFrame"""
        try:
            if not self.connection:
                raise Exception("No database connection")
            
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query)
            
            if fetch and cursor.description:
                results = cursor.fetchall()
                df = pd.DataFrame(results)
                cursor.close()
                return df
            else:
                self.connection.commit()
                cursor.close()
                return None
                
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            raise e
    
    def execute_query_raw(self, query: str) -> List[Dict[str, Any]]:
        """Execute query and return raw results"""
        try:
            if not self.connection:
                raise Exception("No database connection")
            
            cursor = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query)
            
            if cursor.description:
                results = cursor.fetchall()
                cursor.close()
                return [dict(row) for row in results]
            else:
                self.connection.commit()
                cursor.close()
                return []
                
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            raise e
    
    def get_table_info(self) -> pd.DataFrame:
        """Get information about all tables in current database"""
        query = """
        SELECT 
            schemaname,
            tablename,
            tableowner,
            hasindexes,
            hasrules,
            hastriggers
        FROM pg_tables 
        WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
        ORDER BY schemaname, tablename
        """
        return self.execute_query(query)
    
    def get_table_row_count(self, schema: str, table: str) -> int:
        """Get row count for specific table"""
        try:
            query = f'SELECT COUNT(*) FROM "{schema}"."{table}"'
            result = self.execute_query(query)
            return result.iloc[0, 0] if not result.empty else 0
        except:
            return 0
    
    def get_database_size(self) -> str:
        """Get current database size"""
        query = f"SELECT pg_size_pretty(pg_database_size('{self.current_database}'))"
        result = self.execute_query(query)
        return result.iloc[0, 0] if not result.empty else "Unknown"
    
    def get_active_connections(self) -> int:
        """Get number of active connections"""
        query = f"""
        SELECT COUNT(*) 
        FROM pg_stat_activity 
        WHERE datname = '{self.current_database}'
        """
        result = self.execute_query(query)
        return result.iloc[0, 0] if not result.empty else 0
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
