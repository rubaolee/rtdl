# Goal4930 Result: v2.14.2 Layer 0 Writer Phase Decomposition

Date: 2026-07-03

Exit label: `complete_structure_assembly_dominant_authorize_layer3_design`

## Purpose

Measure the current RayJoin Section 5.7 hot path before authorizing any v2.14.2
performance implementation.

This goal was measurement-only. It did not modify RTDL runtime/native code and
did not change the RayJoin app output contract.

## Environment

Host:

```text
ssh 192.168.1.20
hostname: lx1
GPU: NVIDIA GeForce GTX 1070
```

Run directory:

```text
/tmp/rtdl_rayjoin_complete_project_20260703
```

Command:

```bash
cd /tmp/rtdl_rayjoin_complete_project_20260703
RAYJOIN_OUT_DIR=Paper-reproduction-apps/rayjoin-paper/_runs/goal4930/rtdl \
  bash Paper-reproduction-apps/rayjoin-paper/scripts/run_rtdl_public_sample.sh
```

Artifacts copied back:

```text
history/internal_docs/goal4930_v2_14_2_layer0_writer_phase_decomposition_artifacts/summary.json
history/internal_docs/goal4930_v2_14_2_layer0_writer_phase_decomposition_artifacts/section57_overlay.json
history/internal_docs/goal4930_v2_14_2_layer0_writer_phase_decomposition_artifacts/section57_overlay_numba.json
```

## Correctness Gate

Both Section 5.7 routes remained byte-identical to the public answer:

| Route | Byte Equal | SHA-256 |
| --- | --- | --- |
| RTDL public LSI/PIP + Python app writer | true | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |
| RTDL public LSI/PIP + Numba-assisted writer | true | `464f87a59cc2428f63cbfe5068965d7bc7adb8eee51e9c1e3a5960ae8b76019e` |

Performance numbers without this byte-equality gate would not have counted.

## Section 5.7 Phase Ledger

### Plain RTDL App Writer

| Phase | Seconds |
| --- | ---: |
| Total elapsed | 5.402 |
| Hot body excluding file summaries | 5.297 |
| LSI public rows | 0.861 |
| Intersection reprojection | 0.626 |
| Sort total | 0.830 |
| Point-location total, including prepare | 0.647 |
| Midpoint transform total | 0.073 |
| Output-chain write | 2.243 |

### Numba-Assisted Writer Route

| Phase | Seconds |
| --- | ---: |
| Total elapsed | 5.438 |
| Hot body excluding file summaries | 5.333 |
| LSI public rows | 0.869 |
| Intersection reprojection | 0.631 |
| Sort total | 0.826 |
| Point-location total, including prepare | 0.641 |
| Midpoint transform total | 0.221 |
| Output-chain write | 2.129 |

The Numba-assisted route provides the useful internal writer breakdown:

| Writer Subphase | Seconds |
| --- | ---: |
| skip plan | 0.019 |
| group xsects map0 | 0.008 |
| group xsects map1 | 0.070 |
| chain loop map0 | 1.062 |
| chain loop map1 | 0.842 |
| bulk writelines | 0.064 |
| measured structural assembly subtotal | 2.001 |
| measured text/file write subtotal | 0.064 |

Counts:

| Item | Count |
| --- | ---: |
| output chains | 64,459 |
| output lines | 737,830 |
| output points | 673,371 |
| unique point records | 581,554 |
| descriptor-direct chains | 11,263 |
| skipped no-intersection chains | 77 |

## Interpretation

The remaining output cost is not dominated by final text/file write.

Measured writer split:

- structural output-chain assembly: about `2.001s`;
- final bulk text/file write: about `0.064s`.

So the immediate bottleneck is Python-side structural assembly of the output
chains, not byte formatting or disk flushing.

There is also a secondary numeric target:

- reprojection: about `0.63s`;
- sort total: about `0.83s`;
- combined numeric transform/sort: about `1.46s`.

## Classification

Goal4930 classification:

`structure_assembly_dominant`

Reason:

- the largest measured remaining subphase is structural writer assembly;
- final text/file write is tiny in this run;
- numeric transform/sort is real but secondary.

## Next Recommendation

Proceed to a design-only next goal for a generic output-assembly layer.

The next goal should not implement yet. It should design a generic structure:

- input: typed rows / chain descriptors / grouping keys;
- output: compact structural chain descriptors or columnar output records;
- app-owned final formatting remains outside the RTDL engine;
- RayJoin text/output-chain byte formatting must stay app-owned.

Layer 2 numeric continuation work remains a secondary candidate, but Goal4930
says Layer 3 structural output assembly is the first bottleneck to design
against.

## Non-Authorization

Goal4930 does not authorize:

- broad RayJoin speedup wording;
- v2.14.2 release wording;
- implementation of row-buffer/device-resident pipelines;
- implementation of a compiled writer;
- moving RayJoin-specific text formatting into RTDL core;
- in-traversal fusion work.
