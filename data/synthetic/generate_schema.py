import duckdb

def create_schema(db_path='data/raw/experiments.db'):
    """Create all tables for the experimentation platform"""
    
    conn = duckdb.connect(db_path)
    
    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            signup_date DATE,
            company_size VARCHAR(20),
            industry VARCHAR(50),
            plan_type VARCHAR(20),
            created_at TIMESTAMP
        )
    """)
    
    # Experiments table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            experiment_id INTEGER PRIMARY KEY,
            experiment_name VARCHAR(200),
            hypothesis TEXT,
            start_date DATE,
            end_date DATE,
            status VARCHAR(20),
            primary_metric VARCHAR(100),
            secondary_metrics TEXT,
            created_at TIMESTAMP
        )
    """)
    
    # Experiment assignments table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS experiment_assignments (
            assignment_id INTEGER PRIMARY KEY,
            experiment_id INTEGER,
            user_id INTEGER,
            variant VARCHAR(50),
            assigned_at TIMESTAMP,
            FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    # Events table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            event_type VARCHAR(100),
            event_timestamp TIMESTAMP,
            experiment_id INTEGER,
            variant VARCHAR(50),
            event_properties TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
        )
    """)
    
    conn.commit()
    conn.close()
    
    print(f"✓ Schema created successfully at {db_path}")

if __name__ == "__main__":
    create_schema()