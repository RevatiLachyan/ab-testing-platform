import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

st.set_page_config(
    page_title="A/B Testing Platform",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .big-metric {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.title(" A/B Testing Platform")
st.markdown("### End-to-end experimentation with statistical rigor")

st.markdown("")

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Experiments Run", "3", delta="All Completed")

with col2:
    st.metric("Users Tested", "10,000", delta="+4,025 in tests")

with col3:
    st.metric("Features Shipped", "2", delta="After correction")

with col4:
    st.metric("Projected Value", "$3.9M", delta="Annual impact")

st.markdown("---")

# Experiment Results Cards
st.markdown("##  Experiment Results")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### ✅ Experiment 1")
    st.markdown("**New Onboarding Flow**")
    st.markdown("**-28.7%** time to first task")
    st.markdown("*13 minutes saved per user*")
    st.success("🟢 SHIP IT")

with col2:
    st.markdown("### ✅ Experiment 2")
    st.markdown("**AI Task Suggestions**")
    st.markdown("**+57.3%** tasks created")
    st.markdown("*1.6 more tasks per day*")
    st.success("🟢 SHIP IT")

with col3:
    st.markdown("### ⚠️ Experiment 3")
    st.markdown("**Pricing Page Redesign**")
    st.markdown("**+41%** conversion lift")
    st.markdown("*Needs 1,063 more users*")
    st.warning("⚠️ UNDERPOWERED")

st.markdown("---")

# What's Inside
st.markdown("##  What's Inside")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Statistical Rigor
    - T-tests and χ² tests with effect sizes
    - Multiple testing correction (Bonferroni)
    - Sample Ratio Mismatch (SRM) detection
    - Power analysis and sample size calculations
    """)

with col2:
    st.markdown("""
    ### Business Translation
    - Stats → dollar impact for stakeholders
    - Clear ship/no-ship recommendations
    - Data quality validation built-in
    - Interactive analysis tools
    """)

st.info(" **Navigate using the sidebar** to explore individual experiments and statistical deep dives")

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #888; padding: 1rem;'>
    <p><strong>Tech Stack:</strong> Python • DuckDB • SciPy • Streamlit • Plotly</p>
</div>
""", unsafe_allow_html=True)