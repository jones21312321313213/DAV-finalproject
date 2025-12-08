import streamlit as st
import pandas as pd
import folium as fm
from folium.plugins import MarkerCluster, Fullscreen
from streamlit_folium import st_folium
import branca.element
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import math
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- CONFIGURATION ---
st.set_page_config(layout="centered", page_title="Flood Control Project Dashboard")

# --- MAPPING DICTIONARIES ---
TypeOfWork_dict = {
    'Flood Mitigation': 'Construction of Flood Mitigation Structure',
    "Revetment": 'Construction of Revetment',
    "Drainage Structure Rehab": 'Rehabilitation / Major Repair of Drainage Structure',
    "Slope Protection": 'Construction of Slope Protection Structure',
    "Drainage": 'Construction of Drainage Structure',
    "Dike": 'Construction of Dike',
    "Flood Control Rehab": 'Rehabilitation / Major Repair of Flood Control Structure',
    "Flood Mitigation Facility": 'Construction of Flood Mitigation Facility',
    "Flood Mitigation Rehab": 'Rehabilitation / Major Repair of Flood Mitigation Facility',
    "Slope Protection Rehab": 'Rehabilitation / Major Repair of Slope Protection Structure',
    "Retarding Basin": 'Construction of Retarding Basin',
    "Groundsill": 'Construction of Groundsill',
    "Spur Dike": 'Construction of Spur Dike',
    "Drainage Structure Upgrade": 'Upgrading of Drainage Structure',
    "Waterway": 'Construction of Waterway',
    "Cutoff Channel": 'Construction of Cutoff Channel',
    "Flood Control Repair": 'Repair/Maintenance of Flood Control Structures',
    "Embankment": 'Embankment'
}

TypeOfWork_full_color = {
    'Construction of Flood Mitigation Structure': '#1f77b4',
    'Construction of Revetment': '#ff7f0e',
    'Rehabilitation / Major Repair of Drainage Structure': '#2ca02c',
    'Construction of Slope Protection Structure': '#d62728',
    'Construction of Drainage Structure': '#9467bd',
    'Construction of Dike': '#8c564b',
    'Rehabilitation / Major Repair of Flood Control Structure': '#e377c2',
    'Construction of Flood Mitigation Facility': '#7f7f7f',
    'Rehabilitation / Major Repair of Flood Mitigation Facility': '#bcbd22',
    'Rehabilitation / Major Repair of Slope Protection Structure': '#17becf',
    'Construction of Retarding Basin': '#aec7e8',
    'Construction of Groundsill': '#ffbb78',
    'Construction of Spur Dike': '#98df8a',
    'Upgrading of Drainage Structure': '#ff9896',
    'Construction of Waterway': '#c5b0d5',
    'Construction of Cutoff Channel': '#c49c94',
    'Repair/Maintenance of Flood Control Structures': '#f7b6d2',
    'Embankment': '#c7c7c7'
}

# --- DATA LOADING ---
@st.cache_data
def load_data():
    try:
        # Adjusted to match the likely file location in your environment
        dataframe = pd.read_csv("data_cleaning/cleaned_flood_data.csv")
        return dataframe
    except FileNotFoundError:
        st.error("File 'cleaned_flood_data.csv' not found.")
        return None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

@st.cache_data
def preprocess_forensic(data):
    """Cleans data and computes forensic metrics."""
    clean = data.copy()

    # 1. Clean Currency Columns
    cols_to_clean = ['ContractCost', 'ApprovedBudgetForContract']
    for col in cols_to_clean:
        if col in clean.columns:
            if clean[col].dtype == 'object':
                clean[col] = clean[col].astype(str).str.replace(',', '', regex=True)
            clean[col] = pd.to_numeric(clean[col], errors='coerce')

    clean = clean.dropna(subset=['ContractCost', 'ApprovedBudgetForContract'])

    # 2. Compute Metrics
    clean['RiskScore'] = clean['ContractCost'] / clean['ApprovedBudgetForContract']
    clean['IsSuspicious'] = clean['RiskScore'] > 0.99

    # Calculate Budget Variance % (Positive = Savings, Negative = Overrun)
    clean['BudgetVariancePct'] = ((clean['ApprovedBudgetForContract'] - clean['ContractCost']) / clean['ApprovedBudgetForContract']) * 100

    # 3. Date Handling
    clean['StartDate'] = pd.to_datetime(clean['StartDate'], errors='coerce')
    clean['ActualCompletionDate'] = pd.to_datetime(clean['ActualCompletionDate'], errors='coerce')

    # 4. Standardize Coordinates
    col_map = {'ProjectLatitude': 'latitude', 'ProjectLongitude': 'longitude'}
    clean = clean.rename(columns=col_map)
    clean = clean.dropna(subset=['latitude', 'longitude'])

    return clean


def apply_filter(df, search_term, search_id, selected_regions, selected_provinces, selected_works, selected_years):
    filtered_df = df.copy()

    if search_term:
        filtered_df = filtered_df[filtered_df['ProjectName'].str.contains(search_term, case=False, na=False)]
    if search_id:
        filtered_df = filtered_df[filtered_df['ProjectId'].str.astype(str).str.contains(search_id, case=False, na=False)]
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

def get_filters(df):
    with st.sidebar:
        st.header("Project Filters")
        search_term = st.text_input("Project Name", placeholder="e.g., River Wall")
        search_id = st.text_input("Project ID", placeholder="e.g., P00...")

        regions = sorted(df['Region'].unique().tolist())
        selected_regions = st.multiselect("Region", regions)

        provinces = sorted(df['Province'].unique().tolist())
        selected_provinces = st.multiselect("Province", provinces)

        work_keys = sorted(TypeOfWork_dict.keys())
        selected_work_keys = st.multiselect("Type of Work", work_keys)
        selected_works = [TypeOfWork_dict[k] for k in selected_work_keys]

        if 'FundingYear' in df.columns:
            min_y = int(df['FundingYear'].min())
            max_y = int(df['FundingYear'].max())
            selected_years = st.slider("Funding Year", min_y, max_y, (min_y, max_y))
        else:
            selected_years = None

        return apply_filter(df, search_term, search_id, selected_regions, selected_provinces, selected_works, selected_years)


CENTER = (11.8917830337768213,122.41992187500001)
st.session_state["center"] = CENTER
st.session_state["zoom"] = 6

# @st.cache_resource
def create_map(df):
    try:
        m = fm.Map(
            location=CENTER,
            zoom_start=st.session_state["zoom"],
            tiles="Esri.WorldImagery",
            control_scale=True,
            prefer_canvas=True
        )
        fm.plugins.Fullscreen(
            position="topright",
            title="Expand me",
            title_cancel="Exit me",
            force_separate_button=True,
        ).add_to(m)
        # fm.TileLayer("Cartodb dark_matter", name="Dark").add_to(m)
        # fm.TileLayer("OpenStreetMap", name="Street").add_to(m)
        fm.LayerControl().add_to(m)

        fg = fm.FeatureGroup(name="markers")
        if not df.empty:
            id = df['ProjectId'].values
            lats = df['latitude'].values
            lons = df['longitude'].values
            names = df['ProjectName'].values
            regions = df['Region'].values
            startdates = df['StartDate'].values
            enddates = df['ActualCompletionDate'].values
            durations = df['DurationDays'].values
            contractors = df['Contractor'].values
            fundingyears = df['FundingYear'].values
            legislativeDistricts = df['LegislativeDistrict'].values
            Municipalities = df['Municipality'].values
            EngineeringDistricts = df['DistrictEngineeringOffice'].values
            tow = df['TypeOfWork'].values
            costs = df['ContractCost'].values
            # risks = df['RiskScore'].values

            for id, lat, lon, name, region, cost, startdate, enddate, duration, contractor, fundingyear, legDist, Municipality, engDist, tow in zip(id, lats, lons, names, regions, costs, startdates, enddates, durations, contractors, fundingyears, legislativeDistricts, Municipalities, EngineeringDistricts, tow):
                formatted_cost = f"₱{cost:,.2f}"
                popup_html = f"""
                            <div style="font-family: sans-serif; font-size: 12px; line-height: 1.4; color: #333;">
                                <b style="font-size: 14px; color: #000;">{name}</b><br>
                                <span style="color: #006400; font-weight: bold;">{formatted_cost}</span> &bull; {tow} &bull; FY {fundingyear}
                                
                                <hr style="margin: 8px 0; border: 0; border-top: 1px solid #ccc;">
                                
                                <b>Loc:</b> {Municipality}, {legDist} ({region})<br>
                                <b>Eng:</b> {engDist}<br>
                                <b>Time:</b> {startdate} &ndash; {enddate} <i>({duration} days)</i><br>
                                <b>By:</b> {contractor}
                            </div>
                        """
                iframe = branca.element.IFrame(html=popup_html, width="500px", height="180px")
                pp = fm.Popup(iframe, max_width=500)

                mark = fm.CircleMarker(
                    location=[lat, lon],
                    radius=6,
                    fill=True,
                    fill_opacity=0.7,
                    tooltip=f"Project ID: {id}",
                    popup=pp,
                    fill_color=TypeOfWork_full_color[tow],
                    color=TypeOfWork_full_color[tow]
                )
                fg.add_child(mark)

        return m, fg
    except Exception as e:
        st.error(f"Error creating map: {e}")


def plot_benfords_law(df):

    def get_first_digit(x):
        s = str(x).replace('.', '').replace(',', '')
        for char in s:
            if char.isdigit() and char != '0':
                return int(char)
        return np.nan

    first_digits = df['ContractCost'].apply(get_first_digit).dropna()
    digit_counts = first_digits.value_counts().sort_index()
    total_counts = digit_counts.sum()
    if total_counts == 0: return None

    observed_freq = (digit_counts / total_counts) * 100
    benford_expected = {d: math.log10(1 + 1/d) * 100 for d in range(1, 10)}

    plot_data = pd.DataFrame({
        'Digit': range(1, 10),
        'Observed': [observed_freq.get(d, 0) for d in range(1, 10)],
        'Expected': [benford_expected[d] for d in range(1, 10)]
    }).melt(id_vars='Digit', var_name='Type', value_name='Frequency (%)')

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=plot_data, x='Digit', y='Frequency (%)', hue='Type', ax=ax, palette=['#1f77b4', '#ff7f0e'])
    ax.set_title("Benford's Law Analysis (Fraud Detection)")
    ax.set_ylabel("Frequency (%)")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    return fig

def plot_clustering(df):
    cluster_data = df[['ContractCost', 'DurationDays']].dropna()
    if len(cluster_data) < 10: return None # Not enough data

    # Log transform
    cluster_data['Log_Cost'] = np.log1p(cluster_data['ContractCost'])
    cluster_data['Log_Duration'] = np.log1p(cluster_data['DurationDays'])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(cluster_data[['Log_Cost', 'Log_Duration']])

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    cluster_data['Cluster'] = kmeans.fit_predict(X_scaled)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        data=cluster_data, x='DurationDays', y='ContractCost',
        hue='Cluster', palette='viridis', style='Cluster', s=100, ax=ax
    )
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_title("Project Clusters: Cost vs. Duration (Anomaly Detection)")
    ax.set_xlabel("Duration (Days) - Log Scale")
    ax.set_ylabel("Contract Cost (PHP) - Log Scale")
    return fig

def plot_bid_variance(df):
    df_zoom = df[(df['BudgetVariancePct'] > -5) & (df['BudgetVariancePct'] < 10)]

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(df_zoom['BudgetVariancePct'], bins=50, kde=True, color='darkred', ax=ax)
    ax.axvline(0, color='black', linestyle='--', label='Exact Budget Match')
    ax.set_title("Bid Variance Distribution (Detection of Bid Rigging)")
    ax.set_xlabel("Variance % (0 = Bid matched Budget exactly)")
    ax.legend()
    return fig

def plot_top_contractors(df):
    top = df.groupby('Contractor')['ContractCost'].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(y=top.index, x=top.values, palette='mako', ax=ax)
    ax.set_xlabel("Total Contract Value (PHP)")
    ax.set_title("Top 10 Contractors by Market Share")
    return fig


# --- MAIN APP ---
def main():
    st.set_page_config(layout="centered")
    df = load_data()
    if df is None: st.stop()

    df_clean = preprocess_forensic(df)
    filtered_df = get_filters(df_clean)

    st.title("Flood Control Data Analysis")
    # st.markdown("Use this dashboard to detect anomalies, analyze contractor market share, and visualize infrastructure spending.")

    # --- TOP METRICS ---
    total_cost = filtered_df['ContractCost'].sum()
    suspicious_df = filtered_df[filtered_df['IsSuspicious']]
    suspicious_val = suspicious_df['ContractCost'].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Contract Value", f"₱{total_cost/1e9:,.2f} B")
    c2.metric("Suspicious Capital", f"₱{suspicious_val/1e6:,.1f} M", help="Projects with cost > 99% of budget")
    c3.metric("Flagged Projects", f"{len(suspicious_df)}", delta_color="inverse")
    c4.metric("Projects Found", f"{len(filtered_df)}")

    # --- MAP SECTION ---
    st.markdown("---")
    # c_map, c_info = st.columns([0.75, 0.25])

    # with c_map:
    m, fg = create_map(filtered_df)
    st_folium(m, feature_group_to_add=fg, height=500, returned_objects=[], width=1000)

    # with c_info:
    if not filtered_df.empty:
        # Most common project type
        top_type = filtered_df['TypeOfWork'].mode()[0]
        st.info(f"Most Common Work:\n**{top_type}**")

            # Avg Duration
        avg_dur = filtered_df['DurationDays'].mean()
        st.success(f"Avg Duration:\n**{avg_dur:.0f} Days**")

            # Highest Cost Project
        max_proj = filtered_df.loc[filtered_df['ContractCost'].idxmax()]
        st.warning(f"Most Expensive:\n**{max_proj['ProjectName'][:50]}...**\n(₱{max_proj['ContractCost']/1e6:.1f} M)")

    # --- FORENSIC VISUALIZATIONS ---
    st.markdown("### Forensic Analysis Dashboard")

    tab1, tab2, tab3 = st.tabs(["Fraud Detection", "Operational Efficiency", "Market Analysis"])

    with tab1:
        st.markdown("**Benford's Law** - Detects artificial numbers.")
        st.markdown("*If the blue bars deviate significantly from the orange bars (especially for digits 7-9), the costs may be manipulated.*")
        fig_benford = plot_benfords_law(filtered_df)
        if fig_benford: st.pyplot(fig_benford)

        st.divider()
        st.markdown("**Bid Variance Screening** - Detects 'Ceiling Bidding'.")
        st.markdown("*A massive spike between 0% and 0.1% suggests contractors know the budget ceiling and are bidding just below it.*")
        fig_var = plot_bid_variance(filtered_df)
        st.pyplot(fig_var)

    with tab2:
        st.markdown("**Cluster Analysis (K-Means)** - Groups projects by Cost & Time.")
        st.markdown("*Look for outliers: High Cost projects with Short Duration (Top-Left) are red flags.*")
        fig_cluster = plot_clustering(filtered_df)
        if fig_cluster:
            st.pyplot(fig_cluster)
        else:
            st.warning("Not enough data points for clustering.")

        st.divider()
        st.markdown("**Seasonality Analysis** - When do projects start?")
        if 'StartDate' in filtered_df.columns:
            filtered_df['StartMonth'] = filtered_df['StartDate'].dt.month_name()
            month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
            fig_season = plt.figure(figsize=(10, 4))
            sns.countplot(data=filtered_df, x='StartMonth', order=month_order, palette='magma')
            plt.xticks(rotation=45)
            plt.title("Project Starts by Month")
            st.pyplot(fig_season)

    with tab3:
        st.markdown("**Contractor Dominance** - Who controls the market?")
        fig_market = plot_top_contractors(filtered_df)
        st.pyplot(fig_market)

    # --- RAW DATA EXPANDER ---
    with st.expander("View Raw Data Table"):
        st.dataframe(filtered_df[['ProjectId', 'ProjectName', 'Contractor', 'ContractCost', 'ApprovedBudgetForContract', 'BudgetVariancePct', 'DurationDays', 'StartDate']], use_container_width=True)

if __name__ == '__main__':
    main()