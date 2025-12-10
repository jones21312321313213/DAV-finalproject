import streamlit as st
import plotly.express as px
from utils import (
    load_css, load_data, prep_data, get_filters,
    get_island_fig, get_region_fig, get_cost_hist_fig,
    get_project_type_fig, get_contractor_figs
)

st.set_page_config(layout="centered", page_title="Exploration")
load_css()

df = load_data()
clean_df = prep_data(df)
filtered_df = get_filters(clean_df)

st.markdown('<div class="title-card">Data exploration</div>', unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("No data matches your current filters. Please adjust the sidebar filters.")
else:
    # 1. GEOGRAPHIC DISTRIBUTION
    st.markdown('<div class="section-title">Geographic Distribution</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-container"><b>Project Distribution by Island Group</b></div>', unsafe_allow_html=True)
        island_chart_type = st.radio(
            "Visualization Style",
            ["Donut Chart", "Bar Chart"],
            key="island_toggle",
            horizontal=True,
            label_visibility="collapsed"
        )
        fig_island = get_island_fig(filtered_df, island_chart_type)
        if fig_island: st.plotly_chart(fig_island, width='stretch')
        else: st.info("No data available.")

    with col2:
        st.markdown('<div class="section-container"><b>Regional Distribution</b></div>', unsafe_allow_html=True)
        top_n_regions = st.slider("Show Top N Regions", min_value=5, max_value=17, value=10, key="region_slider")
        fig_region = get_region_fig(filtered_df, top_n_regions)
        if fig_region: st.plotly_chart(fig_region, width='stretch')
        else: st.info("No data available.")

    # 2. FINANCIAL DISTRIBUTION
    st.markdown('<div class="section-title">Cost Distribution</div>', unsafe_allow_html=True)

    c_hist1, c_hist2 = st.columns([0.7, 0.3], border=True, vertical_alignment="top")

    with c_hist2:
        st.markdown("""<div class="section-title" style="text-align: center; line-height: 34px">Histogram settings</div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        use_log = st.toggle("Logarithmic Scale", value=True, help="Switch to Log scale to see outliers better.")
        dist_type = st.radio("Distribution Type", ["Contract Cost", "Approved Budget"], horizontal=True, key="hist_toggle")
        bin_count = st.slider("Number of Bins", min_value=10, max_value=150, value=50, step=10)

    with c_hist1:
        fig_hist = get_cost_hist_fig(filtered_df, dist_type, bin_count, use_log)
        if fig_hist: st.plotly_chart(fig_hist, width='stretch')
        else: st.info("No data available.")

    # 3. PROJECT TYPES
    st.markdown('<div class="section-title">Project Types</div>', unsafe_allow_html=True)
    if not filtered_df.empty:
        with st.container(border=True, key="chart_container"):
            type_chart_style = st.radio("Chart Style", ["Bar Chart", "Pie Chart"], horizontal=True)

        fig_tow = get_project_type_fig(filtered_df, type_chart_style)
        if fig_tow:
            with st.container(border=True):
                st.plotly_chart(fig_tow, width='stretch')
        else:
            st.info("No project types found.")
    else:
        st.info("No project types found.")

    # 4. CONTRACTOR MARKET SHARE
    st.markdown('<div class="section-title">Contractor Participation</div>', unsafe_allow_html=True)
    fig_val, fig_vol = get_contractor_figs(filtered_df)
    with st.container(border=True):
        if fig_val: st.plotly_chart(fig_val, width='stretch')
        else: st.info("No contractor data available.")
    with st.container(border=True):
        if fig_vol: st.plotly_chart(fig_vol, width='stretch')
        else: st.info("No contractor data available.")

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