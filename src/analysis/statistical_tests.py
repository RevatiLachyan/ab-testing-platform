import numpy as np
from scipy import stats
from typing import Dict, Tuple
import warnings

def ttest_independent(control_data: np.ndarray, treatment_data: np.ndarray, 
                     alpha: float = 0.05) -> Dict:
        # Calculate means
    control_mean = np.mean(control_data)
    treatment_mean = np.mean(treatment_data)
    
    # Perform t-test (Welch's t-test - doesn't assume equal variances)
    statistic, p_value = stats.ttest_ind(treatment_data, control_data, equal_var=False)
    
    # Calculate effect size (Cohen's d)
    pooled_std = np.sqrt((np.var(control_data) + np.var(treatment_data)) / 2)
    cohens_d = (treatment_mean - control_mean) / pooled_std if pooled_std > 0 else 0
    
    # Calculate confidence interval for the difference
    diff = treatment_mean - control_mean
    se_diff = np.sqrt(np.var(treatment_data)/len(treatment_data) + 
                      np.var(control_data)/len(control_data))
    
    # Use t-distribution critical value
    df = len(control_data) + len(treatment_data) - 2
    t_critical = stats.t.ppf(1 - alpha/2, df)
    ci_lower = diff - t_critical * se_diff
    ci_upper = diff + t_critical * se_diff
    
    # Calculate relative change percentage
    relative_change = ((treatment_mean - control_mean) / control_mean * 100) if control_mean != 0 else 0
    
    return {
        'statistic': statistic,
        'p_value': p_value,
        'significant': p_value < alpha,
        'control_mean': control_mean,
        'treatment_mean': treatment_mean,
        'control_std': np.std(control_data),
        'treatment_std': np.std(treatment_data),
        'effect_size_cohens_d': cohens_d,
        'confidence_interval': (ci_lower, ci_upper),
        'relative_change_percent': relative_change,
        'sample_size_control': len(control_data),
        'sample_size_treatment': len(treatment_data)
    }


def chi_square_test(control_conversions: int, control_total: int,
                   treatment_conversions: int, treatment_total: int,
                   alpha: float = 0.05) -> Dict:
    # Create contingency table
    observed = np.array([
        [treatment_conversions, treatment_total - treatment_conversions],
        [control_conversions, control_total - control_conversions]
    ])
    
    # Perform chi-square test
    chi2_stat, p_value, dof, expected = stats.chi2_contingency(observed)
    
    # Calculate conversion rates
    control_rate = control_conversions / control_total if control_total > 0 else 0
    treatment_rate = treatment_conversions / treatment_total if treatment_total > 0 else 0
    
    # Calculate absolute and relative lift
    absolute_lift = treatment_rate - control_rate
    relative_lift = (absolute_lift / control_rate * 100) if control_rate > 0 else 0
    
    # Calculate confidence interval for difference in proportions
    # Using normal approximation
    se_diff = np.sqrt(
        (control_rate * (1 - control_rate) / control_total) +
        (treatment_rate * (1 - treatment_rate) / treatment_total)
    )
    
    z_critical = stats.norm.ppf(1 - alpha/2)
    ci_lower = absolute_lift - z_critical * se_diff
    ci_upper = absolute_lift + z_critical * se_diff
    
    return {
        'statistic': chi2_stat,
        'p_value': p_value,
        'significant': p_value < alpha,
        'control_rate': control_rate,
        'treatment_rate': treatment_rate,
        'absolute_lift': absolute_lift,
        'relative_lift_percent': relative_lift,
        'confidence_interval': (ci_lower, ci_upper),
        'sample_size_control': control_total,
        'sample_size_treatment': treatment_total
    }


def bonferroni_correction(p_values: list, alpha: float = 0.05) -> Dict:
    n_tests = len(p_values)
    adjusted_alpha = alpha / n_tests
    
    significant_tests = [p < adjusted_alpha for p in p_values]
    
    return {
        'original_alpha': alpha,
        'adjusted_alpha': adjusted_alpha,
        'n_tests': n_tests,
        'p_values': p_values,
        'significant_after_correction': significant_tests,
        'n_significant': sum(significant_tests)
    }


def sample_size_calculator(baseline_metric: float, mde: float, 
                          alpha: float = 0.05, power: float = 0.8,
                          metric_type: str = 'continuous') -> Dict:
    # Z-scores for alpha and power
    z_alpha = stats.norm.ppf(1 - alpha/2)  # Two-tailed
    z_beta = stats.norm.ppf(power)
    
    if metric_type == 'proportion':
        # For conversion rates
        p1 = baseline_metric
        p2 = baseline_metric + mde
        
        # Pooled proportion
        p_pooled = (p1 + p2) / 2
        
        # Sample size formula for proportions
        n = (2 * p_pooled * (1 - p_pooled) * (z_alpha + z_beta)**2) / (mde**2)
        
    else:  # continuous
        # Assume standard deviation ≈ mean (common for count data)
        # For time-based metrics, you'd need historical std dev
        assumed_std = baseline_metric * 0.5  # Conservative estimate
        
        effect_size = baseline_metric * mde
        
        # Sample size formula for continuous metrics
        n = (2 * assumed_std**2 * (z_alpha + z_beta)**2) / (effect_size**2)
    
    return {
        'required_sample_size_per_variant': int(np.ceil(n)),
        'total_sample_size': int(np.ceil(n * 2)),
        'baseline_metric': baseline_metric,
        'minimum_detectable_effect': mde,
        'alpha': alpha,
        'power': power,
        'metric_type': metric_type
    }
    