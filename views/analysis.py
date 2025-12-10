import streamlit as st
from streamlit_folium import st_folium
import streamlit.components.v1 as components
from utils import (
    load_css, load_data, prep_data, get_filters, create_map,
    plot_benfords_law, plot_bid_variance, plot_clustering, plot_top_contractors,
    TypeOfWork_full_color
)

st.set_page_config(layout="centered", page_title="Analysis")
load_css()

# Initialization for map state
CENTER = (11.891783, 122.419922)
if "center" not in st.session_state:
    st.session_state["center"] = CENTER
if "zoom" not in st.session_state:
    st.session_state["zoom"] = 6

df = load_data()
clean_df = prep_data(df)
filtered_df = get_filters(clean_df)

st.markdown("""<div class="title-card">Analysis</div>""", unsafe_allow_html=True)

if filtered_df.empty:
    st.warning("No data matches filters.")
else:
    st.markdown("""
    <div class="section-title">Geospatial Analysis</div>
    """, unsafe_allow_html=True)

    total_cost = (filtered_df['ContractCost'].sum())
    suspicious_df = filtered_df[filtered_df['IsSuspicious']]
    suspicious_val = suspicious_df['ContractCost'].sum()

    c1, c2= st.columns(2)
    c1.metric("Total Contract Value", f"₱{total_cost:,.0f}", border=True)
    c2.metric("Suspicious Capital", f"₱{suspicious_val:,.0f}", help="Projects with cost > 99% of budget", border=True)
    c1.metric("Flagged Projects", f"{len(suspicious_df)}", delta_color="inverse", border=True)
    c2.metric("Projects Found", f"{len(filtered_df)}", border=True)

    m = create_map(filtered_df, st.session_state["center"], st.session_state["zoom"])
    st_folium(m, height=500, returned_objects=[], width=1000)

    with st.expander("Type of Work Legend"):
        html = """
        <div style="font-family: 'Segoe UI', Roboto, sans-serif;">
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; font-size:14px;">
        """
        for work_type, color in TypeOfWork_full_color.items():
            html += f'''
              <div style="display:flex; align-items:center;">
                <div style="width:14px; height:14px; background:{color}; border:1px solid #444; margin-right:8px;"></div>
                <div style="line-height:14px; color: white">{work_type}</div>
              </div>
            '''
        html += "</div></div>"
        components.html(html, height=300, scrolling=True)

    with st.expander("Map Susceptibility Legend"):
        c1, c2 = st.columns(2, vertical_alignment="center")

        with c1:
            st.markdown("**Flood Susceptibility**")
            st.markdown("""
            <div style="font-size: 12px; margin-bottom: 5px;">
                <div style="margin-bottom: 5px;">
                    <span style="display:inline-block; width:12px; height:12px; background-color:#002673; border:1px solid #ccc;"></span> Very High Susceptibility
                </div>
                <div style="margin-bottom: 5px;">
                    <span style="display:inline-block; width:12px; height:12px; background-color:#5900ff; border:1px solid #ccc;"></span> High Susceptibility
                </div>
                <div style="margin-bottom: 5px;">
                    <span style="display:inline-block; width:12px; height:12px; background-color:#b045ff; border:1px solid #ccc;"></span> Moderate Susceptibility
                </div>
                <div style="margin-bottom: 5px;">
                    <span style="display:inline-block; width:12px; height:12px; background-color:#e3d1ff; border:1px solid #ccc;"></span> Low Susceptibility
                </div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            st.markdown("**Landslide Susceptibility**")
            st.markdown("""
                    <div style="font-size: 12px;">
                        <div style="margin-bottom: 5px;">
                            <span style="display:inline-block; width:12px; height:12px; background-color:#902400; border:1px solid #ccc;"></span> Very High Susceptibility
                        </div>
                        <div style="margin-bottom: 5px;">
                            <span style="display:inline-block; width:12px; height:12px; background-color: red; border:1px solid #ccc;"></span> High Susceptibility
                        </div>
                        <div style="margin-bottom: 5px;">
                            <span style="display:inline-block; width:12px; height:12px; background-color: green ; border:1px solid #ccc;"></span> Moderate Susceptibility
                        </div>
                        <div style="margin-bottom: 5px;">
                            <span style="display:inline-block; width:12px; height:12px; background-color: yellow ; border:1px solid #ccc;"></span> Low Susceptibility
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    if not filtered_df.empty:
        top_type = filtered_df['TypeOfWork'].mode()[0]
        st.info(f"Most Common Work:\n**{top_type}**")

        avg_dur = filtered_df['Duration'].mean()
        st.success(f"Avg Duration:\n**{avg_dur:.0f} Days**")

        max_proj = filtered_df.loc[filtered_df['ContractCost'].idxmax()]
        st.warning(f"Most Expensive:\n**{max_proj['ProjectName'][:50]}...**\n(₱{max_proj['ContractCost']/1e6:.1f} M)")

    st.markdown("### Forensic Analysis Dashboard")

    tab1, tab2, tab3 = st.tabs(["Fraud Detection", "Operational Efficiency", "Market Analysis"])

    with tab1:
        st.markdown("**Benford's Law** - Detects artificial numbers.")
        st.markdown("*If the blue bars deviate significantly from the orange bars (especially for digits 7-9), the costs may be manipulated.*")
        fig_benford = plot_benfords_law(filtered_df)
        if fig_benford: st.pyplot(fig_benford)

        st.divider()
        st.markdown("**Bid Variance Screening** - Detects 'Ceiling Bidding'.")
        st.markdown("*A massive spike between 0% and 0.1% suggests contractors know the budget ceiling and are bidding just below it.*")
        fig_var = plot_bid_variance(filtered_df)
        st.pyplot(fig_var)

    with tab2:
        st.markdown("**Cluster Analysis (K-Means)** - Groups projects by Cost & Time.")
        st.markdown("*Look for outliers: High Cost projects with Short Duration (Top-Left) are red flags.*")
        fig_cluster = plot_clustering(filtered_df)
        if fig_cluster:
            st.pyplot(fig_cluster)
        else:
            st.warning("Not enough data points for clustering.")

    with tab3:
        st.markdown("**Contractor Dominance** - Who controls the market?")
        fig_market = plot_top_contractors(filtered_df)
        st.pyplot(fig_market)

    with st.expander("View Raw Data Table"):
        st.dataframe(filtered_df[['ProjectId', 'ProjectName', 'Contractor', 'ContractCost', 'ApprovedBudgetForContract', 'BudgetVariance', 'Duration', 'StartDate']], width='stretch')


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