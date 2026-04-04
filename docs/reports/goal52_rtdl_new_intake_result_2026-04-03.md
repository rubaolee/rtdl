# Goal 52 RTDL-New Intake Result

## Decision

Goal 52 succeeded as a **code-only intake**.

The external `rtdl-new` patchset was worth merging, but not wholesale.

Accepted:

- `rt.contains()` alias
- `contains` export from `rtdsl.__init__`
- `_embree_support.py` loader fix
- `tests/test_core_quality.py`
- one direct alias assertion added locally during intake

Rejected as authoritative project history:

- the external cross-AI consensus docs in `claude-work/rtdl-new/docs/consensus_rounds`

Those docs were not imported because they are stale relative to the actual code and actual test baseline.

## Why The Intake Was Worth Doing

The accepted code changes are useful:

- the alias is a small ergonomic improvement
- the `_embree_support.py` fix removes a real test-discovery annoyance
- the new quality suite adds broad coverage across:
  - types
  - IR serialization
  - API guards
  - lowering validation
  - reference geometry behavior
  - runtime input normalization
  - `run_cpu_python_reference(...)`

## Why The External Docs Were Rejected

The external documentation claimed things that were no longer true in the reviewed repo state.

Most importantly:

- it repeatedly claimed a `255`-test clean baseline
- the actual reviewed repo passed `165` tests with `2` skips before intake
- after merging the accepted code into the main repo, the main repo passed `174` tests with `1` skip
- the docs also claimed `scripts/run_full_verification.py` still lacked real correctness assertions in a way that the current external file no longer did

So the docs were not trustworthy enough to import as authoritative records.

## External Review Outcome

### Gemini

Verdict: `APPROVE`

Recommendation:

- `merge-code-only`

Key point:

- Gemini agreed the code changes are worth keeping and the stale docs should not block code intake.

### Claude

Verdict: `APPROVE`

Recommendation:

- `merge-code-only`

Key point:

- Claude agreed the code should merge now and the external docs should not be treated as load-bearing.
- Claude also raised a prompt-injection concern about the review prompt delivery path; that was an operational CLI concern in the review environment, not a code finding against the RTDL repo itself.

## Main-Repo Verification

After the code-only intake into `/Users/rl2025/rtdl_python_only`:

- `PYTHONPATH=src:. python3 -m unittest tests.test_core_quality`
  - `91` tests
  - `OK`
- `PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'`
  - `174` tests
  - `1` skip
  - `OK`

## Boundary

- Goal 52 does **not** adopt the external `rtdl-new` consensus docs as project truth
- Goal 52 only accepts the reviewed code changes
- any future use of the external doc set should require a fresh correction round first
