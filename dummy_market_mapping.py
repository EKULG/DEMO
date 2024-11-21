import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# Load the data
df = pd.read_csv("large_realistic_companies.csv")

# Streamlit App UI
st.title("Market Mapping Demo")

# Dropdown for company selection
selected_company = st.selectbox(
    "Select target company",
    ["Select..."] + df["Company name"].tolist()
)

# Tags Section
if selected_company != "Select...":
    selected_data = df[df["Company name"] == selected_company].iloc[0]
    
    # Get all possible options for each category
    all_tags = {
        "Industry": df["Industry"].unique().tolist(),
        "Industry Sectors": set(sector.strip() for sectors in df["Industry Sectors"].str.split(",") for sector in sectors),
        "Key product & or services": set(product.strip() for products in df["Key product & or services"].str.split(",") for product in products),
        "Market positioning": set(position.strip() for positions in df["Market positioning"].str.split(",") for position in positions),
        "Business model": df["Business model"].unique().tolist(),
        "Ownership": df["Ownership"].unique().tolist()
    }
    
    # Get selected company's tags
    company_tags = {
        "Industry": [selected_data["Industry"]],
        "Industry Sectors": [s.strip() for s in selected_data["Industry Sectors"].split(",")],
        "Key product & or services": [s.strip() for s in selected_data["Key product & or services"].split(",")],
        "Market positioning": [s.strip() for s in selected_data["Market positioning"].split(",")],
        "Business model": [selected_data["Business model"]],
        "Ownership": [selected_data["Ownership"]]
    }
    
    # Create 3x3 grid of multiselect boxes and store selections
    st.markdown("### Tags")
    cols = st.columns(3)
    
    selected_filters = {}
    for i, (key, options) in enumerate(all_tags.items()):
        with cols[i % 3]:
            selected_filters[key] = st.multiselect(
                key,
                options=sorted(options),
                default=company_tags[key]
            )

    st.markdown("---")

    # Filter the dataframe based on selected tags
    filtered_df = df.copy()
    
    # Apply filters for each category
    if selected_filters["Industry"]:
        filtered_df = filtered_df[filtered_df["Industry"].isin(selected_filters["Industry"])]
    
    # For comma-separated fields, check if any selected tag is in the list
    for field in ["Industry Sectors", "Key product & or services", "Market positioning"]:
        if selected_filters[field]:
            filtered_df = filtered_df[
                filtered_df[field].apply(
                    lambda x: any(tag in [s.strip() for s in x.split(",")] for tag in selected_filters[field])
                )
            ]
    
    # Apply filters for single-value fields
    if selected_filters["Business model"]:
        filtered_df = filtered_df[filtered_df["Business model"].isin(selected_filters["Business model"])]
    
    if selected_filters["Ownership"]:
        filtered_df = filtered_df[filtered_df["Ownership"].isin(selected_filters["Ownership"])]

    # Display Data Table
    st.subheader("Similar Companies")
    st.write(
        filtered_df.sort_values(by="Similarity score", ascending=False).style.highlight_max(
            subset=["Similarity score"], axis=0
        )
    )
