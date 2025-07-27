import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import DatabaseConnection
from utils import (format_number, identify_column_types, create_distribution_chart, 
                  create_correlation_matrix, create_time_series_chart)

st.set_page_config(
    page_title="Analytics - Database Explorer",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("📊 Data Analytics Dashboard")
    st.markdown("Explore your data with interactive charts and visualizations")
    
    # Initialize database
    @st.cache_resource
    def init_database():
        return DatabaseConnection()
    
    db = init_database()
    
    if not db.test_connection():
        st.error("❌ Database connection failed")
        return
    
    # Get all tables
    tables = db.get_all_tables()
    
    if not tables:
        st.error("No tables found")
        return
    
    # Sidebar controls
    st.sidebar.title("Analytics Controls")
    selected_table = st.sidebar.selectbox("Select Table:", tables)
    
    if not selected_table:
        st.info("Please select a table from the sidebar")
        return
    
    # Load data
    @st.cache_data
    def load_table_data(table_name):
        return db.get_table_data(table_name, limit=5000)  # Limit for performance
    
    df = load_table_data(selected_table)
    
    if df.empty:
        st.warning(f"No data found in table '{selected_table}'")
        return
    
    # Table overview
    st.header(f"Analytics for: {selected_table}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Records Analyzed", format_number(len(df)))
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        null_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
        st.metric("Data Completeness", f"{100-null_percentage:.1f}%")
    with col4:
        memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024
        st.metric("Memory Usage", f"{memory_usage:.1f} MB")
    
    # Identify column types
    column_types = identify_column_types(df)
    
    # Chart type selection
    st.sidebar.markdown("---")
    st.sidebar.subheader("Visualization Options")
    
    chart_types = [
        "Overview Dashboard",
        "Distribution Analysis", 
        "Correlation Analysis",
        "Time Series Analysis",
        "Categorical Analysis",
        "Custom Charts"
    ]
    
    selected_chart_type = st.sidebar.selectbox("Chart Type:", chart_types)
    
    # Main analytics content
    if selected_chart_type == "Overview Dashboard":
        show_overview_dashboard(df, column_types, selected_table, db)
    elif selected_chart_type == "Distribution Analysis":
        show_distribution_analysis(df, column_types)
    elif selected_chart_type == "Correlation Analysis":
        show_correlation_analysis(df, column_types)
    elif selected_chart_type == "Time Series Analysis":
        show_time_series_analysis(df, column_types)
    elif selected_chart_type == "Categorical Analysis":
        show_categorical_analysis(df, column_types)
    elif selected_chart_type == "Custom Charts":
        show_custom_charts(df, column_types)

def show_overview_dashboard(df, column_types, table_name, db):
    """Show general overview dashboard"""
    st.subheader("📈 Overview Dashboard")
    
    # Key metrics based on table type
    if table_name == 'customers':
        show_customer_dashboard(df, db)
    elif table_name == 'orders':
        show_orders_dashboard(df, db)
    elif table_name == 'products':
        show_products_dashboard(df, db)
    elif table_name == 'employees':
        show_employees_dashboard(df, db)
    else:
        show_generic_dashboard(df, column_types)

def show_customer_dashboard(df, db):
    """Customer-specific dashboard"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Gender distribution
        if 'gender' in df.columns:
            gender_counts = df['gender'].value_counts()
            fig = px.pie(values=gender_counts.values, names=gender_counts.index, 
                        title="Customer Gender Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Age distribution
        if 'age' in df.columns:
            fig = px.histogram(df, x='age', title="Customer Age Distribution", 
                             nbins=20)
            st.plotly_chart(fig, use_container_width=True)
    
    # Geographic distribution
    if 'country' in df.columns:
        country_counts = df['country'].value_counts().head(10)
        fig = px.bar(x=country_counts.index, y=country_counts.values,
                    title="Top 10 Countries by Customer Count")
        fig.update_xaxis(title="Country")
        fig.update_yaxis(title="Customer Count")
        st.plotly_chart(fig, use_container_width=True)
    
    # Registration trend
    if 'registration_date' in df.columns:
        df['registration_date'] = pd.to_datetime(df['registration_date'])
        daily_registrations = df.groupby(df['registration_date'].dt.date).size()
        fig = px.line(x=daily_registrations.index, y=daily_registrations.values,
                     title="Customer Registration Trend")
        fig.update_xaxis(title="Date")
        fig.update_yaxis(title="New Registrations")
        st.plotly_chart(fig, use_container_width=True)

def show_orders_dashboard(df, db):
    """Orders-specific dashboard"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Order amount distribution
        if 'total_amount' in df.columns:
            fig = px.histogram(df, x='total_amount', title="Order Amount Distribution",
                             nbins=30)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Order quantity distribution
        if 'total_qty' in df.columns:
            fig = px.histogram(df, x='total_qty', title="Order Quantity Distribution",
                             nbins=20)
            st.plotly_chart(fig, use_container_width=True)
    
    # Orders over time
    if 'order_date' in df.columns:
        df['order_date'] = pd.to_datetime(df['order_date'])
        daily_orders = df.groupby(df['order_date'].dt.date).agg({
            'order_id': 'count',
            'total_amount': 'sum'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_orders['order_date'], 
            y=daily_orders['order_id'],
            name='Order Count',
            yaxis='y'
        ))
        fig.add_trace(go.Scatter(
            x=daily_orders['order_date'], 
            y=daily_orders['total_amount'],
            name='Total Revenue',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Orders and Revenue Trend",
            xaxis_title="Date",
            yaxis=dict(title="Order Count", side="left"),
            yaxis2=dict(title="Revenue", side="right", overlaying="y")
        )
        st.plotly_chart(fig, use_container_width=True)

def show_products_dashboard(df, db):
    """Products-specific dashboard"""
    # Get category information
    categories_df = db.execute_query("SELECT category_id, category_name FROM category")
    if not categories_df.empty:
        category_map = dict(zip(categories_df['category_id'], categories_df['category_name']))
        df['category_name'] = df['category_id'].map(category_map)
        
        # Products by category
        category_counts = df['category_name'].value_counts()
        fig = px.pie(values=category_counts.values, names=category_counts.index,
                    title="Products by Category")
        st.plotly_chart(fig, use_container_width=True)

def show_employees_dashboard(df, db):
    """Employees-specific dashboard"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Age distribution
        if 'age' in df.columns:
            fig = px.histogram(df, x='age', title="Employee Age Distribution",
                             nbins=15)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Role distribution
        if 'role' in df.columns:
            role_counts = df['role'].value_counts()
            fig = px.bar(x=role_counts.index, y=role_counts.values,
                        title="Employees by Role")
            fig.update_xaxis(title="Role")
            fig.update_yaxis(title="Employee Count")
            st.plotly_chart(fig, use_container_width=True)

def show_generic_dashboard(df, column_types):
    """Generic dashboard for any table"""
    col1, col2 = st.columns(2)
    
    # Numeric columns summary
    if column_types['numeric']:
        with col1:
            numeric_col = st.selectbox("Select numeric column:", column_types['numeric'])
            if numeric_col:
                fig = px.histogram(df, x=numeric_col, title=f"Distribution of {numeric_col}")
                st.plotly_chart(fig, use_container_width=True)
    
    # Categorical columns summary
    if column_types['categorical']:
        with col2:
            cat_col = st.selectbox("Select categorical column:", column_types['categorical'])
            if cat_col:
                value_counts = df[cat_col].value_counts().head(10)
                fig = px.bar(x=value_counts.index, y=value_counts.values,
                            title=f"Top Values in {cat_col}")
                st.plotly_chart(fig, use_container_width=True)

def show_distribution_analysis(df, column_types):
    """Show distribution analysis"""
    st.subheader("📊 Distribution Analysis")
    
    if not column_types['numeric']:
        st.warning("No numeric columns found for distribution analysis")
        return
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        selected_column = st.selectbox("Select column:", column_types['numeric'])
        chart_type = st.selectbox("Chart type:", ['Histogram', 'Box Plot', 'Violin Plot'])
    
    with col2:
        if selected_column:
            if chart_type == 'Histogram':
                fig = px.histogram(df, x=selected_column, title=f'Distribution of {selected_column}')
            elif chart_type == 'Box Plot':
                fig = px.box(df, y=selected_column, title=f'Box Plot of {selected_column}')
            else:
                fig = px.violin(df, y=selected_column, title=f'Violin Plot of {selected_column}')
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show statistics
            stats = df[selected_column].describe()
            st.write("**Statistics:**")
            st.write(stats)

def show_correlation_analysis(df, column_types):
    """Show correlation analysis"""
    st.subheader("🔗 Correlation Analysis")
    
    if len(column_types['numeric']) < 2:
        st.warning("Need at least 2 numeric columns for correlation analysis")
        return
    
    numeric_df = df[column_types['numeric']].select_dtypes(include=['number'])
    correlation_matrix = numeric_df.corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=correlation_matrix.round(2).values,
        texttemplate="%{text}",
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title='Correlation Matrix',
        xaxis_tickangle=-45,
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show strongest correlations
    st.subheader("Strongest Correlations")
    corr_pairs = []
    for i in range(len(correlation_matrix.columns)):
        for j in range(i+1, len(correlation_matrix.columns)):
            corr_pairs.append({
                'Variable 1': correlation_matrix.columns[i],
                'Variable 2': correlation_matrix.columns[j],
                'Correlation': correlation_matrix.iloc[i, j]
            })
    
    corr_df = pd.DataFrame(corr_pairs)
    corr_df = corr_df.reindex(corr_df['Correlation'].abs().sort_values(ascending=False).index)
    st.dataframe(corr_df.head(10), use_container_width=True)

def show_time_series_analysis(df, column_types):
    """Show time series analysis"""
    st.subheader("📅 Time Series Analysis")
    
    if not column_types['datetime']:
        st.warning("No datetime columns found for time series analysis")
        return
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        date_column = st.selectbox("Select date column:", column_types['datetime'])
        
        if column_types['numeric']:
            value_column = st.selectbox("Select value column (optional):", 
                                      ['Record Count'] + column_types['numeric'])
        else:
            value_column = 'Record Count'
    
    with col2:
        if date_column:
            # Convert to datetime
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            df_clean = df.dropna(subset=[date_column])
            
            if value_column == 'Record Count':
                # Count records over time
                time_series = df_clean.groupby(df_clean[date_column].dt.date).size().reset_index()
                time_series.columns = [date_column, 'count']
                
                fig = px.line(time_series, x=date_column, y='count',
                             title=f'Record Count over Time')
            else:
                # Value over time
                time_series = df_clean.groupby(df_clean[date_column].dt.date)[value_column].sum().reset_index()
                
                fig = px.line(time_series, x=date_column, y=value_column,
                             title=f'{value_column} over Time')
            
            st.plotly_chart(fig, use_container_width=True)

def show_categorical_analysis(df, column_types):
    """Show categorical analysis"""
    st.subheader("📊 Categorical Analysis")
    
    if not column_types['categorical']:
        st.warning("No categorical columns found")
        return
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        selected_column = st.selectbox("Select categorical column:", column_types['categorical'])
        chart_type = st.selectbox("Chart type:", ['Bar Chart', 'Pie Chart', 'Donut Chart'])
        top_n = st.slider("Show top N categories:", 5, 20, 10)
    
    with col2:
        if selected_column:
            value_counts = df[selected_column].value_counts().head(top_n)
            
            if chart_type == 'Bar Chart':
                fig = px.bar(x=value_counts.index, y=value_counts.values,
                            title=f'Top {top_n} values in {selected_column}')
                fig.update_xaxis(title=selected_column)
                fig.update_yaxis(title='Count')
            elif chart_type == 'Pie Chart':
                fig = px.pie(values=value_counts.values, names=value_counts.index,
                            title=f'Distribution of {selected_column}')
            else:  # Donut Chart
                fig = px.pie(values=value_counts.values, names=value_counts.index,
                            title=f'Distribution of {selected_column}', hole=0.4)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show statistics
            st.write(f"**Unique values:** {df[selected_column].nunique()}")
            st.write(f"**Most common:** {value_counts.index[0]} ({value_counts.iloc[0]} occurrences)")

def show_custom_charts(df, column_types):
    """Show custom chart builder"""
    st.subheader("🎨 Custom Chart Builder")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        chart_type = st.selectbox("Chart type:", 
                                 ['Scatter Plot', 'Line Chart', 'Bar Chart', 'Heatmap'])
        
        all_columns = list(df.columns)
        
        x_column = st.selectbox("X-axis:", all_columns)
        y_column = st.selectbox("Y-axis:", all_columns)
        
        if column_types['categorical']:
            color_column = st.selectbox("Color by (optional):", 
                                      ['None'] + column_types['categorical'])
        else:
            color_column = 'None'
    
    with col2:
        if x_column and y_column:
            color_col = None if color_column == 'None' else color_column
            
            if chart_type == 'Scatter Plot':
                fig = px.scatter(df, x=x_column, y=y_column, color=color_col,
                               title=f'{y_column} vs {x_column}')
            elif chart_type == 'Line Chart':
                fig = px.line(df, x=x_column, y=y_column, color=color_col,
                             title=f'{y_column} vs {x_column}')
            elif chart_type == 'Bar Chart':
                if color_col:
                    fig = px.bar(df, x=x_column, y=y_column, color=color_col,
                               title=f'{y_column} by {x_column}')
                else:
                    # Group by x_column and aggregate y_column
                    grouped = df.groupby(x_column)[y_column].mean().reset_index()
                    fig = px.bar(grouped, x=x_column, y=y_column,
                               title=f'Average {y_column} by {x_column}')
            
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
