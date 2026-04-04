# Goal 69 Status: PIP Performance Repair

Date: 2026-04-04

Current status:
- complete
- ready to publish
- final measured package imported
- Codex review complete
- Gemini review complete
- the earlier SSH/banner-exchange failures are no longer the main critical-path
  issue
- the broader measured Linux package is now reported parity-correct for:
  - OptiX
  - Embree
  on both:
  - `county_zipcode`
  - `blockgroup_waterbodies`
- the remaining work is final summary/review preparation before any publish
- the exact measured summary artifact(s) are now mirrored into this local tree
- final timing values are recorded in the Goal 69 result package

What is implemented locally:
- `rt.point_in_polygon(..., result_mode="positive_hits")`
- `rt.contains(..., result_mode="positive_hits")`
- Python reference/runtime support for sparse positive-hit PIP rows
- native oracle, Embree, OptiX, and Vulkan support for the new PIP result mode
- additional sparse-path improvements:
  - Python reference positive-hit mode now bbox-prunes before exact PIP
  - native oracle positive-hit mode now bbox-prunes before exact PIP
  - Embree positive-hit mode now emits only actual hit polygon ids instead of scanning all polygons after each point query
  - OptiX positive-hit mode is being revised from duplicate-prone sparse-hit counting to a per-pair hit-bitset path followed by host compaction
- Goal 69 positive-hit performance harness:
  - `scripts/goal69_pip_positive_hit_performance.py`

What is preserved:
- default `pip` semantics remain `result_mode="full_matrix"`
- accepted Goal 50 / Goal 59 parity claims remain unchanged
- performance priority in this goal is:
  - OptiX first
  - Embree second
  - Vulkan later
  - native C oracle only as correctness reference

Local validation:
- targeted tests passed:
  - `tests.test_core_quality`
  - `tests.rtdsl_py_test`
  - `tests.goal69_pip_positive_hit_performance_test`
- total in the current focused run: `113` tests, `OK`
- most recent focused rerun after the latest local paper/performance edits:
  - `tests.rtdsl_py_test`
  - `tests.goal69_pip_positive_hit_performance_test`
  - total: `19` tests, `OK`

Local micro-check:
- earlier synthetic CPU full-matrix PIP:
  - rows: `10000`
  - time: about `0.013652 s`
- earlier synthetic CPU positive-hit PIP:
  - rows: `120`
  - time: about `0.000666 s`
- current small bbox-pruned CPU micro-check:
  - full-matrix: `2000` rows, about `0.006076 s`
  - positive-hit: `1300` rows, about `0.004568 s`

Interpretation:
- the new positive-hit mode is materially reducing emitted row count and CPU time
- Embree now has a real algorithmic sparse-path improvement, not just reduced output materialization
- the first OptiX sparse design was not acceptable:
  - it counted raw any-hit events
  - one true point/polygon positive could be duplicated many times by polygon-edge intersections
- the current local OptiX repair instead marks one boolean hit flag per point/polygon pair and compacts positives afterward
- the latest local OptiX revision packs those boolean flags into a 32-bit bitset,
  reducing the sparse positive-hit mask footprint by `8x` relative to the
  earlier byte-per-pair flag array
- this does not yet prove the accepted bounded package timings
- the real Linux run is still required

Remote status:
- fresh workspace synced to `~/work/rtdl_goal69_run`
- stale local SSH/rsync sessions were one real source of remote instability and were cleared
- after that cleanup, a narrower OptiX-only `county_zipcode` run was launched successfully
- that narrow run showed a materially better memory profile than the earlier broken run
- the run then exposed the duplicate-hit flaw in the first OptiX sparse design and was stopped intentionally
- the current blocker is finishing the OptiX bitmap-path rebuild/rerun cleanly on `192.168.1.20`
- remote reachability remains intermittent in this shell:
  - some checks succeed
  - others still time out during banner exchange
- the latest direct probe in this session again failed with:
  - `Connection timed out during banner exchange`
  - `Connection to 192.168.1.20 port 22 timed out`
- next remote step should be a narrower rerun once the host is reachable again:
  - county/zipcode alone
  - OptiX first
  - then Embree
  - CPU only if needed as a correctness cross-check

Updated execution state:
- Goal 69 execution has now progressed beyond the earlier blocked handoff
- the broader measured Linux package is reported parity-correct for both OptiX
  and Embree on:
  - `county_zipcode`
  - `blockgroup_waterbodies`
- the correct next step is no longer rerunning the backend path blindly; it is
  final publication of the reviewed result package

Open questions:
1. no blocking open question remains within Goal 69
2. later goals may still pursue larger OptiX, Embree, and Vulkan performance
   improvements beyond the positive-hit `pip` scope closed here
