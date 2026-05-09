import duckdb
from faker import Faker
import random
from datetime import datetime, timedelta
import json

fake = Faker()
Faker.seed(42)
random.seed(42)

def generate_users(conn, n_users=10000):
    """Generate synthetic users"""
    
    users_data = []
    signup_start = datetime(2024, 1, 1)
    
    for i in range(n_users):
        signup_date = signup_start + timedelta(days=random.randint(0, 120))
        users_data.append({
            'user_id': i + 1,
            'signup_date': signup_date.date(),
            'company_size': random.choice(['1-10', '11-50', '51-200', '201-1000', '1000+']),
            'industry': random.choice(['Technology', 'Finance', 'Healthcare', 'Retail', 'Education', 'Manufacturing']),
            'plan_type': random.choice(['free', 'free', 'free', 'starter', 'professional']),  # More free users
            'created_at': signup_date
        })
    
    conn.executemany("""
        INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)
    """, [(u['user_id'], u['signup_date'], u['company_size'], u['industry'], u['plan_type'], u['created_at']) 
          for u in users_data])
    
    print(f"✓ Generated {n_users} users")
    return users_data

def generate_experiments(conn):
    """Generate 3 experiments"""
    
    experiments = [
        {
            'experiment_id': 1,
            'experiment_name': 'New Onboarding Flow',
            'hypothesis': 'A streamlined onboarding flow will reduce time to first task created',
            'start_date': datetime(2024, 3, 1).date(),
            'end_date': datetime(2024, 4, 15).date(),
            'status': 'completed',
            'primary_metric': 'time_to_first_task_minutes',
            'secondary_metrics': 'completion_rate, activation_rate',
            'created_at': datetime(2024, 2, 25)
        },
        {
            'experiment_id': 2,
            'experiment_name': 'AI Task Suggestions',
            'hypothesis': 'AI-powered task suggestions will increase daily active usage and tasks created',
            'start_date': datetime(2024, 3, 15).date(),
            'end_date': datetime(2024, 5, 1).date(),
            'status': 'completed',
            'primary_metric': 'tasks_created_per_user',
            'secondary_metrics': 'dau, session_duration',
            'created_at': datetime(2024, 3, 10)
        },
        {
            'experiment_id': 3,
            'experiment_name': 'Pricing Page Redesign',
            'hypothesis': 'Clearer pricing tiers will improve trial to paid conversion rate',
            'start_date': datetime(2024, 4, 1).date(),
            'end_date': datetime(2024, 5, 15).date(),
            'status': 'completed',
            'primary_metric': 'trial_to_paid_conversion',
            'secondary_metrics': 'page_time, cta_clicks',
            'created_at': datetime(2024, 3, 25)
        }
    ]
    
    conn.executemany("""
        INSERT INTO experiments VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [(e['experiment_id'], e['experiment_name'], e['hypothesis'], e['start_date'], 
           e['end_date'], e['status'], e['primary_metric'], e['secondary_metrics'], e['created_at']) 
          for e in experiments])
    
    print(f"✓ Generated {len(experiments)} experiments")
    return experiments

def generate_experiment_assignments(conn, users_data, experiments):
    """Assign users to experiment variants"""
    
    assignments = []
    assignment_id = 1
    
    for exp in experiments:
        # Get users who signed up before experiment started
        eligible_users = [u for u in users_data 
                         if u['signup_date'] < exp['start_date']]
        
        # Sample 40% of eligible users for the experiment
        sample_size = int(len(eligible_users) * 0.4)
        experiment_users = random.sample(eligible_users, sample_size)
        
        for user in experiment_users:
            variant = random.choice(['control', 'treatment'])
            assignments.append({
                'assignment_id': assignment_id,
                'experiment_id': exp['experiment_id'],
                'user_id': user['user_id'],
                'variant': variant,
                'assigned_at': exp['start_date']
            })
            assignment_id += 1
    
    conn.executemany("""
        INSERT INTO experiment_assignments VALUES (?, ?, ?, ?, ?)
    """, [(a['assignment_id'], a['experiment_id'], a['user_id'], a['variant'], a['assigned_at']) 
          for a in assignments])
    
    print(f"✓ Generated {len(assignments)} experiment assignments")
    return assignments

def generate_events(conn, assignments, experiments):
    """Generate events for each experiment"""
    
    event_id = 1
    
    # Experiment 1: Onboarding flow - time to first task
    exp1_assignments = [a for a in assignments if a['experiment_id'] == 1]
    
    for assignment in exp1_assignments:
        # Control: avg 45 min, Treatment: avg 32 min (improvement)
        if assignment['variant'] == 'control':
            time_to_first_task = max(5, random.gauss(45, 20))
        else:
            time_to_first_task = max(5, random.gauss(32, 15))
        
        event_time = assignment['assigned_at'] + timedelta(minutes=time_to_first_task)
        
        conn.execute("""
            INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (event_id, assignment['user_id'], 'first_task_created', event_time,
              1, assignment['variant'], json.dumps({'time_to_first_task_minutes': round(time_to_first_task, 2)})))
        event_id += 1
    
    print(f"✓ Generated {len(exp1_assignments)} events for Experiment 1")
    
    # Experiment 2: AI suggestions - tasks created
    exp2_assignments = [a for a in assignments if a['experiment_id'] == 2]
    
    for assignment in exp2_assignments:
        # Simulate daily usage over experiment period
        exp_start = datetime(2024, 3, 15)
        exp_end = datetime(2024, 5, 1)
        
        num_days = (exp_end - exp_start).days
        
        for day in range(num_days):
            # 60% daily active rate
            if random.random() < 0.6:
                event_date = exp_start + timedelta(days=day)
                
                # Control: avg 3.2 tasks/day, Treatment: avg 4.8 tasks/day
                if assignment['variant'] == 'control':
                    tasks_created = max(0, int(random.gauss(3.2, 2)))
                else:
                    tasks_created = max(0, int(random.gauss(4.8, 2.5)))
                
                conn.execute("""
                    INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (event_id, assignment['user_id'], 'tasks_created', event_date,
                      2, assignment['variant'], json.dumps({'tasks_count': tasks_created})))
                event_id += 1
    
    print(f"✓ Generated events for Experiment 2")
    
    # Experiment 3: Pricing page - conversions
    exp3_assignments = [a for a in assignments if a['experiment_id'] == 3]
    
    for assignment in exp3_assignments:
        # Only free users can convert
        user_plan = conn.execute("""
            SELECT plan_type FROM users WHERE user_id = ?
        """, [assignment['user_id']]).fetchone()
        
        if user_plan and user_plan[0] == 'free':
            # Control: 8% conversion, Treatment: 11% conversion
            conversion_rate = 0.08 if assignment['variant'] == 'control' else 0.11
            
            if random.random() < conversion_rate:
                conversion_time = assignment['assigned_at'] + timedelta(days=random.randint(1, 30))
                
                conn.execute("""
                    INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (event_id, assignment['user_id'], 'trial_to_paid_conversion', conversion_time,
                      3, assignment['variant'], json.dumps({'converted': True})))
                event_id += 1
    
    print(f"✓ Generated events for Experiment 3")

def main():
    """Main data generation pipeline"""
    
    db_path = 'data/raw/experiments.db'
    
    print("Starting data generation...")
    conn = duckdb.connect(db_path)
    
    # Generate data
    users_data = generate_users(conn, n_users=10000)
    experiments = generate_experiments(conn)
    assignments = generate_experiment_assignments(conn, users_data, experiments)
    generate_events(conn, assignments, experiments)
    
    conn.commit()
    
    # Print summary
    print("\n" + "="*50)
    print("DATA GENERATION COMPLETE")
    print("="*50)
    
    print(f"\nUsers: {conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]}")
    print(f"Experiments: {conn.execute('SELECT COUNT(*) FROM experiments').fetchone()[0]}")
    print(f"Assignments: {conn.execute('SELECT COUNT(*) FROM experiment_assignments').fetchone()[0]}")
    print(f"Events: {conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]}")
    
    conn.close()

if __name__ == "__main__":
    main()