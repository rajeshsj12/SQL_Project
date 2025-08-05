import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, text, inspect
import pymysql
import logging

class DatabaseManager:
    def __init__(self, connection_string_base):
        """
        Initialize database manager with base connection string
        Format: mysql+pymysql://user:password@host:port/
        """
        self.connection_string_base = connection_string_base
        self.engine = None
        self.current_database = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_databases(self):
        """Get list of available databases"""
        try:
            # Connect without specifying database
            engine = create_engine(self.connection_string_base + "information_schema")
            
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    WHERE schema_name NOT IN ('information_schema', 'performance_schema', 'mysql', 'sys')
                    ORDER BY schema_name
                """))
                databases = [row[0] for row in result]
                
            engine.dispose()
            return databases
            
        except Exception as e:
            self.logger.error(f"Error getting databases: {str(e)}")
            raise e
    
    def connect_to_database(self, database_name):
        """Connect to specific database"""
        try:
            if self.engine:
                self.engine.dispose()
            
            connection_string = self.connection_string_base + database_name
            self.engine = create_engine(connection_string, pool_pre_ping=True)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.current_database = database_name
            self.logger.info(f"Connected to database: {database_name}")
            
        except Exception as e:
            self.logger.error(f"Error connecting to database {database_name}: {str(e)}")
            raise e
    
    def get_tables(self):
        """Get list of tables in current database"""
        try:
            inspector = inspect(self.engine)
            return inspector.get_table_names()
        except Exception as e:
            self.logger.error(f"Error getting tables: {str(e)}")
            return []
    
    def get_views(self):
        """Get list of views in current database"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.views 
                    WHERE table_schema = :db_name
                    ORDER BY table_name
                """), {"db_name": self.current_database})
                return [row[0] for row in result]
        except Exception as e:
            self.logger.error(f"Error getting views: {str(e)}")
            return []
    
    def get_procedures(self):
        """Get list of stored procedures"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT routine_name 
                    FROM information_schema.routines 
                    WHERE routine_schema = :db_name 
                    AND routine_type = 'PROCEDURE'
                    ORDER BY routine_name
                """), {"db_name": self.current_database})
                return [row[0] for row in result]
        except Exception as e:
            self.logger.error(f"Error getting procedures: {str(e)}")
            return []
    
    def get_functions(self):
        """Get list of functions"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT routine_name 
                    FROM information_schema.routines 
                    WHERE routine_schema = :db_name 
                    AND routine_type = 'FUNCTION'
                    ORDER BY routine_name
                """), {"db_name": self.current_database})
                return [row[0] for row in result]
        except Exception as e:
            self.logger.error(f"Error getting functions: {str(e)}")
            return []
    
    def get_triggers(self):
        """Get list of triggers"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT trigger_name 
                    FROM information_schema.triggers 
                    WHERE trigger_schema = :db_name
                    ORDER BY trigger_name
                """), {"db_name": self.current_database})
                return [row[0] for row in result]
        except Exception as e:
            self.logger.error(f"Error getting triggers: {str(e)}")
            return []
    
    def get_table_data(self, table_name, limit=100, page=1, search_term=None):
        """Get data from a table with pagination and search"""
        try:
            offset = (page - 1) * limit
            
            query = f"SELECT * FROM `{table_name}`"
            params = {}
            
            if search_term:
                # Get column names for search
                inspector = inspect(self.engine)
                columns = inspector.get_columns(table_name)
                text_columns = [col['name'] for col in columns 
                              if col['type'].python_type in (str, bytes)]
                
                if text_columns:
                    search_conditions = []
                    for col in text_columns:
                        search_conditions.append(f"`{col}` LIKE :search_term")
                    
                    query += " WHERE " + " OR ".join(search_conditions)
                    params['search_term'] = f"%{search_term}%"
            
            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"
            
            return pd.read_sql(query, self.engine, params=params)
            
        except Exception as e:
            self.logger.error(f"Error getting table data: {str(e)}")
            return pd.DataFrame()
    
    def get_table_schema(self, table_name):
        """Get table schema information"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default,
                        column_key,
                        extra,
                        column_comment
                    FROM information_schema.columns 
                    WHERE table_schema = :db_name 
                    AND table_name = :table_name
                    ORDER BY ordinal_position
                """), {"db_name": self.current_database, "table_name": table_name})
                
                columns = ['Column', 'Type', 'Nullable', 'Default', 'Key', 'Extra', 'Comment']
                data = [list(row) for row in result]
                
                return pd.DataFrame(data, columns=columns)
                
        except Exception as e:
            self.logger.error(f"Error getting table schema: {str(e)}")
            return pd.DataFrame()
    
    def get_table_info(self, table_name):
        """Get general table information"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        table_rows,
                        data_length,
                        index_length,
                        table_collation,
                        create_time,
                        update_time,
                        table_comment
                    FROM information_schema.tables 
                    WHERE table_schema = :db_name 
                    AND table_name = :table_name
                """), {"db_name": self.current_database, "table_name": table_name})
                
                row = result.fetchone()
                if row:
                    return {
                        'Estimated Rows': row[0] or 'Unknown',
                        'Data Size (bytes)': row[1] or 'Unknown',
                        'Index Size (bytes)': row[2] or 'Unknown',
                        'Collation': row[3] or 'Unknown',
                        'Created': row[4] or 'Unknown',
                        'Updated': row[5] or 'Unknown',
                        'Comment': row[6] or 'None'
                    }
                
        except Exception as e:
            self.logger.error(f"Error getting table info: {str(e)}")
            return {}
    
    def get_table_row_count(self, table_name):
        """Get exact row count for a table"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM `{table_name}`"))
                return result.scalar()
        except Exception as e:
            self.logger.error(f"Error getting row count: {str(e)}")
            return 0
    
    def get_table_sizes(self):
        """Get size information for all tables"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        table_name,
                        ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
                    FROM information_schema.tables 
                    WHERE table_schema = :db_name 
                    AND table_type = 'BASE TABLE'
                    ORDER BY size_mb DESC
                """), {"db_name": self.current_database})
                
                data = []
                for row in result:
                    data.append({'table_name': row[0], 'size_mb': row[1] or 0})
                
                return pd.DataFrame(data)
                
        except Exception as e:
            self.logger.error(f"Error getting table sizes: {str(e)}")
            return pd.DataFrame()
    
    def get_view_data(self, view_name):
        """Get data from a view"""
        try:
            return pd.read_sql(f"SELECT * FROM `{view_name}` LIMIT 100", self.engine)
        except Exception as e:
            self.logger.error(f"Error getting view data: {str(e)}")
            return pd.DataFrame()
    
    def get_view_definition(self, view_name):
        """Get view definition"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT view_definition 
                    FROM information_schema.views 
                    WHERE table_schema = :db_name 
                    AND table_name = :view_name
                """), {"db_name": self.current_database, "view_name": view_name})
                
                row = result.fetchone()
                return row[0] if row else None
                
        except Exception as e:
            self.logger.error(f"Error getting view definition: {str(e)}")
            return None
    
    def get_procedure_definition(self, procedure_name):
        """Get stored procedure definition"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT routine_definition 
                    FROM information_schema.routines 
                    WHERE routine_schema = :db_name 
                    AND routine_name = :procedure_name
                    AND routine_type = 'PROCEDURE'
                """), {"db_name": self.current_database, "procedure_name": procedure_name})
                
                row = result.fetchone()
                return row[0] if row else None
                
        except Exception as e:
            self.logger.error(f"Error getting procedure definition: {str(e)}")
            return None
    
    def get_function_definition(self, function_name):
        """Get function definition"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT routine_definition 
                    FROM information_schema.routines 
                    WHERE routine_schema = :db_name 
                    AND routine_name = :function_name
                    AND routine_type = 'FUNCTION'
                """), {"db_name": self.current_database, "function_name": function_name})
                
                row = result.fetchone()
                return row[0] if row else None
                
        except Exception as e:
            self.logger.error(f"Error getting function definition: {str(e)}")
            return None
    
    def get_trigger_definition(self, trigger_name):
        """Get trigger definition"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT action_statement 
                    FROM information_schema.triggers 
                    WHERE trigger_schema = :db_name 
                    AND trigger_name = :trigger_name
                """), {"db_name": self.current_database, "trigger_name": trigger_name})
                
                row = result.fetchone()
                return row[0] if row else None
                
        except Exception as e:
            self.logger.error(f"Error getting trigger definition: {str(e)}")
            return None
    
    def get_procedure_parameters(self, procedure_name):
        """Get parameters for a stored procedure"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT 
                        parameter_name,
                        data_type,
                        parameter_mode,
                        ordinal_position
                    FROM information_schema.parameters 
                    WHERE specific_schema = :db_name 
                    AND specific_name = :procedure_name
                    ORDER BY ordinal_position
                """), {"db_name": self.current_database, "procedure_name": procedure_name})
                
                return [dict(row._mapping) for row in result]
        except Exception as e:
            self.logger.error(f"Error getting procedure parameters: {str(e)}")
            return []
    
    def execute_procedure(self, procedure_name, params=None):
        """Execute a stored procedure"""
        try:
            with self.engine.connect() as conn:
                if params:
                    # Filter out empty parameters
                    filtered_params = [p for p in params if p is not None and p != '']
                    if filtered_params:
                        param_str = ', '.join(['%s'] * len(filtered_params))
                        query = f"CALL {procedure_name}({param_str})"
                        result = conn.execute(text(query), filtered_params)
                    else:
                        result = conn.execute(text(f"CALL {procedure_name}()"))
                else:
                    result = conn.execute(text(f"CALL {procedure_name}()"))
                
                # Try to fetch results if available
                try:
                    return pd.DataFrame(result.fetchall(), columns=result.keys())
                except:
                    return pd.DataFrame()
                    
        except Exception as e:
            self.logger.error(f"Error executing procedure: {str(e)}")
            raise e
    
    def execute_query(self, query):
        """Execute custom SQL query"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                
                # Check if query returns results
                try:
                    return pd.DataFrame(result.fetchall(), columns=result.keys())
                except:
                    return pd.DataFrame()
                    
        except Exception as e:
            self.logger.error(f"Error executing query: {str(e)}")
            raise e
    
    def close_connection(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            self.logger.info("Database connection closed")
