## Goal 17 Final Consensus

Decision: Accept Goal 17 first slice as complete.

Accepted result:

- the Python-like DSL remains unchanged
- RTDL now has packed native-ready input containers for:
  - segments
  - points
  - polygons
- RTDL now has a prepared Embree execution API for:
  - `lsi`
  - `pip`
- RTDL now has a thin native result-view path through `EmbreeRowView`

Measured outcome:

- the ordinary dict-return prepared path is not the real performance win
- the packed + prepared + raw-row path is the successful first slice
- on the Goal 15 comparison fixtures:
  - `lsi` raw speedup vs current RTDL Embree: about `31.81x`
  - `pip` raw speedup vs current RTDL Embree: about `51.40x`

Validation:

- `PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py'`
  - `Ran 74 tests ... OK`
- `PYTHONPATH=src:. python3 scripts/goal17_compare_prepared_embree.py`
  - passed and produced benchmark JSON

Review closure:

- Claude accepted the first slice in `Iteration_3_Final_Review_2026-03-31_Claude.md`
- Gemini accepted the first slice in `Iteration_3_Final_Review_2026-03-31_Gemini.md`

Conclusion:

- Goal 17 first slice is complete by Codex + Claude + Gemini consensus.
- The repo now has measured evidence that the Python-like DSL can be preserved while materially reducing the host/runtime overhead on Embree, provided the execution path uses packed inputs and a thin raw result view.
