Please review Goal 205 in the current RTDL repo checkout.

Read these files first:
- `/Users/rl2025/rtdl_python_only/docs/goal_205_knn_rows_cpu_oracle.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal205_knn_rows_cpu_oracle_2026-04-10.md`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/oracle_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/native/oracle/rtdl_oracle_abi.h`
- `/Users/rl2025/rtdl_python_only/src/native/oracle/rtdl_oracle_api.cpp`
- `/Users/rl2025/rtdl_python_only/tests/goal205_knn_rows_cpu_oracle_test.py`
- `/Users/rl2025/rtdl_python_only/tests/goal40_native_oracle_test.py`

Then write your review to:
- `/Users/rl2025/rtdl_python_only/docs/reports/gemini_goal205_knn_rows_cpu_oracle_review_2026-04-10.md`

Response format:
- exactly three short sections titled `Verdict`, `Findings`, and `Summary`

Review focus:
- does the native/oracle path preserve the frozen `knn_rows` contract?
- does it match the Goal 204 Python truth-path semantics?
- are there any correctness or honesty problems that block closure?
