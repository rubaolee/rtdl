# RTDL v2.0 Research Benchmarks

This directory is for serious application studies, not first-run examples. Each
subdirectory shows how a user can write a real RTDL v2.0 program, compare it
with external baselines, and keep the performance claim boundary precise.

Run commands from the repository root with source-tree usage:

```bash
PYTHONPATH=src:. python examples/v2_0/research_benchmarks/<study>/<script>.py
```

On Windows PowerShell, use:

```powershell
$env:PYTHONPATH='src;.'; py -3 examples\v2_0\research_benchmarks\<study>\<script>.py
```

## Studies

| Directory | Purpose | Start here |
| --- | --- | --- |
| `hausdorff_xhd/` | Exact and RT-assisted Hausdorff distance study informed by X-HD techniques | `hausdorff_xhd/README.md` |
| `spatial_rayjoin/` | RayJoin-style spatial join workloads over RTDL v2.0 | `spatial_rayjoin/README.md` |

## How To Read Results

- Treat these as reproducible research harnesses, not universal speedup claims.
- CPU-only commands are useful for correctness and contract checks.
- OptiX timing needs a CUDA-capable machine with `librtdl_optix` built and
  `RTDL_OPTIX_LIBRARY` set when the library is outside the default path.
- A result can show an RTDL program is useful for a workload without claiming
  that every phase is RT-core accelerated.
- Public performance language should cite the exact script, dataset, backend,
  method, commit, and hardware.

## Recommended Flow

1. Run the CPU reference command in the study README.
2. Run the Embree command to check the same RTDL contract on the CPU RT backend.
3. On an NVIDIA pod or workstation, build OptiX and run the OptiX command.
4. Compare JSON fields such as `parity_vs_cpu_python_reference`,
   `matches_exact_reference`, `elapsed_sec`, `rt_core_accelerated`, and
   `claim_boundary`.

The benchmark directories intentionally keep paper-inspired work separate from
the ordinary learner examples so new users can learn RTDL without being pulled
into historical performance debates.
