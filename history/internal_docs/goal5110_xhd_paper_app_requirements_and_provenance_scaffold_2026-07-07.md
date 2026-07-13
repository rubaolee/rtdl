# Goal5110 - X-HD Paper App Requirements And Provenance Scaffold

Date: 2026-07-07

## Verdict

```text
xhd_paper_app_scaffold_created__author_source_pinned__existing_rtdl_assets_mapped
```

Goal5110 starts the X-HD paper-reproduction line. It does not claim
reproduction yet. It pins the public paper/source provenance, maps the existing
RTDL Hausdorff/X-HD-style assets, and creates the `Paper-reproduction-apps`
scaffold for the new paper app.

## Public Sources Located

Paper:

```text
title: X-HD: Fast Hausdorff Distance Computation with Ray Tracing
venue: ACM International Conference on Supercomputing (ICS) 2026
DOI: https://doi.org/10.1145/3797905.3800509
homepage: https://gengl.me/publications/ics26/
PDF: https://rubaolee.github.io/paper_pdfs/2026-xhd.pdf
```

Author source:

```text
repository: https://github.com/pwrliang/X-HD.git
branch: main
commit: 7bf41c8442d059c94f4178355c6d5a10571d9658
commit_date: 2026-06-13 16:59:42 -0400
```

Other branches observed:

```text
paper  = 8c3846866052e1e8755210021f23fac2cbe8c3d6
hybrid = 4d9046a9e55d87f35daf81dd718444029fab56ce
```

## Author Program Contract

The repository README documents:

```text
./bin/hd_exec \
  -input1 "file path1" \
  -input2 "file path2" \
  -n_dims "number of dims" \
  -input_type "image/wkt/ply" \
  -variant "eb/nn/itk/rt" \
  -execution "cpu/gpu" \
  -v=1
```

`src/flags.cc` and `src/main.cpp` refine this:

```text
input_type: wkt/off/image/ply
variant: compare-methods/eb/rt/nn/clover/itk
execution: cpu/gpu
json: output path of json file
check: correctness check
```

`variant=rt` maps to `Variant::kRT`, the X-HD path.

The JSON schema is discoverable from source and checked against repository logs:

```text
HDResult
Running.AvgTime
Running.Repeats[*].ReportedTime
Running.Repeats[*].BVHBuildTime
Running.Repeats[*].Iterations[*].RTTime
Running.Repeats[*].Iterations[*].CUDATime
Running.Repeats[*].Iterations[*].OffloadingSize
```

The source writes these fields in:

```text
src/run_hausdorff_distance.cu
src/hd_impl/hausdorff_distance_rt.h
```

## Existing RTDL Assets

RTDL already has significant Hausdorff/X-HD-style assets under:

```text
examples/current/research_benchmarks/hausdorff_xhd/
```

Key existing files:

```text
rtdl_hausdorff_distance_app.py
rtdl_hausdorff_v2_function.py
rtdl_hausdorff_v2_language_lab.py
rtdl_hausdorff_v2_user_benchmark.py
```

Important routes already present:

- `rtdl_rt_threshold_search`;
- `rtdl_rt_nearest_witness`;
- `rtdl_rt_grouped_nearest_witness`;
- `rtdl_rt_grouped_reduced_nearest_witness`;
- `rtdl_rt_grouped_seeded_pruned_nearest_witness`;
- `rtdl_rt_grouped_active_frontier_nearest_witness`;
- `rtdl_rt_grouped_adaptive_nearest_witness`;
- `rtdl_rt_grouped_device_columns_numba_argmax_nearest_witness`;
- exact CPU/OpenMP, CUDA, CuPy, and Numba witness baselines.

Prior internal report:

```text
history/internal_docs/docs_reports/hausdorff_v2_rt_acceleration_attempt_2026-05-15.md
```

There is also substantial earlier X-HD/Hausdorff evidence in the Goal2110-2143
range, including grouped RT traversal, seeded/pruned variants, public Stanford
graphics harnesses, and synthetic A5000 timing. Those reports repeatedly carry
the same boundary: useful X-HD-style evidence, not exact X-HD paper dataset
reproduction. Goal5110 preserves that distinction instead of resetting history.

Key prior conclusion:

```text
Current v2 can express RT-accelerated HD decision search.
Current v2 cannot yet express full X-HD exact nearest-witness traversal.
```

That history matters. This new paper app must not relabel old
`X-HD-style benchmark` evidence as X-HD paper reproduction.

## Files Added

```text
Paper-reproduction-apps/x-hd-paper/README.md
Paper-reproduction-apps/x-hd-paper/data/README.md
Paper-reproduction-apps/x-hd-paper/data/manifest.json
Paper-reproduction-apps/x-hd-paper/results/README.md
tests/goal5110_xhd_paper_app_scaffold_test.py
```

## Reproduction Status

Current status:

```text
not_started__requirements_and_provenance_scaffold
```

No paper reproduction is claimed.

First target:

```text
bounded_same_input_author_json_gate
```

The first executable goal should:

1. build the author `hd_exec`;
2. create a tiny deterministic WKT/PLY same-input fixture;
3. run author `variant=rt` and at least one exact CPU/GPU author baseline if
   available;
4. run RTDL exact Hausdorff witness output on the same fixture;
5. compare `HDResult` with explicit tolerance;
6. record author JSON phase fields without making a performance claim.

## What This Proves

Proved:

- The paper and public source repository are located.
- The author source commit is pinned.
- The author CLI and JSON output contract are documented.
- Existing RTDL Hausdorff/X-HD-style assets are mapped.
- A new `Paper-reproduction-apps/x-hd-paper` scaffold exists with no false
  reproduction claim.

Not proved:

- `hd_exec` builds locally or on a POD;
- any author result has been reproduced;
- exact paper inputs are available;
- existing RTDL benchmark outputs match author outputs;
- performance parity or speedup.

## Tests

Command:

```text
py -m unittest tests.goal5110_xhd_paper_app_scaffold_test
```

Result:

```text
Ran 3 tests in 0.002s
OK
```

JSON validation:

```text
Paper-reproduction-apps/x-hd-paper/data/manifest.json: ok
```

Coverage:

- manifest pins paper DOI and source commit;
- manifest does not claim full paper reproduction, exact paper data, speedup,
  or reclassification of old benchmarks;
- README keeps existing benchmark assets separate from paper reproduction;
- data README tracks author source files that define CLI and JSON schema.

## Next Goal

Goal5111 should be:

```text
X-HD author build and tiny same-input JSON comparator gate
```

It should not chase full paper datasets first. The first useful milestone is a
tiny same-input gate that proves we can run the pinned author program and compare
its `HDResult` to a deterministic RTDL exact Hausdorff output.
