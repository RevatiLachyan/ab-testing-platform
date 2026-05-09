import duckdb
import numpy as np
import json
from src.analysis.statistical_tests import ttest_independent, chi_square_test, bonferroni_correction
from src.data_quality.srm_check import detect_sample_ratio_mismatch

def test_experiment_1():
    """Test Experiment 1: New Onboarding Flow (continuous metric)"""
    
    print("\n" + "="*60)
    print("EXPERIMENT 1: New Onboarding Flow")
    print("Metric: Time to First Task (minutes)")
    print("="*60)
    
    conn = duckdb.connect('data/raw/experiments.db')
    
    # Get time to first task for both variants
    query = """
    SELECT 
        ea.variant,
        CAST(json_extract_string(e.event_properties, '$.time_to_first_task_minutes') AS DOUBLE) as time_minutes
    FROM events e
    JOIN experiment_assignments ea ON e.user_id = ea.user_id AND e.experiment_id = ea.experiment_id
    WHERE e.experiment_id = 1
    AND e.event_type = 'first_task_created'
    """
    
    df = conn.execute(query).fetchdf()
    
    control_data = df[df['variant'] == 'control']['time_minutes'].values
    treatment_data = df[df['variant'] == 'treatment']['time_minutes'].values
    
    # Run t-test
    results = ttest_independent(control_data, treatment_data)
    
    print(f"\n Sample Sizes:")
    print(f"  Control: {results['sample_size_control']} users")
    print(f"  Treatment: {results['sample_size_treatment']} users")
    
    print(f"\n  Time to First Task:")
    print(f"  Control: {results['control_mean']:.1f} min (± {results['control_std']:.1f})")
    print(f"  Treatment: {results['treatment_mean']:.1f} min (± {results['treatment_std']:.1f})")
    
    print(f"\n Impact:")
    print(f"  Absolute difference: {results['treatment_mean'] - results['control_mean']:.1f} minutes")
    print(f"  Relative change: {results['relative_change_percent']:.1f}%")
    print(f"  95% CI: [{results['confidence_interval'][0]:.1f}, {results['confidence_interval'][1]:.1f}]")
    
    print(f"\n Statistical Test:")
    print(f"  t-statistic: {results['statistic']:.3f}")
    print(f"  p-value: {results['p_value']:.4f}")
    print(f"  Significant: {'✅ YES' if results['significant'] else '❌ NO'}")
    print(f"  Effect size (Cohen's d): {results['effect_size_cohens_d']:.3f}")
    
    # Check for SRM
    srm = detect_sample_ratio_mismatch(results['sample_size_control'], 
                                      results['sample_size_treatment'])
    print(f"\n Data Quality Check (SRM):")
    print(f"  {srm['warning_message']}")
    print(f"  Actual split: {srm['actual_ratio']:.1%} treatment")
    
    conn.close()
    return results

def test_experiment_2():
    """Test Experiment 2: AI Task Suggestions (aggregated continuous metric)"""
    
    print("\n" + "="*60)
    print("EXPERIMENT 2: AI Task Suggestions")
    print("Metric: Tasks Created Per User (Daily Average)")
    print("="*60)
    
    conn = duckdb.connect('data/raw/experiments.db')
    
    # Aggregate tasks per user across the experiment period
    query = """
    SELECT 
        ea.variant,
        ea.user_id,
        AVG(CAST(json_extract_string(e.event_properties, '$.tasks_count') AS INTEGER)) as avg_daily_tasks
    FROM experiment_assignments ea
    JOIN events e ON ea.user_id = e.user_id 
        AND e.experiment_id = 2
    WHERE ea.experiment_id = 2
    AND e.event_type = 'tasks_created'
    GROUP BY ea.variant, ea.user_id
    """
    
    df = conn.execute(query).fetchdf()
    
    control_data = df[df['variant'] == 'control']['avg_daily_tasks'].values
    treatment_data = df[df['variant'] == 'treatment']['avg_daily_tasks'].values
    
    # Run t-test
    results = ttest_independent(control_data, treatment_data)
    
    print(f"\n Sample Sizes:")
    print(f"  Control: {results['sample_size_control']} users")
    print(f"  Treatment: {results['sample_size_treatment']} users")
    
    print(f"\n Average Daily Tasks Created:")
    print(f"  Control: {results['control_mean']:.2f} tasks/day (± {results['control_std']:.2f})")
    print(f"  Treatment: {results['treatment_mean']:.2f} tasks/day (± {results['treatment_std']:.2f})")
    
    print(f"\n Impact:")
    print(f"  Absolute difference: {results['treatment_mean'] - results['control_mean']:.2f} tasks/day")
    print(f"  Relative change: {results['relative_change_percent']:.1f}%")
    print(f"  95% CI: [{results['confidence_interval'][0]:.2f}, {results['confidence_interval'][1]:.2f}]")
    
    print(f"\n Statistical Test:")
    print(f"  t-statistic: {results['statistic']:.3f}")
    print(f"  p-value: {results['p_value']:.4f}")
    print(f"  Significant: {'✅ YES' if results['significant'] else '❌ NO'}")
    print(f"  Effect size (Cohen's d): {results['effect_size_cohens_d']:.3f}")
    
    # Check for SRM
    srm = detect_sample_ratio_mismatch(results['sample_size_control'], 
                                      results['sample_size_treatment'])
    print(f"\n Data Quality Check (SRM):")
    print(f"  {srm['warning_message']}")
    print(f"  Actual split: {srm['actual_ratio']:.1%} treatment")
    
    conn.close()
    return results


def test_experiment_3():
    """Test Experiment 3: Pricing Page Redesign (binary metric)"""
    
    print("\n" + "="*60)
    print("EXPERIMENT 3: Pricing Page Redesign")
    print("Metric: Trial-to-Paid Conversion Rate")
    print("="*60)
    
    conn = duckdb.connect('data/raw/experiments.db')
    
    # Get conversion counts
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
    
    control = df[df['variant'] == 'control'].iloc[0]
    treatment = df[df['variant'] == 'treatment'].iloc[0]
    
    # Run chi-square test
    results = chi_square_test(
        control_conversions=int(control['converted_users']),
        control_total=int(control['total_users']),
        treatment_conversions=int(treatment['converted_users']),
        treatment_total=int(treatment['total_users'])
    )
    
    print(f"\n Sample Sizes:")
    print(f"  Control: {results['sample_size_control']} users")
    print(f"  Treatment: {results['sample_size_treatment']} users")
    
    print(f"\n Conversion Rates:")
    print(f"  Control: {results['control_rate']:.2%}")
    print(f"  Treatment: {results['treatment_rate']:.2%}")
    
    print(f"\n Impact:")
    print(f"  Absolute lift: {results['absolute_lift']:.2%} ({results['absolute_lift']*100:.1f} percentage points)")
    print(f"  Relative lift: {results['relative_lift_percent']:.1f}%")
    print(f"  95% CI: [{results['confidence_interval'][0]:.2%}, {results['confidence_interval'][1]:.2%}]")
    
    print(f"\n Statistical Test:")
    print(f"  χ² statistic: {results['statistic']:.3f}")
    print(f"  p-value: {results['p_value']:.4f}")
    print(f"  Significant: {'✅ YES' if results['significant'] else '❌ NO'}")
    
    # Check for SRM
    srm = detect_sample_ratio_mismatch(results['sample_size_control'], 
                                      results['sample_size_treatment'])
    print(f"\n🔍 Data Quality Check (SRM):")
    print(f"  {srm['warning_message']}")
    
    conn.close()
    return results


if __name__ == "__main__":
    from src.analysis.statistical_tests import sample_size_calculator
    
    # Run tests
    exp1_results = test_experiment_1()
    exp2_results = test_experiment_2()
    exp3_results = test_experiment_3()
    
    # Test multiple testing correction
    print("\n" + "="*60)
    print("MULTIPLE TESTING CORRECTION")
    print("="*60)
    
    p_values = [exp1_results['p_value'],exp2_results['p_value'], exp3_results['p_value']]
    correction = bonferroni_correction(p_values)
    
    print(f"\nOriginal α: {correction['original_alpha']}")
    print(f"Adjusted α (Bonferroni): {correction['adjusted_alpha']:.4f}")
    print(f"Tests still significant: {correction['n_significant']}/{correction['n_tests']}")

    # Show which specific tests are still significant
    print(f"\nIndividual test results:")
    test_names = ['Exp 1: Onboarding Flow', 'Exp 2: AI Suggestions', 'Exp 3: Pricing Page']
    for i, (name, p_val, still_sig) in enumerate(zip(test_names, p_values, correction['significant_after_correction'])):
        status = 'Still significant' if still_sig else 'Not significant after correction'
        print(f"  {name}: p={p_val:.4f} → {status}")

        # Sample size analysis for Experiment 3
    print("\n" + "="*60)
    print("SAMPLE SIZE ANALYSIS: Experiment 3")
    print("="*60)
    print("\nWhy wasn't Exp 3 significant after correction?")
    print("Let's calculate the required sample size...")
    

    baseline = 0.08  # 8% conversion rate
    mde = 0.03  # Want to detect 3 percentage point lift (8% → 11%)
    
    required = sample_size_calculator(
        baseline_metric=baseline,
        mde=mde,
        alpha=0.0167,  # Bonferroni-corrected alpha
        power=0.8,
        metric_type='proportion'
    )
    
    actual_sample = exp3_results['sample_size_control'] + exp3_results['sample_size_treatment']
    
    print(f"\nBaseline conversion rate: {baseline:.1%}")
    print(f"Target lift: {mde:.1%} (to {baseline + mde:.1%})")
    print(f"\nRequired sample size: {required['total_sample_size']:,} users")
    print(f"Actual sample size: {actual_sample:,} users")
    print(f"We had: {actual_sample / required['total_sample_size'] * 100:.0f}% of needed sample")
    print(f"\n To detect this with Bonferroni correction, we'd need")
    print(f"   {required['total_sample_size'] - actual_sample:,} more users")