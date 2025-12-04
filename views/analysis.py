import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error

# Page configuration
st.set_page_config(
    page_title="Flood Mitigation Projects - Analysis",
    page_icon="📈",
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
st.markdown('<div class="main-header">Flood Mitigation Projects - Analysis</div>', unsafe_allow_html=True)

# Load data
try:
    df = pd.read_csv("cleaned_flood_data.csv")
    df['ApprovedBudgetForContract'] = pd.to_numeric(df['ApprovedBudgetForContract'], errors='coerce')
    df['ContractCost'] = pd.to_numeric(df['ContractCost'], errors='coerce')
    df['FundingYear'] = pd.to_numeric(df['FundingYear'], errors='coerce')
    df = df.dropna(subset=['ApprovedBudgetForContract', 'ContractCost', 'FundingYear'])
except FileNotFoundError:
    st.error("Data file 'cleaned_flood_data.csv' not found. Please ensure the file is in the same directory.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Analysis Filters")
selected_regions = st.sidebar.multiselect("Select Regions", sorted(df['Region'].unique()))
year_range = st.sidebar.slider("Funding Year Range",
                               int(df['FundingYear'].min()),
                               int(df['FundingYear'].max()),
                               (int(df['FundingYear'].min()), int(df['FundingYear'].max())))

df_filtered = df.copy()
if selected_regions:
    df_filtered = df_filtered[df_filtered['Region'].isin(selected_regions)]
df_filtered = df_filtered[(df_filtered['FundingYear'] >= year_range[0]) & (df_filtered['FundingYear'] <= year_range[1])]

# --- K-means Clustering Section ---
st.markdown('<div class="sub-header">K-means Clustering</div>', unsafe_allow_html=True)
st.write("We use K-means clustering to group projects based on Approved Budget, Contract Cost, and Funding Year.")

# Sidebar control for number of clusters
k = st.sidebar.slider("Select number of clusters (k)", min_value=2, max_value=8, value=3)

# Scale numeric features
scaler = StandardScaler()
X = scaler.fit_transform(df_filtered[['ApprovedBudgetForContract', 'ContractCost', 'FundingYear']])

# Fit K-means
kmeans = KMeans(n_clusters=k, n_init="auto", random_state=42)
df_filtered['Cluster'] = kmeans.fit_predict(X)

# Cluster visualization options
st.markdown("#### Cluster Visualization")
x_var = st.selectbox("X-axis variable", ["ApprovedBudgetForContract", "ContractCost", "FundingYear"])
y_var = st.selectbox("Y-axis variable", ["ApprovedBudgetForContract", "ContractCost", "FundingYear"], index=1)

fig, ax = plt.subplots(figsize=(8, 6))
sns.scatterplot(x=df_filtered[x_var], y=df_filtered[y_var], hue=df_filtered['Cluster'], palette="tab10", ax=ax)
ax.set_title(f"Clusters of Projects ({x_var} vs {y_var})")
ax.set_xlabel(x_var)
ax.set_ylabel(y_var)
st.pyplot(fig, use_container_width=True)

# Cluster summaries
st.write("**Cluster Summaries (Average values per cluster):**")
cluster_summary = df_filtered.groupby('Cluster')[['ApprovedBudgetForContract','ContractCost','FundingYear']].mean()
st.dataframe(cluster_summary)

st.write("**Regional Distribution per Cluster:**")
region_cluster = df_filtered.groupby(['Cluster','Region']).size().unstack(fill_value=0)
st.dataframe(region_cluster)

st.info("Insight: Clusters reveal distinct spending patterns. Some regions dominate high-budget clusters, suggesting unequal resource distribution.")

# --- Linear Regression Section ---
st.markdown('<div class="sub-header">Linear Regression</div>', unsafe_allow_html=True)
st.write("We use Linear Regression to predict Contract Cost from Approved Budget and Funding Year.")

# Regression feature toggle
include_year = st.checkbox("Include Funding Year as predictor", value=True)

if include_year:
    X = df_filtered[['ApprovedBudgetForContract','FundingYear']]
else:
    X = df_filtered[['ApprovedBudgetForContract']]
y = df_filtered['ContractCost']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# Metrics
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

st.write(f"**R² Score:** {r2:.3f}")
st.write(f"**Mean Absolute Error:** {mae:,.0f} PHP")

# Coefficients
coef_df = pd.DataFrame({
    "Feature": X.columns,
    "Coefficient": model.coef_
})
st.write("**Regression Coefficients:**")
st.dataframe(coef_df)

# Scatter plot of predictions vs actual
fig, ax = plt.subplots(figsize=(8, 6))
sns.scatterplot(x=y_test, y=y_pred, ax=ax, color="blue")
ax.set_title("Predicted vs Actual Contract Cost")
ax.set_xlabel("Actual Contract Cost (PHP)")
ax.set_ylabel("Predicted Contract Cost (PHP)")
st.pyplot(fig, use_container_width=True)

# Residual plot
fig, ax = plt.subplots(figsize=(8, 6))
sns.histplot(y_test - y_pred, bins=30, kde=True, color="red", ax=ax)
ax.set_title("Residuals Distribution (Actual - Predicted)")
ax.set_xlabel("Residual (PHP)")
ax.set_ylabel("Frequency")
st.pyplot(fig, use_container_width=True)

# Compare models with vs without FundingYear
metrics = []
for include_year in [True, False]:
    if include_year:
        X = df_filtered[['ApprovedBudgetForContract','FundingYear']]
        label = "With Funding Year"
    else:
        X = df_filtered[['ApprovedBudgetForContract']]
        label = "Without Funding Year"
    y = df_filtered['ContractCost']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression().fit(X_train, y_train)
    y_pred = model.predict(X_test)
    metrics.append({"Model": label, "R²": r2_score(y_test, y_pred), "MAE": mean_absolute_error(y_test, y_pred)})

st.write("**Model Comparison:**")
st.dataframe(pd.DataFrame(metrics))

st.info("Insight: Approved budget is the strongest predictor of contract cost. Funding year adds little explanatory power, meaning costs are mostly driven by budget size.")
