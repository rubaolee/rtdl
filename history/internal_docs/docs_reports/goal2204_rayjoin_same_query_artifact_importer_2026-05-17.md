# Goal2204 RayJoin Same-Query Artifact Importer

Date: 2026-05-17

Status: importer prepared; actual import requires Goal2198 pod artifacts.

## Purpose

Goal2198 runs the same-query RayJoin/RTDL pod experiment. Goal2201 summarizes a
completed pod artifact directory. Goal2204 prepares the final repo-import step:
copy the compact review artifacts into `docs/reports/`, regenerate the evidence
summary, hash the full RayJoin query streams, and keep claim boundaries locked.

Prepared script:

- `scripts/goal2204_rayjoin_same_query_artifact_import.py`

## Usage After A Pod Run

Example:

```bash
PYTHONPATH=src:. python3 scripts/goal2204_rayjoin_same_query_artifact_import.py \
  --artifact-dir /path/to/copied/goal2198/artifacts \
  --output-dir docs/reports/goal2204_rayjoin_same_query_pod_evidence \
  --output-json docs/reports/goal2204_rayjoin_same_query_pod_evidence_2026-05-17.json \
  --output-md docs/reports/goal2204_rayjoin_same_query_pod_evidence_2026-05-17.md
```

By default, the importer does not copy the full query streams into the repo.
It requires them to exist and records their byte counts and SHA-256 hashes.

Use `--include-streams` only when we deliberately want to preserve the full
RayJoin query streams in the repository.

## Imported Files

The importer copies the compact required artifacts:

- `environment.txt`
- `progress.log`
- `summary.json`
- all six RayJoin `rayjoin_<workload>_<mode>.log` files;
- both RTDL same-stream result artifacts;
- regenerated `evidence_summary.regenerated.json`;
- regenerated `evidence_report.regenerated.md`.

It hashes, and optionally copies, the full RayJoin query streams:

- `rayjoin_lsi_gen<query_count>_stream.json`
- `rayjoin_pip_gen<query_count>_stream.json`

## Fail-Closed Checks

The importer reuses the Goal2201 parser, so it refuses to import if:

- a required RayJoin log or RTDL same-stream artifact is missing;
- a full query stream is missing and cannot be hashed;
- RTDL artifacts are not from `rayjoin_query_exec_export_patch`;
- `same_contract_with_rayjoin_query_exec` is not true;
- RTDL backend parity failed;
- any stronger public claim flag is true.

## Boundary

Goal2204 is import tooling only. It does not authorize:

- RayJoin paper reproduction;
- RTDL beating RayJoin;
- broad RT-core acceleration;
- v2.0 release readiness.

Those claims require imported pod artifacts plus external review and a separate
consensus report.
