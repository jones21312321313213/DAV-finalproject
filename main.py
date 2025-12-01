import streamlit as st


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

pg.run()