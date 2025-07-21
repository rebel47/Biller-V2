import streamlit as st
import pandas as pd
import plotly.express as px
from database import FirebaseHandler
from ui_components import render_header

def analytics_page():
    """Analytics and insights page"""
    render_header("📊 Analytics", "Insights into your spending patterns")
    
    try:
        username = st.session_state["username"]
        db = FirebaseHandler()
        bills_df = db.get_bills(username)
        
        if not bills_df.empty:
            bills_df['date'] = pd.to_datetime(bills_df['date'])
            bills_df['month'] = bills_df['date'].dt.strftime('%Y-%m')
            
            # Create visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                render_monthly_chart(bills_df)
            
            with col2:
                render_category_chart(bills_df)
            
            # Spending trends
            st.markdown("### 📈 Spending Trends")
            render_spending_trends(bills_df)
            
            # Additional insights
            col1, col2 = st.columns(2)
            
            with col1:
                render_weekly_pattern(bills_df)
            
            with col2:
                render_top_expenses(bills_df)
            
        else:
            st.info("📊 No data available for analytics. Add some bills first!")
            
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

@st.fragment
def render_monthly_chart(df):
    """Render monthly spending chart"""
    monthly_data = df.groupby('month')['amount'].sum().reset_index()
    monthly_data = monthly_data.sort_values('month').tail(12)  # Last 12 months
    
    fig = px.bar(
        monthly_data,
        x='month',
        y='amount',
        title='📅 Monthly Spending',
        color='amount',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Month",
        yaxis_title="Amount (€)"
    )
    
    st.plotly_chart(fig, use_container_width=True)

@st.fragment
def render_category_chart(df):
    """Render category breakdown chart"""
    category_data = df.groupby('category')['amount'].sum().reset_index()
    
    fig = px.pie(
        category_data,
        values='amount',
        names='category',
        title='🏷️ Spending by Category'
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

@st.fragment
def render_spending_trends(df):
    """Render daily spending trends"""
    daily_spending = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
    daily_spending.columns = ['date', 'amount']
    
    fig = px.line(
        daily_spending,
        x='date',
        y='amount',
        title='Daily Spending Trend'
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Amount (€)"
    )
    
    st.plotly_chart(fig, use_container_width=True)

@st.fragment
def render_weekly_pattern(df):
    """Render weekly spending pattern"""
    df['day_of_week'] = df['date'].dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    weekly_data = df.groupby('day_of_week')['amount'].mean().reindex(day_order).reset_index()
    weekly_data.columns = ['day', 'avg_amount']
    
    fig = px.bar(
        weekly_data,
        x='day',
        y='avg_amount',
        title='📅 Average Spending by Day of Week',
        color='avg_amount',
        color_continuous_scale='Greens'
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Day of Week",
        yaxis_title="Average Amount (€)"
    )
    
    st.plotly_chart(fig, use_container_width=True)

@st.fragment
def render_top_expenses(df):
    """Render top expenses"""
    top_expenses = df.nlargest(10, 'amount')[['description', 'amount', 'date', 'category']]
    
    st.markdown("### 💸 Top 10 Expenses")
    
    for idx, expense in top_expenses.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.write(f"**{expense['description'][:40]}{'...' if len(expense['description']) > 40 else ''}**")
            
            with col2:
                st.write(f"€{expense['amount']:.2f}")
            
            with col3:
                st.write(expense['category'].title())
            
            with col4:
                st.write(expense['date'].strftime('%Y-%m-%d'))
            
            st.markdown("---")