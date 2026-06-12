import subprocess, sys
tests = [
    "tests.goal2319_v2_0_final_cleanup_release_candidate_test",
    "tests.goal2068_final_v2_0_release_matrix_test",
    "tests.goal2069_v2_0_pre_release_gate_test",
    "tests.goal2072_v2_0_final_readiness_aggregator_test",
    "tests.goal1680_current_native_app_leakage_gap_test",
]
r = subprocess.run([sys.executable, "-m", "unittest"] + tests, capture_output=True, text=True)
print(r.stdout)
print(r.stderr)
sys.exit(r.returncode)
