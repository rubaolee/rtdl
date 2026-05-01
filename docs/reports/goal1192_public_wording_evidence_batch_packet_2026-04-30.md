# Goal1192 Public Wording Evidence Batch Packet

Date: 2026-04-30

Valid: `True`

## Runner

- runner: `scripts/goal1192_public_wording_evidence_batch_runner.sh`
- expected apps: `6`
- expected outputs: `12`

## Pod Preconditions

- RTX-class Linux pod with NVIDIA driver visible through nvidia-smi.
- OptiX backend built successfully with make build-optix before invoking the runner.
- GEOS/pkg-config installed before Embree/geometry baselines.
- Run the full batch once, copy back the tgz and sha256, then run a local intake script.

## Run Command

```bash
OUTDIR=docs/reports/goal1192_public_wording_evidence_batch bash scripts/goal1192_public_wording_evidence_batch_runner.sh
```

## Expected Outputs

- `database_compact_summary_embree.json`
- `database_compact_summary_optix.json`
- `graph_visibility_edges_embree.json`
- `graph_visibility_edges_optix.json`
- `road_hazard_native_summary_embree.json`
- `road_hazard_native_summary_optix.json`
- `polygon_pair_candidate_discovery_embree.json`
- `polygon_pair_candidate_discovery_optix.json`
- `polygon_jaccard_safe_chunk_embree.json`
- `polygon_jaccard_safe_chunk_optix.json`
- `hausdorff_threshold_prepared_embree.json`
- `hausdorff_threshold_prepared_optix.json`

## Boundary

This packet defines a future six-row evidence batch only. It does not run cloud, does not authorize release, and does not authorize public RTX speedup wording.
