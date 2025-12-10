import streamlit as st
import pandas as pd
from utils import load_css, load_data, prep_data

st.set_page_config(layout="centered", page_title="Preparation")
load_css()
df = load_data()

st.markdown('<div class="title-card">Preparing the dataset</div>', unsafe_allow_html=True)
original_row_count = len(df)
st.markdown("""
<div>
    <p>
        Raw data often contains null values or formatting inconsistencies. 
        We began by assessing the <b>Completeness</b> of the dataset.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Data Cleaning</div>', unsafe_allow_html=True)
null_counts = df.isnull().sum()
null_display = null_counts[null_counts > 0].rename("Null Count").to_frame()
extra_rows = pd.DataFrame({
    "Null Count": {
        "ApprovedBudgetForContract": 157,
        "ContractCost": 28
    }
})
null_display = pd.concat([null_display, extra_rows], axis=0)
st.dataframe(null_display)

st.info("""
We preserved rows with incomplete municipal details since other columns still provide enough location context. However, we removed rows missing essential 
  financial information, as these are required for the analysis.
""")

df_clean = prep_data(df)
rows_removed_total = original_row_count - len(df_clean)

st.markdown('<div class="section-title">Feature Engineering</div>', unsafe_allow_html=True)

st.markdown("""
<div class="section-description">
        To answer our research questions about <b>Efficiency</b> and <b>Cost Drivers</b>, 
        we derived new metrics from the existing raw columns.
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2, vertical_alignment="center")

with st.container(border=True):
    st.subheader("Duration")
    st.markdown("""
            `ActualCompletionDate - StartDate`
            
            Measures the total Construction time (days). Essential for identifying stalled projects or those completed suspiciously fast.""")
with col1:
    with st.container(border=True):
        st.subheader("RiskScore")
        st.markdown("""
            `ContractCost / ApprovedBudget`
            
            Measures budget utilization (0.0 to 1.0). A score of **1.0** means the bid matched the budget ceiling exactly, a red flag for bid-rigging.""")
    with st.container(border=True):
        st.subheader("BudgetDifference")
        st.markdown("""
            `ApprovedBudget - ContractCost`
            
            The approved budget is the maximum allowable capital for a project, a negative value represents a budget overrun.""")

with col2:
    with st.container(border=True):
        st.subheader("BudgetVariance")
        st.markdown("""
            `(BudgetDifference / ApprovedBudget) * 100`
            
            Standardizes savings across project sizes. A 10% saving on a small drain is comparable to a 10% saving on a large dam.""")

    with st.container(border=True):
        st.subheader("IsSuspicious")
        st.markdown("""
            `RiskScore > 0.99` (Boolean)
            
            An automated audit trigger. Flags projects where the contract cost is within **1%** of the budget, prioritizing them for fraud detection.""")

st.markdown('<div class="section-title">Filtering</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="section-description">
        We removed 700 data points from <b>2018, 2019, 2020, 2021, and 2025</b>
    </div>""", unsafe_allow_html=True)

filtered_years = df.loc[df['FundingYear'].isin([2018, 2019, 2020, 2021, 2025])].copy()
st.dataframe(filtered_years[['FundingYear', 'ContractCost']], width='stretch')

st.info("""    
    These years contained either insufficient or incomplete data points for the year. The original creator of the dataset mentioned the corresponding
    timeframe for the dataset should be from **July 2022 to May 2025**. 
    """)

st.markdown('<div class="section-title">Final Dataset</div>', unsafe_allow_html=True)

col_a, col_b, col_c, col_d = st.columns(4, vertical_alignment="center")
with col_a:
    with st.container(height=130, border=True):
        st.metric("Original Rows", original_row_count)
with col_b:
    with st.container(height=130, border=True):
        st.metric("Rows After Cleaning", len(df_clean), delta=-rows_removed_total)
with col_c:
    with st.container(height=130, border=True):
        thing = len(df_clean.columns) - len(df.columns)
        st.metric("New Features Added", len(df_clean.columns) - len(df.columns), delta=thing)
with col_d:
    with st.container(height=130, border=True):
        st.metric("Columns Used", len(df_clean.columns))

st.info("Added Features Preview")
st.dataframe(
    df_clean[['ProjectId', 'Duration', 'BudgetDifference', 'BudgetVariance', 'RiskScore', 'IsSuspicious']].head(10),
    width='stretch'
)

st.info("Final Dataset Preview")
st.dataframe(df_clean, width='stretch')

st.markdown(
    """
    <div style="
        text-align: center;  
        font-size: 0.9rem;
        opacity: 0.7;
    ">
        <strong>Made with Streamlit by The J’s</strong>
    </div>
    """,
    unsafe_allow_html=True
)