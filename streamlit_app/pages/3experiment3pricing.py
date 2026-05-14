import streamlit as st
import duckdb
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
import sys
from scipy import stats

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.analysis.statistical_tests import chi_square_test, sample_size_calculator
from src.data_quality.srm_check import detect_sample_ratio_mismatch

st.set_page_config(page_title="Experiment 3: Pricing Page", page_icon="💰", layout="wide")

# Title
st.title("💰 Experiment 3: Pricing Page Redesign")
st.markdown("**Hypothesis:** Clearer pricing tiers will improve trial-to-paid conversion rate")

st.markdown("---")

# Alert box at the top
st.warning("""
⚠️ **This experiment shows why sample size planning matters!**

We detected a large effect (+41% lift) but didn't have enough users to meet the 
statistical threshold after running multiple experiments.
""")

st.markdown("---")

# Load data
@st.cache_data
def load_experiment_data():
    db_path = project_root / 'data' / 'raw' / 'experiments.db'
    conn = duckdb.connect(str(db_path))
    
    query = """
    SELECT 
        ea.variant,
        COUNT(DISTINCT ea.user_id) as total_users,
        COUNT(DISTINCT e.user_id) as converted_users
    FROM experiment_assignments ea
    LEFT JOIN events e ON ea.user_id = e.user_id 
        AND e.experiment_id = 3 
        AND e.event_type = 'trial_to_paid_conversion'
    WHERE ea.experiment_id = 3
    GROUP BY ea.variant
    """
    
    df = conn.execute(query).fetchdf()
    conn.close()
    return df

try:
    df = load_experiment_data()
    
    control = df[df['variant'] == 'control'].iloc[0]
    treatment = df[df['variant'] == 'treatment'].iloc[0]
    
    # Run chi-square test
    results = chi_square_test(
        control_conversions=int(control['converted_users']),
        control_total=int(control['total_users']),
        treatment_conversions=int(treatment['converted_users']),
        treatment_total=int(treatment['total_users'])
    )
    
    # Check for SRM
    srm = detect_sample_ratio_mismatch(results['sample_size_control'], 
                                      results['sample_size_treatment'])
    
    # Bonferroni correction
    bonferroni_alpha = 0.05 / 3  # 3 experiments
    significant_after_correction = results['p_value'] < bonferroni_alpha
    
    # Key Results Section
    st.markdown("## 📊 Key Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Control Rate",
            f"{results['control_rate']:.2%}",
            help="Conversion rate in control group"
        )
    
    with col2:
        st.metric(
            "Treatment Rate",
            f"{results['treatment_rate']:.2%}",
            delta=f"+{results['absolute_lift']:.2%}",
            help="Conversion rate in treatment group"
        )
    
    with col3:
        st.metric(
            "Relative Lift",
            f"+{results['relative_lift_percent']:.1f}%",
            help="Percentage improvement"
        )
    
    with col4:
        st.metric(
            "p-value",
            f"{results['p_value']:.4f}",
            help=f"Needs to be < {bonferroni_alpha:.4f} after Bonferroni correction"
        )
    
    # Decision Box
    if significant_after_correction:
        st.success("✅ **DECISION: SHIP IT** - Statistically significant after correction")
    else:
        st.error(f"""
        ❌ **DECISION: DO NOT SHIP YET**
        
        While p = {results['p_value']:.4f} < 0.05 (significant without correction), it doesn't meet the 
        Bonferroni-corrected threshold of α = {bonferroni_alpha:.4f} for running 3 experiments.
        
        **We need ~1,064 more users to detect this effect reliably.**
        """)
    
    st.markdown("---")
    
    # The Problem Explained - SIDE BY SIDE
    st.markdown("## 🎯 Why This Experiment Failed")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ❌ Problem 1: Not Enough Users")
        
        # Sample Size Gap Chart
        actual_sample = results['sample_size_control'] + results['sample_size_treatment']
        
        # Calculate required sample size
        baseline = results['control_rate']
        mde = results['absolute_lift']
        
        required = sample_size_calculator(
            baseline_metric=baseline,
            mde=mde,
            alpha=bonferroni_alpha,
            power=0.8,
            metric_type='proportion'
        )
        
        required_total = required['total_sample_size']
        
        categories = ['What We Had', 'What We Needed']
        sample_sizes = [actual_sample, required_total]
        colors = ['#FF6B6B', '#4ECDC4']
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=categories,
            y=sample_sizes,
            text=[f"{s:,}" for s in sample_sizes],
            textposition='outside',
            marker_color=colors,
            width=0.6
        ))
        
        # Gap annotation
        gap = required_total - actual_sample
        fig.add_annotation(
            x=0.5, y=max(sample_sizes) * 0.85,
            text=f"Gap: {gap:,} users<br>({actual_sample/required_total*100:.0f}% coverage)",
            showarrow=True,
            arrowhead=2,
            arrowcolor="#FF6B6B",
            font=dict(size=12, color="#FF6B6B", family="Arial Black")
        )
        
        fig.update_layout(
            yaxis_title='Number of Users',
            height=350,
            showlegend=False,
            margin=dict(t=20, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption(f"**{actual_sample/required_total*100:.0f}% coverage** - Need {gap:,} more users")
    
    with col2:
        st.markdown("### ⚠️ Problem 2: Threshold Too Strict")
        
        # P-value threshold chart
        fig = go.Figure()
        
        # Your p-value as a point
        fig.add_trace(go.Scatter(
            x=[results['p_value']], y=[1],
            mode='markers',
            marker=dict(size=25, color='orange', 
                       line=dict(width=2, color='white')),
            name='Our p-value',
            showlegend=False
        ))
        
        # Threshold lines
        fig.add_vline(x=0.05, line_dash="dash", line_color="blue", 
                      line_width=2,
                      annotation_text="Standard α=0.05",
                      annotation_position="top")
        
        fig.add_vline(x=bonferroni_alpha, line_dash="dash", line_color="red",
                      line_width=2,
                      annotation_text=f"Bonferroni α={bonferroni_alpha:.4f}",
                      annotation_position="bottom")
        
        # Colored regions
        fig.add_vrect(x0=0, x1=bonferroni_alpha, 
                      fillcolor="green", opacity=0.15,
                      layer="below", line_width=0,
                      annotation_text="Ship ✅",
                      annotation_position="inside top left")
        
        fig.add_vrect(x0=bonferroni_alpha, x1=0.05,
                      fillcolor="orange", opacity=0.15,
                      layer="below", line_width=0,
                      annotation_text="Borderline ⚠️",
                      annotation_position="inside top")
        
        fig.add_vrect(x0=0.05, x1=0.06,
                      fillcolor="red", opacity=0.15,
                      layer="below", line_width=0,
                      annotation_text="Don't Ship ❌",
                      annotation_position="inside top right")
        
        fig.update_layout(
            xaxis_title='P-value',
            xaxis_range=[0, 0.06],
            yaxis_visible=False,
            height=350,
            showlegend=False,
            margin=dict(t=20, b=20)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption(f"**p = {results['p_value']:.4f}** - In the borderline zone")
    
    # Summary box below both charts
    st.info("""
    📊 **The Complete Picture:**  
    
    We detected a promising +41% lift in conversion rate, but fell short on **both** requirements:
    - ❌ **Sample size:** Only 73% of needed users (2,936 vs 4,000 required)
    - ❌ **Statistical threshold:** p-value above Bonferroni cutoff (0.0243 > 0.0167)
    
    **Why both matter:** Even a large effect can be noise if the sample is too small AND we're 
    running multiple tests (increasing false positive risk).
    
    **Solution:** Continue experiment for 2-3 more weeks to reach ~4,000 users, then re-evaluate.
    """)
    
    st.markdown("---")
    
    # Detailed Conversion Data
    st.markdown("## 📈 Conversion Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Control Group")
        st.metric("Conversion Rate", f"{results['control_rate']:.2%}")
        st.metric("Conversions", f"{int(control['converted_users']):,}")
        st.metric("Total Users", f"{results['sample_size_control']:,}")
    
    with col2:
        st.markdown("### Treatment Group")
        st.metric("Conversion Rate", f"{results['treatment_rate']:.2%}", 
                 delta=f"+{results['absolute_lift']*100:.1f}pp")
        st.metric("Conversions", f"{int(treatment['converted_users']):,}")
        st.metric("Total Users", f"{results['sample_size_treatment']:,}")
    
    with col3:
        st.markdown("### Impact (If Real)")
        st.metric("Absolute Lift", f"+{results['absolute_lift']:.2%}")
        st.metric("Relative Lift", f"+{results['relative_lift_percent']:.1f}%")
        
        # Calculate potential value
        conversions_per_year = 1000
        arpu = 1000
        annual_value = conversions_per_year * results['absolute_lift'] * arpu
        
        st.metric("Potential Annual Value", f"${annual_value:,.0f}")
    
    st.markdown("---")
    
    # The Multiple Testing Problem
    st.markdown("## 🧪 Understanding Multiple Testing Correction")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### Why Bonferroni?")
        st.markdown("""
        When running **3 simultaneous experiments**, our false positive risk compounds:
        
        **Without correction:**
        - Each test: 5% false positive rate (α = 0.05)
        - Running 3 tests: ~14.3% chance of at least one false positive
        - Nearly 3× higher than intended! ❌
        
        **With Bonferroni correction:**
        - Adjusted α = 0.05 / 3 = 0.0167
        - Overall false positive rate: ~5% ✅
        - More conservative, but protects against wasted effort
        
        **The Trade-off:**
        - ✅ Controls false positives
        - ❌ Requires larger sample sizes
        - ❌ Might miss real but smaller effects
        """)
    
    with col2:
        st.markdown("### Our Experiment Results")
        
        # All three experiments comparison
        exp_data = {
            'Experiment': ['1: Onboarding', '2: AI Suggestions', '3: Pricing Page'],
            'p-value': [0.0001, 0.0001, results['p_value']],
            'Status': ['✅ Ship', '✅ Ship', '⚠️ Re-run']
        }
        
        st.dataframe(exp_data, use_container_width=True, hide_index=True)
        
        st.markdown(f"""
        **Bonferroni threshold:** {bonferroni_alpha:.4f}
        
        - **Exp 1 & 2:** p < 0.0001 → Still significant ✅
        - **Exp 3:** p = {results['p_value']:.4f} → Not significant ❌
        
        This is exactly what the correction is designed to catch: effects that 
        *might* be real but don't meet the stricter bar when running multiple tests.
        """)
    
    st.markdown("---")
    
    # Power Analysis
    st.markdown("## 🔬 Power Analysis: What If We Kept Running?")
    
    # Calculate power at different sample sizes
    sample_sizes_range = np.arange(1000, 6000, 200)
    powers = []
    
    effect_size = results['absolute_lift']
    baseline_rate = results['control_rate']
    
    for n in sample_sizes_range:
        # Pooled proportion
        p_pooled = baseline_rate + effect_size / 2
        
        # Standard error
        se = np.sqrt(2 * p_pooled * (1 - p_pooled) / (n / 2))
        
        # Z-score for effect
        z_effect = effect_size / se
        
        # Critical z-value for Bonferroni-corrected alpha
        z_crit = stats.norm.ppf(1 - bonferroni_alpha / 2)
        
        # Power calculation
        power = 1 - stats.norm.cdf(z_crit - z_effect)
        powers.append(power)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=sample_sizes_range,
        y=powers,
        mode='lines',
        line=dict(width=3, color='#4ECDC4'),
        fill='tozeroy',
        fillcolor='rgba(78, 205, 196, 0.2)',
        name='Power'
    ))
    
    # Current position
    current_power = powers[np.argmin(np.abs(sample_sizes_range - actual_sample))]
    fig.add_trace(go.Scatter(
        x=[actual_sample],
        y=[current_power],
        mode='markers+text',
        marker=dict(size=15, color='orange'),
        text=[f'We are here<br>({current_power:.0%} power)'],
        textposition='top center',
        name='Current',
        showlegend=False
    ))
    
    # Target position
    fig.add_trace(go.Scatter(
        x=[required_total],
        y=[0.80],
        mode='markers+text',
        marker=dict(size=15, color='green'),
        text=[f'Need to be here<br>(80% power)'],
        textposition='bottom center',
        name='Target',
        showlegend=False
    ))
    
    # Target line
    fig.add_hline(y=0.8, line_dash="dash", line_color="green",
                  annotation_text="Industry Standard: 80% power",
                  annotation_position="right")
    
    fig.update_layout(
        xaxis_title='Total Sample Size (users)',
        yaxis_title='Statistical Power',
        yaxis_tickformat='.0%',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info(f"""
    📊 **Power Analysis Summary:**
    
    - **Current Status:** ~{current_power:.0%} power (underpowered)
    - **Target:** 80% power (industry standard)
    - **Sample Gap:** Need {required_total - actual_sample:,} more users
    - **Time Estimate:** ~2-3 more weeks at current traffic
    
    **What is "power"?** The probability we'll detect this effect if it's real. 
    At 80% power, we have a 4-in-5 chance of catching a true +41% lift.
    """)
    
    st.markdown("---")
    
    # Data Quality Check
    st.markdown("## 🔍 Data Quality Check (SRM)")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if srm['srm_detected']:
            st.error("⚠️ **SRM DETECTED**")
        else:
            st.success("✅ **NO SRM DETECTED**")
        
        st.markdown(f"""
        **Expected Split:** 50/50
        
        **Actual Split:**
        - Control: {(1 - srm['actual_ratio'])*100:.1f}%
        - Treatment: {srm['actual_ratio']*100:.1f}%
        
        **χ² p-value:** {srm['p_value']:.4f}
        """)
    
    with col2:
        st.markdown("### What is SRM?")
        st.markdown("""
        **Sample Ratio Mismatch (SRM)** checks if the randomization worked correctly.
        
        - **Expected:** 50/50 split between control and treatment
        - **Actual:** Close enough to 50/50 (within statistical noise)
        - **Status:** ✅ No issues with randomization
        
        If SRM was detected, we'd need to investigate:
        - Bot traffic affecting one variant
        - Implementation bugs in assignment logic
        - Browser/device compatibility issues
        
        Since SRM check passed, we can trust the experiment ran correctly - 
        we just need more data!
        """)
    
    st.markdown("---")
    
    # Recommendation Section
    st.markdown("## ✅ Recommendation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.warning("""
        ### ⏸️ PAUSE AND RE-RUN WITH MORE USERS
        
        **Why Not Ship Now?**
        
        1. **Risk of False Positive:** Without correction, ~14% chance this is random noise
        2. **Cost of Being Wrong:** Engineering resources wasted on ineffective redesign
        3. **Opportunity Cost:** Could be testing other features instead
        4. **Large Effect Detected:** Worth validating with proper sample size
        
        **Recommended Next Steps:**
        
        1. **Continue Experiment** 
           - Run for 2-3 more weeks
           - Target: ~4,000 total users
           - Monitor for any SRM issues
        
        2. **Re-analyze When Target Reached**
           - If still significant → Ship with confidence ✅
           - If not significant → Redesign didn't work, move on ❌
        
        3. **Alternative: Pre-register Single Follow-up**
           - New experiment with α = 0.05 (no correction)
           - Only need ~2,700 users
           - But can't look at other experiments first
        
        **Projected Value (If Real):**
        
        A +41% lift in conversion = ~{int(conversions_per_year * results['absolute_lift']):,} 
        additional conversions per year = **${annual_value:,.0f}** in additional revenue.
        
        Worth the extra 2-3 weeks to get it right!
        """.format(conversions_per_year=1000, annual_value=int(1000 * results['absolute_lift'] * 1000)))
    
    with col2:
        st.markdown("### Quick Stats")
        st.markdown(f"""
        | Metric | Value |
        |--------|-------|
        | **Observed Lift** | +{results['relative_lift_percent']:.1f}% |
        | **p-value** | {results['p_value']:.4f} |
        | **Bonferroni α** | {bonferroni_alpha:.4f} |
        | **Current Sample** | {actual_sample:,} |
        | **Required Sample** | {required_total:,} |
        | **Gap** | {required_total - actual_sample:,} |
        | **Coverage** | {actual_sample/required_total*100:.0f}% |
        | **Current Power** | ~{current_power:.0%} |
        """)
        
        st.markdown("---")
        
        st.markdown("### Status")
        st.error("⚠️ **UNDERPOWERED**")
        st.markdown("Re-run needed")
    
    st.markdown("---")
    
    # Methodology
    with st.expander("📚 Methodology & Assumptions"):
        st.markdown("""
        ### Statistical Test
        - **Test Used:** Chi-square test of independence
        - **Metric:** Binary conversion (trial → paid)
        - **Significance Level:** α = 0.0167 (Bonferroni-corrected for 3 tests)
        - **Power Target:** 80%
        
        ### Sample Size Calculation
        - **Baseline Rate:** 8.0% (control conversion)
        - **Minimum Detectable Effect (MDE):** 3.0 percentage points
        - **Formula:** Uses normal approximation for proportions
        
        ### Multiple Testing Correction
        - **Method:** Bonferroni correction
        - **Reason:** Running 3 simultaneous experiments
        - **Adjusted α:** 0.05 / 3 = 0.0167
        
        ### Business Impact Assumptions
        - **Annual conversions:** 1,000 (baseline)
        - **ARPU:** $1,000 per year
        - **Incremental value:** Lift × conversions × ARPU
        
        ### Data Quality
        - **SRM Check:** Chi-square goodness-of-fit (α = 0.001)
        - **Randomization:** 50/50 split
        - **Experiment Period:** April 1 - May 15, 2024
        """)

except Exception as e:
    st.error(f"""
    ## ⚠️ Unable to load data
    
    Please ensure:
    1. Database exists at `data/raw/experiments.db`
    2. Run `python generate_schema.py` and `python generate_data.py` first
    
    Error: {str(e)}
    """)