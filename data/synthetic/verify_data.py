import duckdb

def verify_data():
    """Quick verification of generated data"""
    
    conn = duckdb.connect('data/raw/experiments.db')
    
    print("\n" + "="*60)
    print("DATA VERIFICATION")
    print("="*60)
    
    # Check record counts
    print("\n📊 Record Counts:")
    print(f"  Users: {conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]:,}")
    print(f"  Experiments: {conn.execute('SELECT COUNT(*) FROM experiments').fetchone()[0]}")
    print(f"  Assignments: {conn.execute('SELECT COUNT(*) FROM experiment_assignments').fetchone()[0]:,}")
    print(f"  Events: {conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]:,}")
    
    # Check experiment distribution
    print("\n🧪 Experiment Assignments by Variant:")
    result = conn.execute("""
    SELECT 
        e.experiment_id,
        e.experiment_name,
        a.variant,
        COUNT(*) as users
    FROM experiment_assignments a
    JOIN experiments e ON a.experiment_id = e.experiment_id
    GROUP BY e.experiment_id, e.experiment_name, a.variant
    ORDER BY e.experiment_id, a.variant
    """).fetchall()

    for row in result:
        print(f"  {row[1][:30]:30} | {row[2]:10} | {row[3]:,} users")
    
    
    # Check sample events
    print("\n📝 Sample Events:")
    result = conn.execute("""
        SELECT event_type, COUNT(*) as count
        FROM events
        GROUP BY event_type
    """).fetchall()
    
    for row in result:
        print(f"  {row[0]:30} | {row[1]:,} events")
    
    conn.close()

if __name__ == "__main__":
    verify_data()