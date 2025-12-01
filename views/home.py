import streamlit as st
import pandas as pd



st.title("HOME PAGE")
st.header("Overview")

# temp rani ang bg 
page_bg = """
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1729179664855-9c068fec328d?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=870");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

[data-testid="stSidebar"] {
    background-color: rgba(255,255,255,0.15);
    backdrop-filter: blur(5px);
}
</style>
"""

st.markdown(page_bg, unsafe_allow_html=True)


st.write("""
This is floodcontrol data set

**Research Question:**  
which contractor company stole the most

**Selected Analysis Techniques:**  
- Anomaly detection  


**Dataset link:**  
https://www.kaggle.com/datasets/bwandowando/dpwh-flood-control-projects/data
""")


df = pd.read_csv("data_cleaning/cleaned_flood_data.csv")


st.header("Dataset Structure & Summary")


st.subheader("Dataset Preview")
st.dataframe(df.head())



st.subheader("Distinct Values per Column")
st.write(df.nunique())

st.subheader("Null Value Counts")
st.write(df.isnull().sum())


st.subheader("Dataset Dimensions")
st.write(f"Rows: {df.shape[0]}")
st.write(f"Columns: {df.shape[1]}")


st.subheader(" Column Names")
st.write(list(df.columns))


st.subheader("🔧 Cleaned Numeric Columns")
numeric_cols = ['ApprovedBudgetForContract', 'ContractCost', 'FundingYear']
existing_num_cols = [c for c in numeric_cols if c in df.columns]
st.write(df[existing_num_cols].dtypes)


st.subheader("Cleaned Dataset Preview")
st.dataframe(df)
