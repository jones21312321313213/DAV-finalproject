import streamlit as st

# Define pages
home_page = st.Page(
    page="views/overview.py",
    title="Overview",
    icon=":material/account_circle:",
    default=True
)

# --- Data subsections ---
preparation_page = st.Page(
    page="views/preparation.py",
    title="Preparation",
    icon=":material/insights:",
)

data_exploration_page = st.Page(
    page="views/exploration.py",
    title="Exploration",
    icon=":material/bar_chart:",
)

# Other sections
analysis_page = st.Page(
    page="views/analysis.py",
    title="Analysis",
    icon=":material/business_center:",
)

conclusions_page = st.Page(
    page="views/conclusions.py",
    title="Conclusions",
    icon=":material/business_center:",
)

# Navigation with collapsible dropdown for Data
pg = st.navigation({
    "Project Info": [home_page, conclusions_page],
    "Data Pipeline": [preparation_page, data_exploration_page, analysis_page]
})

pg.run()


with st.sidebar:
    st.markdown("""
        <div class="custom-box" style='margin-bottom: 15px;'>
                <b>Authors: The J's</b>
        </div>
    """, unsafe_allow_html=True)
    st.info("Joshua Arco")
    st.info("Jon Mari Casipong")
    st.info("John Kevin Muyco")
    st.info("Jive Tyler Revalde")
    st.info("John Michael Sayson")
