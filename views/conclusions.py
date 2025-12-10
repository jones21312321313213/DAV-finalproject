import streamlit as st
from utils import load_css

st.set_page_config(layout="centered", page_title="Conclusions")
load_css()

st.markdown('<div class="title-card">Conclusions & Recommendations</div>', unsafe_allow_html=True)

# Executive Summary Box
st.markdown("""
    <div>
        <div class="section-title">Summary</div>
        <div class="custom-box" style='margin-bottom: 10px;'>
            <b>The analysis reveals significant regional disparities in funding, with a concentration of capital in Luzon.</b>
        </div>
        <div class="custom-box" style='margin-bottom: 10px;'>
            <b>Forensic markers indicate potential non-competitive bidding practices in specific clusters, where contract costs align suspiciously 
    close to budget ceilings.</b>
        </div>
        <div class="custom-box" style='margin-bottom: 10px;'>
            <b>Market analysis further identifies a risk of oligopoly, with a few contractors dominating the sector.</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("### Key Insights")

    with st.expander("Geospatial Disparity", expanded=True):
        st.write("""
            * **Luzon Bias:** High-value projects are heavily concentrated in NCR and Region III.
            * **Fragmentation:** Visayas and Mindanao receive a high volume of projects, but they are significantly smaller in scale/cost, suggesting a fragmented approach to flood control.
            """)

    with st.expander("2. Forensic Flags (Corruption Risk)", expanded=True):
        st.write("""
            * **Ceiling Bidding:** A distinct cluster of projects has a `RiskScore > 0.99`. This lack of variance between Budget and Cost suggests potential collusion or lack of competition.
            * **Cost Anomalies:** Outlier detection found projects with extremely high costs but suspiciously short durations, warranting physical audits.
            """)

with col2:
    st.markdown("### Recommendations")

    with st.expander("Policy & Auditing", expanded=True):
        st.write("""
            * **Automated Flagging:** Implement a system that auto-flags bids within 1% of the budget ceiling.
            * **Market Entry:** Encourage more competition to break the oligopoly of top contractors.
            """)

    with st.expander("Data Governance", expanded=True):
        st.write("""
            * **Mandatory Reporting:** Enforce strict encoding of `ActualCompletionDate`. Missing data hides delays.
            * **Standardization:** Standardize project naming conventions to allow for better NLP analysis of project scopes.
            """)

st.divider()
st.markdown("""
    <div style="text-align: center; color: #666; font-style: italic;">
        "Data science does not just analyze numbers; it enforces accountability."
    </div>
    """, unsafe_allow_html=True)
