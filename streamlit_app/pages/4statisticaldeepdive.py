import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.analysis.statistical_tests import sample_size_calculator

st.set_page_config(page_title="Statistical Deep Dive", page_icon="📊", layout="wide")

# Title
st.title("📊 Statistical Deep Dive")
st.markdown("### Comparing all experiments and exploring methodology")

st.markdown("---")

# Summary Comparison Table
st.markdown("## 📋 Experiments at a Glance")

summary_data = {
    'Experiment': [
        'Onboarding Flow',
        'AI Suggestions',
        'Pricing Page'
    ],
    'Metric Type': [
        'Continuous',
        'Continuous',
        'Binary'
    ],
    'Statistical Test': [
        "Welch's t-test",
        "Welch's t-test",
        'χ² test'
    ],
    'Sample Size': [
        '2,017',
        '2,008',
        '2,936'
    ],
    'Effect Size': [
        '-28.7%',
        '+57.3%',
        '+41.0%'
    ],
    'p-value': [
        '< 0.0001',
        '< 0.0001',
        '0.0243'
    ],
    'Significant (α=0.05)': [
        '✅',
        '✅',
        '✅'
    ],
    'Significant (Bonferroni)': [
        '✅',
        '✅',
        '❌'
    ],
    'Decision': [
        '🚢 Ship',
        '🚢 Ship',
        '⏸️ Re-run'
    ]
}

df_summary = pd.DataFrame(summary_data)
st.dataframe(df_summary, use_container_width=True, hide_index=True)

st.markdown("---")

# Multiple Testing Correction
st.markdown("## 🔬 Multiple Testing Correction")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### Why Bonferroni Correction?
    
    When running **multiple experiments simultaneously**, our risk of false positives increases:
    
    **The Problem:**
    - If α = 0.05, each test has a 5% chance of false positive
    - With 3 independent tests: P(at least one false positive) = 1 - (0.95)³ = **14.3%**
    - This is nearly 3× higher than our intended 5% rate!
    
    **The Solution (Bonferroni):**
    - Divide α by the number of tests: α_adjusted = 0.05 / 3 = **0.0167**
    - Now P(at least one false positive) ≈ 5% (as intended)
    
    **Trade-off:**
    - ✅ Controls false positives (Type I errors)
    - ❌ Requires larger sample sizes
    - ⚠️ More conservative (might miss real effects)
    
    **Our Results:**
    - Experiments 1 & 2: p < 0.0001 → Still significant ✅
    - Experiment 3: p = 0.0243 → Not significant after correction ❌
    """)

with col2:
    st.markdown("### Bonferroni Formula")
    st.latex(r"\alpha_{adjusted} = \frac{\alpha}{n_{tests}}")
    
    st.markdown("### Our Case")
    st.latex(r"\alpha_{adjusted} = \frac{0.05}{3} = 0.0167")
    
    st.markdown("### P-value Comparison")
    
    fig = go.Figure()
    
    p_values = [0.0001, 0.0001, 0.0243]
    experiments = ['Exp 1', 'Exp 2', 'Exp 3']
    colors = ['#28a745', '#28a745', '#fd7e14']
    
    fig.add_trace(go.Bar(
        x=experiments,
        y=p_values,
        marker_color=colors,
        text=[f"p={p:.4f}" for p in p_values],
        textposition='outside',
        textfont=dict(size=12)
    ))
    
    # Add threshold lines with better styling
    fig.add_hline(y=0.05, line_dash="dash", line_color="#0066cc", line_width=2,
                  annotation_text="α = 0.05 (uncorrected)", 
                  annotation_position="right")
    fig.add_hline(y=0.0167, line_dash="dash", line_color="#dc3545", line_width=2,
                  annotation_text="α = 0.0167 (Bonferroni)", 
                  annotation_position="right")
    
    # Add shaded regions
    fig.add_hrect(y0=0, y1=0.0167, fillcolor="green", opacity=0.1, 
                  layer="below", line_width=0)
    fig.add_hrect(y0=0.0167, y1=0.05, fillcolor="orange", opacity=0.1, 
                  layer="below", line_width=0)
    fig.add_hrect(y0=0.05, y1=0.06, fillcolor="red", opacity=0.1, 
                  layer="below", line_width=0)
    
    fig.update_layout(
        yaxis_title='p-value',
        yaxis_range=[0, 0.06],
        height=400,
        showlegend=False,
        yaxis=dict(
            tickformat='.4f',
            gridcolor='rgba(128,128,128,0.2)'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Simple Sample Size Calculator
st.markdown("## 🧮 Sample Size Calculator")

st.markdown("""
**Plan your experiments before running them!** This calculator tells you how many users 
you need to reliably detect an effect.
""")

st.info("""
💡 **Quick Guide:**
- **Baseline:** Your current metric value (e.g., 10% conversion rate)
- **MDE (Minimum Detectable Effect):** Smallest improvement you want to detect (e.g., +2%)
- **Power:** Probability of detecting a real effect (80% is standard)
- **Alpha (α):** False positive rate (5% is standard)
""")

# Input Section
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📊 Metric Settings")
    
    metric_type = st.radio(
        "What type of metric?",
        ["Conversion Rate", "Continuous Metric"],
        help="Conversion rate = % who take an action. Continuous = numbers like time, count, revenue"
    )
    
    if metric_type == "Conversion Rate":
        baseline = st.number_input(
            "Current Conversion Rate (%)",
            min_value=0.1,
            max_value=99.0,
            value=10.0,
            step=0.1,
            help="Example: If 10% of users convert, enter 10"
        ) / 100
        
        mde = st.number_input(
            "Effect You Want to Detect (%)",
            min_value=0.1,
            max_value=50.0,
            value=2.0,
            step=0.1,
            help="Example: To detect improvement from 10% to 12%, enter 2"
        ) / 100
        
        st.markdown(f"**Target Rate:** {baseline:.1%} → {baseline + mde:.1%}")
        
    else:
        baseline = st.number_input(
            "Current Average Value",
            min_value=1.0,
            value=100.0,
            step=1.0,
            help="Example: Average of 100 tasks per user"
        )
        
        mde_percent = st.number_input(
            "Effect You Want to Detect (%)",
            min_value=1.0,
            max_value=100.0,
            value=10.0,
            step=1.0,
            help="Example: To detect 10% improvement, enter 10"
        )
        
        mde = baseline * (mde_percent / 100)
        st.markdown(f"**Target Value:** {baseline:.1f} → {baseline + mde:.1f}")

with col2:
    st.markdown("### ⚙️ Statistical Settings")
    
    power = st.select_slider(
        "Statistical Power",
        options=[0.70, 0.75, 0.80, 0.85, 0.90],
        value=0.80,
        format_func=lambda x: f"{x:.0%}",
        help="80% is industry standard - means 80% chance of detecting a real effect"
    )
    
    alpha = st.select_slider(
        "Significance Level (α)",
        options=[0.01, 0.05, 0.10],
        value=0.05,
        format_func=lambda x: f"{x:.2%}",
        help="5% is standard - means 5% false positive rate"
    )
    
    num_tests = st.number_input(
        "Number of Experiments Running",
        min_value=1,
        max_value=10,
        value=1,
        help="If running multiple tests, we apply Bonferroni correction"
    )
    
    if num_tests > 1:
        adjusted_alpha = alpha / num_tests
        st.warning(f"**Bonferroni Correction Applied**  \nAdjusted α = {adjusted_alpha:.4f}")
        alpha_to_use = adjusted_alpha
    else:
        alpha_to_use = alpha

# Calculate Button
st.markdown("---")

if st.button("🔍 Calculate Sample Size", type="primary", use_container_width=True):
    try:
        result = sample_size_calculator(
            baseline_metric=baseline,
            mde=mde,
            alpha=alpha_to_use,
            power=power,
            metric_type='proportion' if metric_type == "Conversion Rate" else 'continuous'
        )
        
        st.markdown("---")
        st.markdown("## ✅ Results")
        
        # Display results
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "🎯 Per Variant",
                f"{result['required_sample_size_per_variant']:,}",
                help="Users needed in EACH group (control and treatment)"
            )
        
        with col2:
            st.metric(
                "👥 Total Users",
                f"{result['total_sample_size']:,}",
                help="Total users needed for the experiment"
            )
        
        with col3:
            if metric_type == "Conversion Rate":
                lift_pct = (mde / baseline) * 100
            else:
                lift_pct = mde_percent
            
            st.metric(
                "📈 Expected Lift",
                f"+{lift_pct:.1f}%",
                help="The improvement you're trying to detect"
            )
        
        # Interpretation
        st.success(f"""
        ### 🎯 What This Means
        
        To reliably detect a **{lift_pct:.1f}% improvement** with **{power:.0%} power** 
        and **{alpha:.1%} significance level**, you need:
        
        - **{result['required_sample_size_per_variant']:,}** users in control group
        - **{result['required_sample_size_per_variant']:,}** users in treatment group
        - **{result['total_sample_size']:,}** total users
        
        💡 **Run your experiment until you reach this sample size, then analyze the results.**
        """)
        
        # Time estimate helper
        with st.expander("⏱️ How long will this take?"):
            st.markdown("""
            **Estimate experiment duration:**
            
            If you get 1,000 users per week:
            - Your experiment will take approximately **{:.1f} weeks**
            
            If you get 500 users per week:
            - Your experiment will take approximately **{:.1f} weeks**
            
            💡 Adjust based on your actual traffic to plan timeline!
            """.format(
                result['total_sample_size'] / 1000,
                result['total_sample_size'] / 500
            ))
    
    except Exception as e:
        st.error(f"❌ Error calculating sample size: {str(e)}")

st.markdown("---")

# Quick Reference Examples
with st.expander("📖 Example Scenarios"):
    st.markdown("""
    ### Example 1: Testing a New Checkout Flow
    - **Metric:** Conversion rate
    - **Current:** 12% complete checkout
    - **Want to detect:** +2% improvement (to 14%)
    - **Result:** Need ~3,800 users total
    
    ### Example 2: Testing AI Suggestions
    - **Metric:** Tasks created per day
    - **Current:** 5 tasks/day average
    - **Want to detect:** +20% improvement (to 6 tasks/day)
    - **Result:** Need ~800 users total
    
    ### Example 3: Testing Pricing Page
    - **Metric:** Trial-to-paid conversion
    - **Current:** 8% convert
    - **Want to detect:** +3% improvement (to 11%)
    - **Result:** Need ~2,200 users total
    """)

st.markdown("---")

# Methodology Reference
st.markdown("## 📚 Methodology Reference")

tab1, tab2, tab3, tab4 = st.tabs(["T-Tests", "Chi-Square", "Effect Sizes", "Data Quality"])

with tab1:
    st.markdown("""
    ### Welch's T-Test (Independent Samples)
    
    **When to use:**
    - Comparing means of two independent groups
    - Continuous metrics (time, count, revenue, etc.)
    - Examples: time to first task, tasks created per day
    
    **Why Welch's instead of Student's t-test:**
    - Doesn't assume equal variances between groups
    - More robust in A/B testing where groups might differ
    
    **Formula:**
    """)
    
    st.latex(r"t = \frac{\bar{X}_2 - \bar{X}_1}{\sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}}}")
    
    st.markdown("""
    **What you need:**
    - X̄₁, X̄₂ = means of control and treatment
    - s₁, s₂ = standard deviations
    - n₁, n₂ = sample sizes
    
    **Assumptions:**
    - ✅ Independence: observations are independent
    - ✅ Approximately normal: data roughly bell-shaped (less critical with large samples)
    - ✅ Random assignment: users randomly assigned to variants
    
    **How to interpret:**
    - p < 0.05 → statistically significant difference
    - Report: mean difference, confidence interval, effect size
    """)

with tab2:
    st.markdown("""
    ### Chi-Square Test of Independence
    
    **When to use:**
    - Comparing proportions between two groups
    - Binary metrics (converted/not converted, clicked/didn't click)
    - Example: trial-to-paid conversion rate
    
    **Formula:**
    """)
    
    st.latex(r"\chi^2 = \sum \frac{(O_i - E_i)^2}{E_i}")
    
    st.markdown("""
    **Example contingency table:**
    ```
                 Converted   Not Converted   Total
    Control         120          880         1000
    Treatment       150          850         1000
    Total           270         1730         2000
    ```
    
    **Assumptions:**
    - ✅ Independence: observations are independent
    - ✅ Expected frequencies: E_i ≥ 5 for all cells
    - ✅ Random assignment
    
    **How to interpret:**
    - p < 0.05 → conversion rates significantly different
    - Report: absolute lift, relative lift, confidence interval
    """)

with tab3:
    st.markdown("""
    ### Effect Size (Cohen's d)
    
    **Why it matters:**
    - Statistical significance ≠ practical significance
    - Large samples can make tiny effects "significant"
    - Effect size tells you if the difference actually matters
    
    **Formula:**
    """)
    
    st.latex(r"d = \frac{\mu_2 - \mu_1}{\sigma_{pooled}}")
    
    st.markdown("""
    **Interpretation:**
    - |d| < 0.2: **Negligible** - effect too small to matter
    - 0.2 ≤ |d| < 0.5: **Small** - subtle but real effect
    - 0.5 ≤ |d| < 0.8: **Medium** - moderate effect
    - |d| ≥ 0.8: **Large** - substantial effect
    
    **Our Experiments:**
    - Experiment 1: d = -0.68 → Medium-large (13 min faster)
    - Experiment 2: d = 0.82 → Large (+57% more tasks)
    
    **Pro Tip for Stakeholders:**
    Don't just report Cohen's d! Translate to business terms:
    - ❌ "Cohen's d = -0.68"
    - ✅ "Users complete onboarding 28% faster, saving 13 minutes on average"
    """)

with tab4:
    st.markdown("""
    ### Sample Ratio Mismatch (SRM)
    
    **What is it:**
    A data quality check that verifies your randomization worked correctly.
    If you expect 50/50 split but observe 60/40, something went wrong.
    
    **Why it matters:**
    - 🚨 Indicates bugs in randomization code
    - 🚨 Biased assignment invalidates all results
    - 🚨 Can't trust experiment conclusions if SRM detected
    
    **Common causes:**
    - Bot traffic hitting one variant more
    - Implementation bug in assignment logic
    - Browser/device compatibility issues
    - Caching problems
    
    **Our threshold:**
    - α = 0.001 (very strict)
    - Only flag if we're highly confident there's a problem
    
    **What to do if SRM detected:**
    1. ❌ **DO NOT SHIP** based on these results
    2. 🔍 Investigate randomization implementation
    3. 🐛 Fix the bug
    4. 🔄 Re-run the experiment
    
    **In our experiments:**
    ✅ All three experiments passed SRM check
    
    ---
    
    ### Other Data Quality Checks
    
    **Guardrail Metrics:**
    - Monitor metrics you DON'T want to move
    - Example: New onboarding shouldn't hurt retention
    - Check these don't degrade even if primary metric improves
    
    **Variance Ratio:**
    - Compare standard deviation between control and treatment
    - Large differences might indicate data quality issues
    - Rule of thumb: ratio should be 0.5 to 2.0
    """)

st.markdown("---")

# Footer
st.markdown("""
<div style='text-align: center; color: #888; padding: 2rem;'>
    <p><strong>Statistical Methods:</strong> Welch's t-test • Chi-square test • Bonferroni correction • Cohen's d</p>
    <p><strong>Tech Stack:</strong> Python • SciPy • NumPy • Pandas • Plotly • Streamlit</p>
</div>
""", unsafe_allow_html=True)