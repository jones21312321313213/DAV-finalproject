import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page configuration
st.set_page_config(
    page_title="Flood Mitigation Projects - Overview",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
.main-header {
    font-size: 2.2em;
    font-weight: bold;
    color: #2E86AB;
    text-align: center;
    margin-bottom: 20px;
}
.sub-header {
    font-size: 1.4em;
    font-weight: bold;
    color: #A23B72;
    margin-top: 20px;
    margin-bottom: 10px;
}
.description {
    font-size: 1.05em;
    line-height: 1.6;
    color: #333;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">Flood Mitigation Projects - Data Overview</div>', unsafe_allow_html=True)

# Introductory section
st.markdown("### Dataset Introduction")
st.write(
    "This dataset contains flood mitigation projects across regions in the Philippines. "
    "It includes details such as approved budgets, contract costs, funding years, and project types. "
    "The dataset allows us to explore how resources are allocated and which contractors dominate the field."
)

st.markdown("### Research Question")
st.write(
    "How are flood mitigation budgets and contract costs distributed across regions and project types?"
)

st.markdown("### Selected Analysis Technique")
st.write(
    "We apply descriptive statistics and visualization techniques (pie charts, histograms) "
    "to identify trends and anomalies in the dataset."
)

# Load data
try:
    df = pd.read_csv("cleaned_flood_data.csv")
    df['ApprovedBudgetForContract'] = pd.to_numeric(df['ApprovedBudgetForContract'], errors='coerce')
    df['ContractCost'] = pd.to_numeric(df['ContractCost'], errors='coerce')
    df['FundingYear'] = pd.to_numeric(df['FundingYear'], errors='coerce')
    df = df.dropna(subset=['ApprovedBudgetForContract', 'ContractCost'])

    # 🔑 Fix Arrow serialization issue: convert object columns to strings
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str)

except FileNotFoundError:
    st.error("Data file 'cleaned_flood_data.csv' not found. Please ensure the file is in the same directory.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Filters")
selected_regions = st.sidebar.multiselect("Select Regions", sorted(df['Region'].unique()))
year_range = st.sidebar.slider("Funding Year Range",
                               int(df['FundingYear'].min()),
                               int(df['FundingYear'].max()),
                               (int(df['FundingYear'].min()), int(df['FundingYear'].max())))
selected_types = st.sidebar.multiselect("Select Type of Work", sorted(df['TypeOfWork'].unique()))

df_filtered = df.copy()
if selected_regions:
    df_filtered = df_filtered[df_filtered['Region'].isin(selected_regions)]
if selected_types:
    df_filtered = df_filtered[df_filtered['TypeOfWork'].isin(selected_types)]
df_filtered = df_filtered[(df_filtered['FundingYear'] >= year_range[0]) & (df_filtered['FundingYear'] <= year_range[1])]

# --- Key Metrics ---
st.markdown('<div class="sub-header">Key Metrics</div>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
col1.metric("Total Projects", len(df_filtered))
col2.metric("Average Approved Budget", f"₱{df_filtered['ApprovedBudgetForContract'].mean():,.0f}")
col3.metric("Average Contract Cost", f"₱{df_filtered['ContractCost'].mean():,.0f}")

# --- Dataset Structure ---
st.markdown('<div class="sub-header">Dataset Structure</div>', unsafe_allow_html=True)
structure_df = pd.DataFrame({
    "Column": df_filtered.columns,
    "Non-Null Count": df_filtered.notnull().sum(),
    "Data Type": df_filtered.dtypes.astype(str)
})
st.dataframe(structure_df, use_container_width=True)

# --- Raw Data (collapsible) ---
st.markdown('<div class="sub-header">Raw Data</div>', unsafe_allow_html=True)
with st.expander("Click to view raw dataset preview"):
    st.dataframe(df_filtered.head(20), use_container_width=True)

# --- Descriptive Statistics ---
st.markdown('<div class="sub-header">Descriptive Statistics</div>', unsafe_allow_html=True)
if not df_filtered.empty:
    variable = st.selectbox("Select variable for summary statistics:", ["ApprovedBudgetForContract", "ContractCost"])
    st.write(f"Summary statistics for **{variable}**:")
    st.dataframe(df_filtered[[variable]].describe())
else:
    st.warning("No valid rows remain after filtering. Adjust your filters to see data.")

# --- Quick Visualization ---
st.markdown('<div class="sub-header">Projects per Region</div>', unsafe_allow_html=True)
region_counts = df_filtered['Region'].value_counts()
fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(x=region_counts.index, y=region_counts.values, palette="tab20", ax=ax)
ax.set_title("Number of Projects per Region")
ax.set_xlabel("Region")
ax.set_ylabel("Project Count")
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
st.pyplot(fig, use_container_width=True)

# --- Download Filtered Data ---
st.download_button(
    label="Download Filtered Data",
    data=df_filtered.to_csv(index=False),
    file_name="filtered_flood_data.csv",
    mime="text/csv"
)
