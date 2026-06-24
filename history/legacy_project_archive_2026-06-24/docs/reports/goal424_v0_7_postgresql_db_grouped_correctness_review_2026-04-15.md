# Codex Review: Goal 424

Verdict: ACCEPT

Goal 424 extends the PostgreSQL correctness gate to the first grouped DB
kernels:

- `grouped_count`
- `grouped_sum`

Accepted evidence:

- grouped SQL-shape coverage
- fake grouped PostgreSQL parity
- live Linux PostgreSQL grouped parity
- parity against:
  - `run_cpu_python_reference(...)`
  - `run_cpu(...)`

The report stays honest:

- this closes grouped PostgreSQL correctness only
- it does not claim RT backend execution
- it does not claim a native C DB oracle ABI yet
