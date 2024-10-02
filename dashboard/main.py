import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import seaborn as sns
import streamlit as st
import urllib
from func import DataAnalyzer, BrazilMapPlotter
from babel.numbers import format_currency

# Set styles for seaborn and Streamlit
sns.set(style='white')

# Load and preprocess the dataset
datetime_cols = [
    "order_approved_at", 
    "order_delivered_carrier_date", 
    "order_delivered_customer_date", 
    "order_estimated_delivery_date", 
    "order_purchase_timestamp", 
    "shipping_limit_date"
]

# Load the main dataset
all_df = pd.read_csv('data/all_data.csv')
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(drop=True, inplace=True)

# Convert date columns to datetime
for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

# Load geolocation dataset
geolocation = pd.read_csv('data/geolocation.csv')
data = geolocation.drop_duplicates(subset='customer_unique_id')

# Get the date range
min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar configuration
with st.sidebar:
    st.title("Nicholas Febrian Liswanto")
    st.image("dashboard/logo.jpg")
    start_date, end_date = st.date_input(
        label="Select Date Range",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Filter the main dataframe based on date selection
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                 (all_df["order_approved_at"] <= str(end_date))]

# Data Analysis and Visualization
function = DataAnalyzer(main_df)
map_plot = BrazilMapPlotter(data, plt, mpimg, urllib, st)

# Create dataframes for analysis
daily_orders_df = function.create_daily_orders_df()
sum_order_items_df = function.create_sum_order_items_df()
review_score, common_score = function.review_score_df()
state, most_common_state = function.create_bystate_df()
order_status, common_status = function.create_order_status()

# Main Dashboard Title
st.title("E-Commerce Dashboard :shopping_bags:")

# --- Layout: Overview Section ---
st.markdown("## 📊 Overview")
col1, col2, col3 = st.columns(3)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.metric(label="Total Orders", value=f"{total_order}")

with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "IDR", locale="id_ID")
    st.metric(label="Total Revenue", value=f"{total_revenue}")

with col3:
    avg_review_score = review_score.mean()
    st.metric(label="Avg. Review Score", value=f"{avg_review_score:.2f}")

# --- Layout: Data Visualization Section ---
st.markdown("## 📈 Data Visualization")

# Tabs for different visualizations
tab1, tab2, tab3, tab4 = st.tabs(["Daily Orders", "Order Items", "Review Score", "Customer Demographics"])

# --- Tab 1: Daily Orders ---
with tab1:
    st.markdown("### 📅 Daily Orders")
    
    # Plotting Daily Orders
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        daily_orders_df["order_approved_at"],
        daily_orders_df["order_count"],
        marker="o",
        linewidth=2,
        color="#007BFF"
    )
    ax.tick_params(axis="x", rotation=45)
    ax.tick_params(axis="y", labelsize=15)
    st.pyplot(fig)

# --- Tab 2: Order Items ---
with tab2:
    st.markdown("### 📦 Order Items")
    
    # Split Order Items into 2 columns for better layout
    col1, col2 = st.columns(2)

    with col1:
        total_items = sum_order_items_df["product_count"].sum()
        st.metric(label="Total Items Sold", value=f"{total_items}")

    with col2:
        avg_items = sum_order_items_df["product_count"].mean()
        st.metric(label="Avg. Items per Order", value=f"{avg_items:.2f}")

    # Plotting Most and Least Sold Products
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))
    colors = ["#4C9F70", "#6AC08B", "#94D3AC", "#C2E6CF", "#E5F5E9"]

    # Most Sold Products
    sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.head(5), palette=colors, ax=ax[0])
    ax[0].set_title("Top 5 Most Sold Products")
    ax[0].tick_params(axis='y', labelsize=12)

    # Least Sold Products
    sns.barplot(x="product_count", y="product_category_name_english", data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), palette=colors, ax=ax[1])
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Top 5 Least Sold Products")
    
    st.pyplot(fig)

# --- Tab 3: Review Score ---
with tab3:
    st.markdown("### ⭐ Customer Review Score")
    
    # Most common review score
    most_common_review_score = review_score.value_counts().idxmax()
    st.markdown(f"**Most Common Review Score**: {most_common_review_score}")

    # Plotting Review Scores
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=review_score.index, 
                y=review_score.values, 
                palette=["#007BFF" if score == common_score else "#D3D3D3" for score in review_score.index])
    
    plt.title("Customer Ratings", fontsize=15)
    plt.xlabel("Rating")
    plt.ylabel("Count")
    st.pyplot(fig)

# --- Tab 4: Customer Demographics ---
with tab4:
    st.markdown("### 🌍 Customer Demographics")
    tab_state, tab_status, tab_map = st.tabs(["State", "Order Status", "Geolocation"])

    with tab_state:
        most_common_state = state.customer_state.value_counts().index[0]
        st.markdown(f"Most Common State: **{most_common_state}**")

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x=state.customer_state.value_counts().index,
                    y=state.customer_count.values, 
                    data=state,
                    palette=["#068DA9" if score == most_common_state else "#D3D3D3" for score in state.customer_state.value_counts().index]
                        )

        plt.title("Number customers from State", fontsize=15)
        plt.xlabel("State")
        plt.ylabel("Number of Customers")
        plt.xticks(fontsize=12)
        st.pyplot(fig)

    with tab_status:
        common_status_ = order_status.value_counts().index[0]
        st.markdown(f"Most Common Order Status: **{common_status_}**")

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(x=order_status.index,
                    y=order_status.values,
                    order=order_status.index,
                    palette=["#068DA9" if score == common_status else "#D3D3D3" for score in order_status.index]
                    )
        
        plt.title("Order Status", fontsize=15)
        plt.xlabel("Status")
        plt.ylabel("Count")
        plt.xticks(fontsize=12)
        st.pyplot(fig)

    with tab_map:
        map_plot.plot()
        with st.expander("See Explanation"):
            st.write(
                "The state with the most customers is São Paulo (SP), followed by Rio de Janeiro (RJ). "
                "The majority of customer orders have a status of 'delivered,' indicating successful shipping. "
                "This correlates with higher customer ratings, as many customers gave a 5-star rating for the e-commerce service. "
                "The graph indicates a higher concentration of customers in capital cities, particularly in the southeastern and southern regions."
            )

