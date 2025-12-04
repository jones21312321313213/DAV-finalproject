"""import streamlit as st


home_page = st.Page(
    page = "views/home.py",
    title = "Home",
    icon = ":material/account_circle:",
    default= True
)


data_page = st.Page(
    page = "views/data_exploration.py",
    title = "DATA",
    icon = ":material/business_center:",
)


analysis_page = st.Page(
    page = "views/analysis.py",
    title = "analysis",
    icon = ":material/business_center:",
)


conclusions_page = st.Page(   
    page = "views/conclusions.py",
    title = "conclusions",
    icon = ":material/business_center:",
)


pg = st.navigation(
    {
        "Home":[home_page],
        "Data":[data_page],
        "Analysis":[analysis_page],
        "Conclusions":[conclusions_page]
    }
)

#st.logo()
st.sidebar.text("Made by The J's")

pg.run()"""
import streamlit as st

# Define pages
home_page = st.Page(
    page="views/home.py",
    title="Home",
    icon=":material/account_circle:",
    default=True
)

# --- Data subsections ---
data_overview_page = st.Page(
    page="views/data_overview.py",
    title="Overview",
    icon=":material/insights:",
)

data_visualizations_page = st.Page(
    page="views/data_visualizations.py",
    title="Visualizations",
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
pg = st.navigation(
    {
        
        "Data": [data_overview_page, data_visualizations_page],
        "Analysis": [analysis_page],
        "Conclusions": [conclusions_page]
    }
)

st.sidebar.text("Made by The J's")

pg.run()
