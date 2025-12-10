import streamlit as st
import pandas as pd
import numpy as np
import folium as fm
from folium import TileLayer, FeatureGroup, CircleMarker, Popup, LayerControl
import branca.element
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import math
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import streamlit.components.v1 as components

# Import your dictionaries from your data folder as originally structured
# Or define them here if mapping_dicts.py doesn't exist yet
from data.mapping_dicts import TypeOfWork_full_color, TypeOfWork_dict, column_interpretations

def load_css():
    with open("styles/main.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        dataframe = pd.read_csv("data/dpwh_flood_control_projects.csv")
        return dataframe
    except FileNotFoundError:
        st.error("File 'dpwh_flood_control_projects.csv' not found.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

@st.cache_data
def prep_data(data):

    if data.empty: return data
    clean = data.copy()

    cols_to_clean = ['ContractCost', 'ApprovedBudgetForContract']
    for col in cols_to_clean:
        if col in clean.columns:
            if clean[col].dtype == 'object':
                clean[col] = clean[col].astype(str).str.replace(',', '', regex=True)
            clean[col] = pd.to_numeric(clean[col], errors='coerce')

    clean = clean.dropna(subset=['ContractCost', 'ApprovedBudgetForContract'])

    clean['StartDate'] = pd.to_datetime(clean['StartDate'], errors='coerce')
    clean['ActualCompletionDate'] = pd.to_datetime(clean['ActualCompletionDate'], errors='coerce')

    clean['Duration'] = (clean['ActualCompletionDate'] - clean['StartDate']).dt.days

    clean['StartDate'] = clean['StartDate'].dt.strftime('%B-%d-%Y')
    clean['ActualCompletionDate'] = clean['ActualCompletionDate'].dt.strftime('%B-%d-%Y')

    clean['FundingYear'] = pd.to_numeric(clean['FundingYear'], errors='coerce')
    clean = clean.loc[~clean['FundingYear'].isin([2018, 2019, 2020, 2021, 2025])]

    clean['BudgetDifference'] = clean['ApprovedBudgetForContract'] - clean['ContractCost']
    clean['BudgetVariance'] = (clean['BudgetDifference'] / clean['ApprovedBudgetForContract']) * 100
    clean['RiskScore'] = (clean['ContractCost'] / clean['ApprovedBudgetForContract'])
    clean['IsSuspicious'] = clean['RiskScore'] > 0.99

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
            (filtered_df['FundingYear'] <= selected_years[1])]
    return filtered_df

def get_filters(df):
    """Renders sidebar filters and returns filtered dataframe"""
    with st.sidebar:
        st.subheader("zearch and Filter")
        search_term = st.text_input("Project Name", placeholder="e.g., River Wall", key="search_term")
        search_id = st.text_input("Project ID", placeholder="e.g., P00...", key="search_id")

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

@st.cache_data
def get_island_fig(df, chart_type):
    island_counts = df['MainIsland'].value_counts().reset_index()
    island_counts.columns = ['MainIsland', 'Count']
    if island_counts.empty: return None

    if chart_type == "Donut Chart":
        fig = px.pie(island_counts, values='Count', names='MainIsland', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Prism)
    else:
        fig = px.bar(island_counts, x='MainIsland', y='Count', color='Count',
                     color_continuous_scale='Viridis')
    fig.update_layout(margin=dict(t=10, b=0, l=0, r=0), height=350)
    return fig

@st.cache_data
def get_region_fig(df, top_n):
    region_counts = df['Region'].value_counts().reset_index().head(top_n)
    region_counts.columns = ['Region', 'Count']
    if region_counts.empty: return None
    dynamic_height = 150 + (len(region_counts) * 25)
    fig = px.bar(region_counts, x='Count', y='Region', orientation='h',
                 text='Count', color='Count', color_continuous_scale='Blues')
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=10, b=0, l=0, r=0), height=dynamic_height)
    return fig

@st.cache_data
def get_cost_hist_fig(df, dist_type, bin_count, use_log):
    if df.empty: return None
    if dist_type == "Contract Cost":
        fig = px.histogram(df, x="ContractCost", nbins=bin_count, title="Distribution of Contract Costs")
    else:
        fig = px.histogram(df, x="ApprovedBudgetForContract", nbins=bin_count, title="Distribution of Approved Budgets")
    if use_log:
        fig.update_layout(yaxis_type="log")
    fig.update_layout(bargap=0.1, margin=dict(t=30, b=0, l=0, r=0))
    return fig

@st.cache_data
def get_project_type_fig(df, chart_type):
    tow_counts = df['TypeOfWork'].value_counts().reset_index().head(10)
    tow_counts.columns = ['TypeOfWork', 'Count']
    if tow_counts.empty: return None
    dynamic_height = 400
    if chart_type == "Bar Chart":
        dynamic_height = 150 + (len(tow_counts) * 30)
        fig = px.bar(tow_counts, x='TypeOfWork', y='Count', color='TypeOfWork', title="Top 10 Project Types by Volume")
        fig.update_layout(showlegend=False, xaxis_tickangle=-45)
    else:
        fig = px.pie(tow_counts, values='Count', names='TypeOfWork', title="Top 10 Project Types by Volume")
    fig.update_layout(height=dynamic_height)
    return fig

@st.cache_data
def get_contractor_figs(df):
    con_val = df.groupby('Contractor')['ContractCost'].sum().sort_values(ascending=False).head(20).reset_index()
    dynamic_height = 150 + (20 * 25)
    if not con_val.empty:
        fig_val = px.bar(con_val, x='ContractCost', y='Contractor', orientation='h',
                         title=f"Top {20} Contractors by Value",
                         text_auto='.2s', color='ContractCost', color_continuous_scale='Viridis')
        fig_val.update_layout(yaxis={'categoryorder':'total ascending'}, height=dynamic_height)
    else:
        fig_val = None

    con_count = df['Contractor'].value_counts().head(20).rename_axis('Contractor').reset_index(name='Count')
    if not con_count.empty:
        fig_vol = px.bar(con_count, x='Count', y='Contractor', orientation='h',
                         title=f"Top {20} Contractors by Volume",
                         text_auto=True, color='Count', color_continuous_scale='Inferno')
        fig_vol.update_layout(yaxis={'categoryorder':'total ascending'}, height=dynamic_height)
    else:
        fig_vol = None
    return fig_val, fig_vol

# Non-cached plot functions (matplotlib returns figs)
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
    cluster_data = df[['ContractCost', 'Duration']].dropna()
    if len(cluster_data) < 10: return None
    cluster_data['Log_Cost'] = np.log1p(cluster_data['ContractCost'])
    cluster_data['Log_Duration'] = np.log1p(cluster_data['Duration'])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(cluster_data[['Log_Cost', 'Log_Duration']])
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    cluster_data['Cluster'] = kmeans.fit_predict(X_scaled)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        data=cluster_data, x='Duration', y='ContractCost',
        hue='Cluster', palette='viridis', style='Cluster', s=100, ax=ax
    )
    ax.set_xscale('log')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_title("Project Clusters: Cost vs. Duration (Anomaly Detection)")
    ax.set_xlabel("Duration (Days) - Log Scale")
    ax.set_ylabel("Contract Cost (PHP) - Log Scale")
    return fig

def plot_bid_variance(df):
    df_zoom = df[(df['BudgetVariance'] > -5) & (df['BudgetVariance'] < 10)]
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(df_zoom['BudgetVariance'], bins=50, kde=True, color='darkred', ax=ax)
    ax.axvline(0, color='black', linestyle='--', label='Exact Budget Match')
    ax.set_title("Bid Variance Distribution (Detection of Bid Rigging)")
    ax.set_xlabel("Variance % (0 = Bid matched Budget exactly)")
    ax.legend()
    return fig

def plot_top_contractors(df):
    top = df.groupby('Contractor')['ContractCost'].sum().sort_values(ascending=False).head(20)
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.barplot(y=top.index, x=top.values, palette='mako', ax=ax)
    ax.set_xlabel("Total Contract Value (PHP)")
    ax.set_title("Top 20 Contractors by Market Share")
    return fig

@st.cache_resource
def create_map(df, center, zoom):
    try:
        m = fm.Map(location=center, zoom_start=zoom, control_scale=True, prefer_canvas=True, tiles=None)
        TileLayer(
            tiles="https://controlmap.mgb.gov.ph/arcgis/rest/services/GeospatialDataInventory_Public/GDI_Detailed_Flood_Susceptibility_Public/MapServer/tile/{z}/{y}/{x}",
            attr="MGB Flood Hazard", name="MGB Flood Susceptibility", overlay=True, control=True, show=False, opacity=0.5
        ).add_to(m)
        TileLayer(
            tiles="https://controlmap.mgb.gov.ph/arcgis/rest/services/GeospatialDataInventory_Public/GDI_Detailed_Rain_induced_Landslide_Susceptibility_Public/MapServer/tile/{z}/{y}/{x}",
            attr="MGB Rain/Landslide",
            name="MGB Rain Induced Landslide Susceptibility",
            overlay=True,
            control=True,
            show=False,
            opacity=0.5
        ).add_to(m)

        TileLayer("Esri.WorldImagery", name="Satellite", show=True).add_to(m)
        TileLayer("CartoDB.DarkMatter", name="Dark Mode", show=False).add_to(m)
        TileLayer("OpenStreetMap", name="Street Map", show=False).add_to(m)

        fm.plugins.Fullscreen(position="bottomleft", title="Expand me", title_cancel="Exit me", force_separate_button=True).add_to(m)
        fg = fm.FeatureGroup(name="DPWH Projects (Markers)")

        if not df.empty:
            # Vectorized data extraction for speed
            id, lats, lons = df['ProjectId'].values, df['latitude'].values, df['longitude'].values
            names, regions, costs = df['ProjectName'].values, df['Region'].values, df['ContractCost'].values
            startdates, enddates, durations = df['StartDate'].values, df['ActualCompletionDate'].values, df['Duration'].values
            contractors, fundingyears = df['Contractor'].values, df['FundingYear'].values
            legDist, Municipality, engDist = df['LegislativeDistrict'].values, df['Municipality'].values, df['DistrictEngineeringOffice'].values
            risks, tow_vals = df['RiskScore'].values, df['TypeOfWork'].values

            for pid, lat, lon, name, region, cost, start, end, dur, cont, fund, ld, mun, ed, risk, tow in zip(id, lats, lons, names, regions, costs, startdates, enddates, durations, contractors, fundingyears, legDist, Municipality, engDist, risks, tow_vals):
                formatted_cost = f"₱{cost:,.2f}"
                popup_html = f"""
                            <div style="font-family: sans-serif; font-size: 12px; line-height: 1.4; color: #333;">
                                <b style="font-size: 14px; color: #000;">{name}</b><br>
                                <span style="color: #006400; font-weight: bold;">{formatted_cost}</span> &bull; {tow} &bull; FY {fund}
                                <hr style="margin: 8px 0; border: 0; border-top: 1px solid #ccc;">
                                <b>Loc:</b> {mun}, {ld} ({region})<br>
                                <b>Eng:</b> {ed}<br>
                                <b>Time:</b> {start} &ndash; {end} <i>({dur} days)</i><br>
                                <b>By:</b> {cont}<br>
                                <b>Risk Score: {risk:.2f} </b>
                            </div>
                        """
                iframe = branca.element.IFrame(html=popup_html, width="520px", height="180px")
                pp = fm.Popup(iframe, max_width=500)
                mark = fm.CircleMarker(
                    location=[lat, lon], radius=3, fill=True, fill_opacity=0.7, tooltip=f"Project ID: {pid}", popup=pp,
                    fill_color=TypeOfWork_full_color.get(tow, 'blue'), color=TypeOfWork_full_color.get(tow, 'blue')
                )
                fg.add_child(mark)
        fg.add_to(m)
        fm.LayerControl(position='bottomleft').add_to(m)
        return m
    except Exception as e:
        st.error(f"Error creating map: {e}")