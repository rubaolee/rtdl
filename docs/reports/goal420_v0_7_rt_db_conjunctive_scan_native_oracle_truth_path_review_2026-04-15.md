# Codex Review: Goal 420

Verdict: ACCEPT

Goal 420 makes the bounded `conjunctive_scan` oracle path materially more
honest:

- `run_cpu(...)` now hits a real native/oracle ABI for `conjunctive_scan`
- the Python truth helper is no longer a hidden dependency
- Linux PostgreSQL parity is proved after the native change

The boundary is still explicit:

- this does not yet close grouped native/oracle kernels
- this is a small scalar-table ABI, not a general DB row ABI
