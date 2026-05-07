"""Verify environment is set up correctly"""
import sys

def test_imports():
    """Test that all required packages can be imported"""
    try:
        import pandas as pd
        import numpy as np
        import duckdb
        import scipy
        import statsmodels
        import pingouin
        import streamlit
        import plotly
        import faker
        print("✓ All packages imported successfully!")
        print(f"✓ Python version: {sys.version}")
        print(f"✓ Pandas version: {pd.__version__}")
        print(f"✓ DuckDB version: {duckdb.__version__}")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)