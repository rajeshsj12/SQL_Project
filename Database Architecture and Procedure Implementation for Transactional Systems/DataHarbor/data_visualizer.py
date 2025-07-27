import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

class DataVisualizer:
    def __init__(self, data):
        """
        Initialize data visualizer with pandas DataFrame
        """
        self.data = data
    
    def create_bar_chart(self, x_column, y_column, title=None):
        """Create bar chart"""
        try:
            if title is None:
                title = f"{y_column} by {x_column}"
            
            # If y_column is numeric, aggregate data
            if pd.api.types.is_numeric_dtype(self.data[y_column]):
                chart_data = self.data.groupby(x_column)[y_column].sum().reset_index()
            else:
                # Count occurrences for non-numeric data
                chart_data = self.data.groupby(x_column).size().reset_index(name='count')
                y_column = 'count'
            
            fig = px.bar(
                chart_data, 
                x=x_column, 
                y=y_column, 
                title=title,
                labels={x_column: x_column.replace('_', ' ').title(),
                       y_column: y_column.replace('_', ' ').title()}
            )
            
            fig.update_layout(
                showlegend=False,
                xaxis_tickangle=-45,
                height=500
            )
            
            return fig
            
        except Exception as e:
            # Return error chart
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating bar chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
    
    def create_line_chart(self, x_column, y_column, title=None):
        """Create line chart"""
        try:
            if title is None:
                title = f"{y_column} over {x_column}"
            
            # Sort data by x_column for proper line chart
            sorted_data = self.data.sort_values(x_column)
            
            fig = px.line(
                sorted_data, 
                x=x_column, 
                y=y_column, 
                title=title,
                labels={x_column: x_column.replace('_', ' ').title(),
                       y_column: y_column.replace('_', ' ').title()}
            )
            
            fig.update_layout(height=500)
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating line chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
    
    def create_scatter_plot(self, x_column, y_column, color_column=None, title=None):
        """Create scatter plot"""
        try:
            if title is None:
                title = f"{y_column} vs {x_column}"
                if color_column:
                    title += f" (colored by {color_column})"
            
            fig = px.scatter(
                self.data, 
                x=x_column, 
                y=y_column, 
                color=color_column,
                title=title,
                labels={x_column: x_column.replace('_', ' ').title(),
                       y_column: y_column.replace('_', ' ').title()}
            )
            
            fig.update_layout(height=500)
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating scatter plot: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
    
    def create_histogram(self, column, bins=30, title=None):
        """Create histogram"""
        try:
            if title is None:
                title = f"Distribution of {column}"
            
            fig = px.histogram(
                self.data, 
                x=column, 
                nbins=bins,
                title=title,
                labels={column: column.replace('_', ' ').title()}
            )
            
            fig.update_layout(
                showlegend=False,
                height=500
            )
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating histogram: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
    
    def create_box_plot(self, column, title=None):
        """Create box plot"""
        try:
            if title is None:
                title = f"Box Plot of {column}"
            
            fig = px.box(
                self.data, 
                y=column,
                title=title,
                labels={column: column.replace('_', ' ').title()}
            )
            
            fig.update_layout(height=500)
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating box plot: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
    
    def create_pie_chart(self, column, title=None):
        """Create pie chart"""
        try:
            if title is None:
                title = f"Distribution of {column}"
            
            # Count values
            value_counts = self.data[column].value_counts()
            
            fig = px.pie(
                values=value_counts.values,
                names=value_counts.index,
                title=title
            )
            
            fig.update_layout(height=500)
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating pie chart: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
    
    def create_heatmap(self, x_column, y_column, value_column, title=None):
        """Create heatmap"""
        try:
            if title is None:
                title = f"Heatmap: {value_column} by {x_column} and {y_column}"
            
            # Create pivot table for heatmap
            pivot_data = self.data.pivot_table(
                values=value_column,
                index=y_column,
                columns=x_column,
                aggfunc='mean'  # Use mean for aggregation
            )
            
            fig = px.imshow(
                pivot_data,
                title=title,
                labels={
                    'x': x_column.replace('_', ' ').title(),
                    'y': y_column.replace('_', ' ').title(),
                    'color': value_column.replace('_', ' ').title()
                }
            )
            
            fig.update_layout(height=500)
            
            return fig
            
        except Exception as e:
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating heatmap: {str(e)}",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
    
    def get_data_summary(self):
        """Get summary statistics of the data"""
        try:
            summary = {
                'Total Rows': len(self.data),
                'Total Columns': len(self.data.columns),
                'Numeric Columns': len(self.data.select_dtypes(include=[np.number]).columns),
                'Text Columns': len(self.data.select_dtypes(include=['object', 'string']).columns),
                'Missing Values': self.data.isnull().sum().sum()
            }
            
            return summary
            
        except Exception as e:
            return {'Error': str(e)}
    
    def get_column_info(self):
        """Get information about each column"""
        try:
            info = []
            
            for col in self.data.columns:
                col_info = {
                    'Column': col,
                    'Type': str(self.data[col].dtype),
                    'Non-Null Count': self.data[col].count(),
                    'Null Count': self.data[col].isnull().sum(),
                    'Unique Values': self.data[col].nunique()
                }
                
                # Add additional stats for numeric columns
                if pd.api.types.is_numeric_dtype(self.data[col]):
                    col_info.update({
                        'Mean': self.data[col].mean(),
                        'Std': self.data[col].std(),
                        'Min': self.data[col].min(),
                        'Max': self.data[col].max()
                    })
                
                info.append(col_info)
            
            return pd.DataFrame(info)
            
        except Exception as e:
            return pd.DataFrame({'Error': [str(e)]})
