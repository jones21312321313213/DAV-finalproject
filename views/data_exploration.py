import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Flood Mitigation Projects - Data Exploration",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5em;
    font-weight: bold;
    color: #2E86AB;
    text-align: center;
    margin-bottom: 20px;
}
.description {
    font-size: 1.1em;
    line-height: 1.6;
    color: #333;
    margin-bottom: 20px;
}
.footer {
    text-align: center;
    font-size: 0.9em;
    color: #666;
    margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)

# Title and Introduction
st.markdown('<div class="main-header">Flood Mitigation Projects - Data Exploration</div>', unsafe_allow_html=True)

st.markdown("""
<div class="description">
Welcome to the Data Exploration section of the Flood Mitigation Projects Dashboard.  
Here you can explore the dataset through three dedicated subsections:
- **Overview**: Inspect raw data and descriptive statistics.  
- **Visualizations**: Explore charts and distributions by region, island, type of work, and costs.  
- **Analysis**: (coming soon or handled separately).  

Use the sidebar navigation to access each subsection.
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown('<div class="footer">---<br>Data Exploration hub. Navigate to Overview or Visualizations for detailed insights.</div>', unsafe_allow_html=True)
