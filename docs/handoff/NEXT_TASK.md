# Next Task

Primary task:
- resume Goal 69: OptiX-first PIP performance repair

Immediate target:
- get a real Linux timing result for the narrow `county_zipcode` OptiX-only positive-hit run

Exact order:
1. verify SSH access to `lestat-lx1`
2. sync the latest local tree to the Linux workspace
3. rebuild OptiX on Linux
4. run Goal 69 with:
   - `county_zipcode` only
   - `optix` only
5. collect and inspect:
   - parity
   - row count
   - timing
   - memory behavior
6. if OptiX result is valid, run the same positive-hit contract for Embree
7. write/update the Goal 69 status/result docs
8. get Gemini review before any publish

Secondary task:
- continue paper professionalization only after the performance run is back on track
- the paper needs:
  - figure redesign
  - another Gemini review
  - continued prose cleanup where needed

Important boundaries:
- OptiX performance is first
- Embree is second
- Vulkan is not the current performance focus
- C oracle is correctness-only
