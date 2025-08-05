import time
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import text
import logging

class QueryExecutor:
    def __init__(self, database_manager):
        """
        Initialize query executor with database manager
        """
        self.db_manager = database_manager
        self.logger = logging.getLogger(__name__)
    
    def execute_query(self, query):
        """
        Execute SQL query and return results with execution time
        """
        start_time = time.time()
        
        try:
            # Clean and validate query
            query = query.strip()
            if not query:
                return {
                    'success': False,
                    'error': 'Empty query provided',
                    'data': None,
                    'execution_time': 0
                }
            
            # Check for dangerous operations (basic protection)
            dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE']
            query_upper = query.upper()
            
            contains_dangerous = any(keyword in query_upper for keyword in dangerous_keywords)
            if contains_dangerous:
                # Ask for confirmation in a real app - for now, we'll allow with warning
                self.logger.warning(f"Potentially dangerous query detected: {query[:100]}...")
            
            # Execute query
            with self.db_manager.engine.connect() as conn:
                result = conn.execute(text(query))
                
                # Try to fetch results
                try:
                    columns = result.keys()
                    data = result.fetchall()
                    df = pd.DataFrame(data, columns=columns)
                except Exception:
                    # Query might not return results (INSERT, UPDATE, etc.)
                    df = pd.DataFrame()
                
                execution_time = time.time() - start_time
                
                return {
                    'success': True,
                    'error': None,
                    'data': df,
                    'execution_time': execution_time,
                    'rows_affected': result.rowcount if hasattr(result, 'rowcount') else len(df)
                }
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            self.logger.error(f"Query execution failed: {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'data': None,
                'execution_time': execution_time
            }
    
    def validate_query(self, query):
        """
        Validate SQL query syntax and safety
        """
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        try:
            query = query.strip()
            
            if not query:
                validation_result['is_valid'] = False
                validation_result['errors'].append('Empty query')
                return validation_result
            
            # Check for SQL injection patterns
            suspicious_patterns = [
                '; --',
                '/*',
                '*/',
                'UNION ALL',
                'UNION SELECT',
                'OR 1=1',
                'AND 1=1',
                "' OR '1'='1",
                '" OR "1"="1'
            ]
            
            query_upper = query.upper()
            for pattern in suspicious_patterns:
                if pattern.upper() in query_upper:
                    validation_result['warnings'].append(f'Suspicious pattern detected: {pattern}')
            
            # Check for potentially dangerous operations
            dangerous_operations = {
                'DROP': 'Drops database objects',
                'DELETE': 'Deletes data from tables',
                'TRUNCATE': 'Removes all rows from tables',
                'ALTER': 'Modifies database structure',
                'CREATE': 'Creates new database objects',
                'GRANT': 'Grants permissions',
                'REVOKE': 'Revokes permissions'
            }
            
            for operation, description in dangerous_operations.items():
                if operation in query_upper:
                    validation_result['warnings'].append(f'Dangerous operation detected - {operation}: {description}')
            
            # Basic syntax validation
            if query_upper.count('(') != query_upper.count(')'):
                validation_result['errors'].append('Unmatched parentheses')
            
            if query_upper.count("'") % 2 != 0:
                validation_result['warnings'].append('Unmatched single quotes detected')
            
            if query_upper.count('"') % 2 != 0:
                validation_result['warnings'].append('Unmatched double quotes detected')
            
            # Check for common MySQL keywords
            if not any(keyword in query_upper for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'SHOW', 'DESCRIBE', 'EXPLAIN', 'CALL']):
                validation_result['warnings'].append('Query does not contain common SQL keywords')
            
            if validation_result['errors']:
                validation_result['is_valid'] = False
            
            return validation_result
            
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f'Validation error: {str(e)}')
            return validation_result
    
    def get_query_plan(self, query):
        """
        Get execution plan for a query
        """
        try:
            explain_query = f"EXPLAIN {query}"
            result = self.execute_query(explain_query)
            
            if result['success']:
                return result['data']
            else:
                return pd.DataFrame({'Error': [result['error']]})
                
        except Exception as e:
            return pd.DataFrame({'Error': [str(e)]})
    
    def get_query_suggestions(self, partial_query):
        """
        Get suggestions for query completion
        """
        suggestions = []
        
        try:
            partial_upper = partial_query.upper().strip()
            
            # Basic keyword suggestions
            if not partial_upper:
                suggestions = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'SHOW', 'DESCRIBE', 'EXPLAIN']
            
            elif partial_upper.startswith('SELECT'):
                if 'FROM' not in partial_upper:
                    # Suggest table names
                    tables = self.db_manager.get_tables()
                    suggestions = [f"SELECT * FROM {table}" for table in tables[:10]]
                
            elif partial_upper.startswith('SHOW'):
                suggestions = [
                    'SHOW TABLES',
                    'SHOW DATABASES',
                    'SHOW COLUMNS FROM table_name',
                    'SHOW INDEX FROM table_name',
                    'SHOW CREATE TABLE table_name',
                    'SHOW PROCESSLIST',
                    'SHOW STATUS',
                    'SHOW VARIABLES'
                ]
            
            elif partial_upper.startswith('DESCRIBE') or partial_upper.startswith('DESC'):
                tables = self.db_manager.get_tables()
                suggestions = [f"DESCRIBE {table}" for table in tables[:10]]
            
            return suggestions[:10]  # Limit to 10 suggestions
            
        except Exception as e:
            self.logger.error(f"Error getting query suggestions: {str(e)}")
            return []
    
    def format_query(self, query):
        """
        Basic SQL query formatting
        """
        try:
            # Simple formatting rules
            keywords = [
                'SELECT', 'FROM', 'WHERE', 'JOIN', 'INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN',
                'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'INSERT', 'UPDATE', 'DELETE',
                'CREATE', 'ALTER', 'DROP', 'INDEX', 'TABLE', 'DATABASE', 'SCHEMA'
            ]
            
            formatted_query = query
            
            # Add newlines before major keywords
            for keyword in keywords:
                formatted_query = formatted_query.replace(f' {keyword} ', f'\n{keyword} ')
                formatted_query = formatted_query.replace(f' {keyword.lower()} ', f'\n{keyword} ')
            
            # Clean up extra whitespace
            lines = formatted_query.split('\n')
            cleaned_lines = []
            
            for line in lines:
                cleaned_line = ' '.join(line.split())  # Remove extra spaces
                if cleaned_line:
                    cleaned_lines.append(cleaned_line)
            
            return '\n'.join(cleaned_lines)
            
        except Exception as e:
            self.logger.error(f"Error formatting query: {str(e)}")
            return query
    
    def get_recent_queries(self):
        """
        Get recent queries from MySQL process list
        """
        try:
            recent_queries = self.execute_query("SHOW PROCESSLIST")
            
            if recent_queries['success']:
                return recent_queries['data']
            else:
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error getting recent queries: {str(e)}")
            return pd.DataFrame()
