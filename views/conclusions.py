import streamlit as st
import pandas as pd


# Page configuration
st.set_page_config(
    page_title="Flood Mitigation Projects - Conclusions",
    page_icon="✅",
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
st.markdown('<div class="main-header">Flood Mitigation Projects - Conclusions & Recommendations</div>', unsafe_allow_html=True)

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

# --- Summary Section ---
st.markdown('<div class="sub-header">Summary of Findings</div>', unsafe_allow_html=True)

avg_budget = df['ApprovedBudgetForContract'].mean()
avg_cost = df['ContractCost'].mean()
top_region = df['Region'].value_counts().idxmax()
top_type = df['TypeOfWork'].value_counts().idxmax()

st.write(f"""
- The **average approved budget** across projects is around ₱{avg_budget:,.0f}.
- The **average contract cost** is around ₱{avg_cost:,.0f}.
- The region with the **highest number of projects** is **{top_region}**.
- The most common **type of work** is **{top_type}**.
""")

st.info("From clustering, we saw distinct groups: low‑budget projects, mid‑range projects, and high‑budget outliers. Regression confirmed that approved budget is the strongest predictor of contract cost, while funding year adds little explanatory power.")

# --- Recommendations Section ---
st.markdown('<div class="sub-header">Recommendations</div>', unsafe_allow_html=True)

options = st.selectbox(
    "Choose a focus area to view recommendations:",
    ["Overall Budgeting", "Regional Allocation", "Project Types", "Future Planning"]
)

if options == "Overall Budgeting":
    st.write(f"""
    - Strengthen monitoring of projects with very high budgets (average ₱{avg_budget:,.0f}), as they tend to form outlier clusters.
    - Ensure contract costs remain aligned with approved budgets to avoid overspending.
    - Use regression insights to forecast contract costs more accurately during planning.
    """)

elif options == "Regional Allocation":
    st.write(f"""
    - Regions like **{top_region}** dominate project counts; balance allocations to reduce disparities.
    - Regions with consistently higher contract costs should undergo stricter auditing.
    - Identify low‑cost clusters and investigate whether underfunding affects project quality.
    """)

elif options == "Project Types":
    st.write(f"""
    - The most common type of work is **{top_type}**; diversify project types to balance resource use.
    - Small categories grouped under 'Others' should be reviewed to ensure they are not overlooked.
    - Consider bundling similar project types to achieve economies of scale.
    """)

elif options == "Future Planning":
    st.write("""
    - Use regression models to predict future contract costs based on proposed budgets.
    - Plan budgets with inflation and cost escalation in mind, especially for long-term projects.
    - Track funding year trends to anticipate periods of higher spending and prepare accordingly.
    """)


# --- Closing Section ---
st.markdown('<div class="sub-header">Final Takeaway</div>', unsafe_allow_html=True)
st.write("""
Flood mitigation projects show clear patterns in budget and cost behavior. By combining clustering and regression,
we can identify high-risk projects, forecast costs more reliably, and make smarter allocation decisions.
Implementing these recommendations will improve transparency, efficiency, and impact of future flood mitigation efforts.
""")
