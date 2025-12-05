import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.ticker import FuncFormatter

# Currency formatter for PHP
def php_fmt(x, pos):
    return f'₱{x:,.0f}'

# Page configuration
st.set_page_config(
    page_title="Flood Mitigation Projects - Visualizations",
    page_icon="📊",
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
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">Flood Mitigation Projects - Visualizations</div>', unsafe_allow_html=True)

# --- Data Exploration and Preparation Section ---
st.markdown('<div class="sub-header">Data Exploration and Preparation</div>', unsafe_allow_html=True)
st.write(
    "Before analysis, the dataset was cleaned to ensure consistency. "
    "Numeric columns such as **Approved Budget**, **Contract Cost**, and **Funding Year** "
    "were converted to numeric types. Rows with missing values in key budget and cost fields "
    "were dropped to avoid skewed results. Object-type columns were converted to strings "
    "to ensure compatibility with Streamlit’s visualization engine."
)

# Load data safely
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
bins = st.sidebar.slider("Number of bins for histograms", min_value=10, max_value=100, value=30)

# Apply filters
df_filtered = df.copy()
if selected_regions:
    df_filtered = df_filtered[df_filtered['Region'].isin(selected_regions)]
if selected_types:
    df_filtered = df_filtered[df_filtered['TypeOfWork'].isin(selected_types)]
df_filtered = df_filtered[(df_filtered['FundingYear'] >= year_range[0]) & (df_filtered['FundingYear'] <= year_range[1])]

# Box plot: Budget by Region with variable toggle
st.markdown("#### Box Plot by Region")
y_var = st.radio("Select variable for box plot:", ["ApprovedBudgetForContract", "ContractCost"])
fig, ax = plt.subplots(figsize=(10, 6))
sns.boxplot(x="Region", y=y_var, data=df_filtered, ax=ax)
ax.set_title(f"Distribution of {y_var} by Region")
ax.set_ylabel(f"{y_var} (PHP)")
ax.set_xlabel("Region")
ax.yaxis.set_major_formatter(FuncFormatter(php_fmt))
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
fig.tight_layout()
st.pyplot(fig, use_container_width=True)
st.info("Insight: Some regions show wider budget ranges, indicating variability in project funding. "
        "Regions with tighter boxes have more consistent budget allocations.")

# Correlation heatmap
st.markdown("#### Correlation Heatmap of Numeric Variables")
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(df_filtered[['ApprovedBudgetForContract','ContractCost','FundingYear']].corr(),
            annot=True, cmap="RdBu", center=0, ax=ax)
ax.set_title("Correlation Between Budget, Cost, and Funding Year")
fig.tight_layout()
st.pyplot(fig, use_container_width=True)
st.info("Insight: Approved budget and contract cost are strongly correlated, "
        "suggesting that higher budgets generally lead to higher costs. "
        "Funding year shows weaker correlation, meaning time has less influence on costs.")

# Funding Year distribution
st.markdown("#### Funding Year Distribution")
fig, ax = plt.subplots(figsize=(8, 5))
sns.histplot(df_filtered['FundingYear'].dropna(), bins=bins, kde=False, color="purple", ax=ax)
ax.set_title("Distribution of Funding Years")
ax.set_xlabel("Funding Year")
ax.set_ylabel("Project Count")
fig.tight_layout()
st.pyplot(fig, use_container_width=True)
st.info("Insight: Certain years have spikes in project counts, which may reflect government initiatives "
        "or increased funding during those periods.")

# --- Main Visualizations Section ---
# Region distribution with chart type toggle
st.markdown('<div class="sub-header">Distribution of Projects by Region</div>', unsafe_allow_html=True)
chart_type = st.selectbox("Choose chart type for Region distribution:", ["Pie", "Bar"])
region_counts = df_filtered['Region'].value_counts()
fig, ax = plt.subplots(figsize=(8, 6))
if chart_type == "Pie":
    ax.pie(region_counts.values, labels=region_counts.index, autopct='%1.1f%%',
           startangle=140, colors=plt.cm.tab20.colors)
    ax.axis('equal')
else:
    sns.barplot(x=region_counts.index, y=region_counts.values, ax=ax, palette="tab20")
    ax.set_ylabel("Project Count")
    ax.set_xlabel("Region")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
st.pyplot(fig, use_container_width=True)
st.info("Insight: Some regions account for a larger share of projects, "
        "indicating uneven distribution of flood mitigation efforts.")

# Main Island distribution
st.markdown('<div class="sub-header">Distribution of Projects by Main Island</div>', unsafe_allow_html=True)
island_groups = df_filtered['MainIsland'].value_counts()
fig, ax = plt.subplots(figsize=(8, 6))
ax.pie(island_groups.values, labels=island_groups.index, autopct='%1.1f%%',
       startangle=140, colors=plt.cm.tab20.colors)
ax.axis('equal')
st.pyplot(fig, use_container_width=True)
st.info("Insight: Luzon, Visayas, and Mindanao show different shares of projects, "
        "which may reflect geographic priorities in flood mitigation.")

# Type of Work distribution
st.markdown('<div class="sub-header">Distribution of Projects by Type of Work</div>', unsafe_allow_html=True)
tow = df_filtered['TypeOfWork'].value_counts()
small_tow = tow[tow / tow.sum() >= 0.01].copy()
others_sum = tow[tow / tow.sum() < 0.01].sum()
if others_sum > 0:
    small_tow.loc['Others'] = others_sum
fig, ax = plt.subplots(figsize=(8, 6))
ax.pie(small_tow.values, labels=small_tow.index, autopct='%1.1f%%',
       colors=plt.cm.tab20.colors)
ax.axis('equal')
st.pyplot(fig, use_container_width=True)
st.info("Insight: Certain types of work dominate spending, while smaller categories are grouped as 'Others'. "
        "This suggests a concentration of resources in specific project types.")

# Budget and Cost Distributions with adjustable bins
st.markdown('<div class="sub-header">Budget and Cost Distributions</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.histplot(df_filtered['ApprovedBudgetForContract'].dropna(), bins=bins, kde=True,
                 color='skyblue', ax=ax)
    ax.set_title('Approved Budget Distribution')
    ax.set_xlabel('Approved Budget (PHP)')
    ax.set_ylabel('Project Count')
    ax.xaxis.set_major_formatter(FuncFormatter(php_fmt))
    fig.tight_layout()
    st.pyplot(fig)
    st.info("Insight: Most projects have moderate budgets, but a few high-budget projects create a long tail.")

with col2:
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.histplot(df_filtered['ContractCost'].dropna(), bins=bins, kde=True,
                 color='salmon', ax=ax)
    ax.set_title('Contract Cost Distribution')
    ax.set_xlabel('Contract Cost (PHP)')
    ax.set_ylabel('Project Count')
    ax.xaxis.set_major_formatter(FuncFormatter(php_fmt))
    fig.tight_layout()
    st.pyplot(fig)
    st.info("Insight: Contract costs follow a similar distribution to budgets, "
            "reinforcing their strong correlation.")
