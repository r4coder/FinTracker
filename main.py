"""
main.py — Run full pipeline in one command
Run: python main.py
"""

import subprocess
import sys

STEPS = [
    ("💰 Generating expense data...",    [sys.executable, "src/generate_data.py"]),
    ("📊 Running analysis...",           [sys.executable, "src/analyzer.py"]),
    ("📈 Generating visualizations...",  [sys.executable, "src/visualizer.py"]),
]

print("=" * 55)
print("  Personal Expense Tracker — Full Pipeline")
print("=" * 55)

for label, cmd in STEPS:
    print(f"\n{label}")
    print("-" * 45)
    result = subprocess.run(cmd, capture_output=False, text=True)
    if result.returncode != 0:
        print("❌ Step failed. Fix errors and rerun.")
        sys.exit(1)

print("\n" + "=" * 55)
print("  ✅ Pipeline Complete!")
print("  📁 Check outputs/ for all charts")
print("  📁 Check data/ for generated CSVs")
print("  🚀 Run: python -m streamlit run dashboard.py")
print("=" * 55)