# Goal4790 Ray Hit And Grouped Continuation Tutorial Batch

Date: 2026-06-28

## Purpose

Goal4790 extends the final RTDL V4 tutorial ladder beyond spatial predicates.
It adds the next shared concepts needed before users can read the benchmark
apps: ray/triangle hit rows and grouped continuations.

The purpose is not to teach a specific benchmark app. The purpose is to teach
the RTDL programming model:

1. express an RT-shaped relation as a kernel;
2. inspect relation rows;
3. reduce rows with an app-owned continuation;
4. only then inspect the V4 operator/runtime surface.

## Files Changed

| File | Action | Purpose |
| --- | --- | --- |
| `examples/tutorial_programs/ray_triangle_hits.py` | Rewritten with `--mode kernel`, `--mode visible`, `--mode v4`, and `--mode both`. | Teach ray/triangle any-hit as an RTDL kernel relation before showing the V4 Torch-backed any-hit surface. |
| `examples/tutorial_programs/continuation_grouped_sum.py` | Rewritten with `--mode kernel`, `--mode visible`, `--mode v4`, and `--mode both`. | Teach grouped continuation as a post-kernel reduction over relation rows before showing V4 grouped continuation surfaces. |
| `tutorials/current/10_ray_triangle_hits.md` | Added. | Teach ray/triangle hit rows, any-hit output, hit-count/closest-hit variants, and V4 mapping. |
| `tutorials/current/11_grouped_continuations.md` | Added. | Teach grouped count/sum/min/max/argmin/bounded-witness continuation rows and V4 partner-backed mapping. |
| `tutorials/current/README.md` | Updated. | Add lessons 10 and 11 to the public tutorial sequence. |
| `examples/tutorial_programs/README.md` | Updated. | Make commands use `--mode both` for ray hits and grouped continuations. |
| `examples/README.md` | Updated. | Add the repaired ray/continuation examples to the public quick path. |
| `docs/public_documentation_map.md` | Updated. | Add the repaired ray/continuation examples to the public quick check path. |
| `tests/v4_goal4640_public_docs_cleanup_test.py` | Updated. | Include lessons 10 and 11 in public docs scanning and snippet execution. |

## Design Rules Applied

1. Kernel mode remains the programming model.
2. Visible mode mirrors rows and continuations in plain Python.
3. V4 mode shows the measured execution surface after meaning is clear.
4. Group IDs and payloads are explicitly app-owned; the generic continuation
   remains app-free.
5. Partner choices are explicit and not described as broad V4-over-V2 speedup.
6. Scripts remain runnable without CUDA.

## Validation

Windows:

```text
py -3 examples\tutorial_programs\ray_triangle_hits.py --mode both
py -3 examples\tutorial_programs\continuation_grouped_sum.py --mode both
py -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 21 tests in 79.039s
OK
```

Linux clean-copy validation on `192.168.1.20`:

```text
cd /tmp/rtdl_goal4790_ray_cont
PYTHONPATH=src:. python3 examples/tutorial_programs/ray_triangle_hits.py --mode both
PYTHONPATH=src:. python3 examples/tutorial_programs/continuation_grouped_sum.py --mode both
PYTHONPATH=src:. python3 -m unittest tests.v4_goal4640_public_docs_cleanup_test tests.v4_frontdoor_test tests.v4_goal4643_publication_decision_test
```

Result:

```text
Ran 21 tests in 29.775s
OK
```

## Completion Claim

Goal4790 is ready for external review as the ray-hit and grouped-continuation
tutorial batch. The public tutorial ladder now has kernel-first lessons through
spatial primitives, ray/triangle hit rows, and grouped continuations.

This record does not authorize any new performance claim, release claim,
Tier-3 callback claim, raw OptiX callback claim, C ABI claim, embedding claim,
or full paper-reproduction claim.
