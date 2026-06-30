# Goal2525 GPU Database Candidate Gate For RayDB-Style RTDL

Date: 2026-05-23

## Verdict

Goal2525 probes the pod for a quick GPU database baseline candidate. The pod has
an NVIDIA GPU, but no ready GPU database/dataframe stack is installed.

Decision: do not spend this goal installing a GPU database. Use PostgreSQL and
DuckDB as the immediate absolute baselines. If a GPU DB-like baseline is still
needed, make RAPIDS/cuDF a separate install-and-contract goal.

Follow-up: the user explicitly chose the lightweight GPU dataframe route, so
Goal2526 installs RAPIDS/cuDF and records the GPU baseline. Goal2525 remains the
environment/candidate gate that justified using cuDF instead of a heavier GPU
database server.

## Pod Evidence

Pod:

```text
ssh root@213.173.108.13 -p 15902 -i ~/.ssh/id_ed25519_rtdl_codex
hostname: 57449dd4f93c
```

GPU probe:

```text
NVIDIA RTX 4000 Ada Generation, driver 550.127.05, 20475 MiB
```

Artifact:

- `docs/reports/goal2525_gpu_database_candidate_gate_pod_2026-05-23.json`

Runner:

```bash
python3 scripts/goal2525_gpu_database_candidate_gate.py \
  --output docs/reports/goal2525_gpu_database_candidate_gate_pod_2026-05-23.json
```

## Candidate Status

| Candidate | Pod status | Decision |
| --- | --- | --- |
| PostgreSQL | Installed and used | Keep as SQL correctness plus CPU DBMS diagnostic timing |
| DuckDB | Installed in venv and used | Keep as quick embedded analytical SQL baseline |
| RAPIDS/cuDF | `cudf` and `pylibcudf` not installed | Best first GPU DB-like candidate, but defer to separate install goal |
| HeavyDB/OmniSci | Server commands not installed | Not quick for this goal |
| Crystal | Command not found | Not available on this pod |

## Interpretation

The GPU is available, but a GPU database stack is not. Installing RAPIDS/cuDF or
a server-style GPU DB would add dependency, CUDA/Python compatibility, and setup
risk that is larger than this tiny baseline goal.

The pragmatic sequence is:

1. Use Goal2522 PostgreSQL correctness to prove SQL semantics.
2. Use Goal2523 PostgreSQL diagnostic timing as a CPU DBMS reference.
3. Use Goal2524 DuckDB diagnostic timing as an embedded analytical SQL
   reference.
4. Only if needed, open a dedicated RAPIDS/cuDF goal with installation,
   correctness, and timing as first-class deliverables.

## Claim Boundary

This gate does not authorize public speedup, whole-DBMS, authors-code, RayDB
reproduction, true zero-copy, or GPU-database performance claims.

Allowed:

- the pod has an NVIDIA RTX 4000 Ada GPU;
- no quick GPU database baseline was available on the pod;
- RAPIDS/cuDF is the recommended first GPU DB-like candidate if we choose to
  pay the setup cost later.

Blocked:

- GPU database performance claim;
- public speedup wording;
- whole-DBMS performance claim;
- RayDB or authors-code comparison;
- true zero-copy claim.
