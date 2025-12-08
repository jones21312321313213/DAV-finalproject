import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import FastMarkerCluster

# Set page configuration
st.set_page_config(
    page_title="Forensic Flood Project Analysis",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. Load Data ---
@st.cache_data
def load_data():
    """Loads CSV data."""
    try:
        # Using the file available in the environment
        data = pd.read_csv("data_cleaning/dpwh_flood_control_projects.csv")
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# --- 2. Preprocessing ---
@st.cache_data
def preprocess_forensic(df):
    """Cleans data and computes forensic metrics."""
    clean = df.copy()

    # Clean Currency Columns
    cols_to_clean = ['ContractCost', 'ApprovedBudgetForContract']
    for col in cols_to_clean:
        if col in clean.columns:
            if clean[col].dtype == 'object':
                clean[col] = clean[col].astype(str).str.replace(',', '', regex=True)
            clean[col] = pd.to_numeric(clean[col], errors='coerce')

    # Drop invalid rows
    clean = clean.dropna(subset=['ContractCost', 'ApprovedBudgetForContract'])

    # Compute Risk Metrics
    clean['RiskScore'] = clean['ContractCost'] / clean['ApprovedBudgetForContract']
    clean['IsSuspicious'] = clean['RiskScore'] > 0.99
    clean['Savings'] = clean['ApprovedBudgetForContract'] - clean['ContractCost']

    # Clean Year
    if 'FundingYear' in clean.columns:
        clean['FundingYear'] = pd.to_numeric(clean['FundingYear'], errors='coerce')
        clean = clean.dropna(subset=['FundingYear'])

    # Standardize Lat/Lon
    col_map = {'ProjectLatitude': 'latitude', 'ProjectLongitude': 'longitude'}
    clean = clean.rename(columns=col_map)
    clean = clean.dropna(subset=['latitude', 'longitude'])

    return clean

# --- 3. Filter Logic ---
def get_filters(df):
    """Renders filters in the sidebar/column and returns filtered dataframe."""

    with st.sidebar:
        st.header("🔍 Filter Projects")
        search_term = st.text_input("Search Project Name", "")

        regions = sorted(df['Region'].dropna().unique().tolist()) if 'Region' in df.columns else []
        selected_regions = st.multiselect("Select Region", regions)

        provinces = sorted(df['Province'].dropna().unique().tolist()) if 'Province' in df.columns else []
        selected_provinces = st.multiselect("Select Province", provinces)

        work_types = sorted(df['TypeOfWork'].dropna().unique().tolist()) if 'TypeOfWork' in df.columns else []
        selected_works = st.multiselect("Select Type of Work", work_types)

        selected_years = None
        if 'FundingYear' in df.columns:
            min_year = int(df['FundingYear'].min())
            max_year = int(df['FundingYear'].max())
            selected_years = st.slider("Funding Year Range", min_year, max_year, (min_year, max_year))

    # Apply Logic
    filtered_df = df.copy()

    if search_term:
        filtered_df = filtered_df[filtered_df['ProjectName'].str.contains(search_term, case=False, na=False)]
    if selected_regions:
        filtered_df = filtered_df[filtered_df['Region'].isin(selected_regions)]
    if selected_provinces:
        filtered_df = filtered_df[filtered_df['Province'].isin(selected_provinces)]
    if selected_works:
        filtered_df = filtered_df[filtered_df['TypeOfWork'].isin(selected_works)]
    if selected_years:
        filtered_df = filtered_df[
            (filtered_df['FundingYear'] >= selected_years[0]) &
            (filtered_df['FundingYear'] <= selected_years[1])
            ]

    return filtered_df

# --- 4. Optimized Map Generation ---
# @st.cache_resource
def generate_map(data, center):
    """
    Generates the Folium map object.
    Cached with st.cache_resource so it only rebuilds when 'data' changes.
    """
    m = folium.Map(location=center, zoom_start=6, tiles="cartodbpositron")

    if not data.empty:
        locations = data[['latitude', 'longitude']].values.tolist()
        FastMarkerCluster(data=locations).add_to(m)
    st_folium(m, returned_objects=[], use_container_width=True)
    return m

# --- 5. Main Application ---
def main():
    st.title("Forensic Data Analysis for Flood Control Projects")

    # Load and Clean
    raw_data = load_data()
    if raw_data is None:
        return
    df_clean = preprocess_forensic(raw_data)

    # Get Filtered Data
    filtered_df = get_filters(df_clean)

    # --- KPI METRICS SECTION ---
    # We display high-level stats relevant to forensic auditing
    if not filtered_df.empty:
        total_expenditure = filtered_df['ContractCost'].sum()
        total_suspicious_value = filtered_df[filtered_df['IsSuspicious']]['ContractCost'].sum()
        suspicious_count = filtered_df['IsSuspicious'].sum()
        suspicious_pct = (suspicious_count / len(filtered_df)) * 100

        # Calculate Bid Variance (Savings)
        total_budget = filtered_df['ApprovedBudgetForContract'].sum()
        avg_savings_pct = ((total_budget - total_expenditure) / total_budget) * 100

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        kpi1.metric(
            "Total Contract Value",
            f"₱{total_expenditure / 1e9:,.2f} B",
            help="Total value of contracts awarded."
        )

        kpi2.metric(
            "At-Risk Capital",
            f"₱{total_suspicious_value / 1e9:,.2f} B",
            delta_color="inverse",
            help="Total value of projects flagged as suspicious (Cost > 99% of Budget)."
        )

        kpi3.metric(
            "Suspicious Projects",
            f"{suspicious_count} ({suspicious_pct:.1f}%)",
            delta=f"{suspicious_count} Flagged",
            delta_color="inverse",
            help="Number of projects where Contract Cost is suspiciously close to the Budget Ceiling."
        )

        kpi4.metric(
            "Gov't Savings Rate",
            f"{avg_savings_pct:.2f}%",
            delta="Lower is Riskier",
            delta_color="normal", # Logic: Low savings = Bad for govt/High risk of collusion
            help="Average difference between Budget and Contract Cost. Near 0% suggests lack of competition."
        )

        st.markdown("---")

    # Layout
    col1, col2 = st.columns([0.8, .2], gap="small")

    with col1:
        st.subheader(f"Interactive Map ({len(filtered_df)} projects)")

        if not filtered_df.empty:
            center_lat = filtered_df['latitude'].mean()
            center_lon = filtered_df['longitude'].mean()
            center = [center_lat, center_lon]
        else:
            center = [11.8917, 122.4199]

        folium_map = generate_map(filtered_df, center)


    with col2:
        st.subheader("Details")

        if not filtered_df.empty:
            # Top Contractor Statistic
            if 'Contractor' in filtered_df.columns:
                top_contractor = filtered_df.groupby('Contractor')['ContractCost'].sum().sort_values(ascending=False).head(1)
                st.info(f"🏆 Top Contractor: **{top_contractor.index[0]}**")
                st.caption(f"Total Awarded: ₱{top_contractor.values[0]/1e6:,.1f} M")

            st.write("Recent Projects:")
            st.dataframe(
                filtered_df[['ProjectName', 'ContractCost', 'RiskScore']].sort_values('ContractCost', ascending=False).head(10),
                hide_index=True
            )
        else:
            st.warning("No projects match the current filters.")

if __name__ == '__main__':
    main()