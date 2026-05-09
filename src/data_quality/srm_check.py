import numpy as np
from scipy import stats
from typing import Dict

def detect_sample_ratio_mismatch(control_count: int, treatment_count: int, 
                                expected_ratio: float = 0.5, 
                                alpha: float = 0.001) -> Dict:
    """
    Detect Sample Ratio Mismatch (SRM) using chi-square goodness of fit test.
    """
    total = control_count + treatment_count
    
    # Expected counts based on ratio
    expected_treatment = total * expected_ratio
    expected_control = total * (1 - expected_ratio)
    
    # Observed counts
    observed = np.array([treatment_count, control_count])
    expected = np.array([expected_treatment, expected_control])
    
    # Chi-square goodness of fit test
    chi2_stat, p_value = stats.chisquare(observed, expected)
    
    # Actual ratio
    actual_ratio = treatment_count / total if total > 0 else 0
    
    # Flag SRM if p-value is below threshold
    srm_detected = p_value < alpha
    
    return {
        'srm_detected': srm_detected,
        'p_value': p_value,
        'chi2_statistic': chi2_stat,
        'control_count': control_count,
        'treatment_count': treatment_count,
        'expected_ratio': expected_ratio,
        'actual_ratio': actual_ratio,
        'ratio_difference': abs(actual_ratio - expected_ratio),
        'warning_message': 'SRM DETECTED - Check randomization implementation!' if srm_detected else 'No SRM detected'
    }