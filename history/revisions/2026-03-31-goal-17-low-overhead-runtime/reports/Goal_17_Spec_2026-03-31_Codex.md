## Goal 17 Spec

Title: Low-Overhead Embree Runtime

Primary objective:
- keep the Python-like RTDL authoring surface
- reduce runtime overhead enough that the Embree execution path moves materially closer to the pure native C++ + Embree comparison path

Immediate first slice:
- introduce a prepared low-overhead execution path for `lsi` and `pip`
- add native-ready packed buffers for their input forms
- compare current RTDL Embree vs packed/prepared RTDL Embree vs native Goal 15 paths

Evidence basis:
- Goal 15 measured roughly `7.6x` slowdown for `lsi`
- Goal 15 measured roughly `37.4x` slowdown for `pip`

Acceptance bar:
- correctness parity preserved
- measurable performance improvement
- honest report about remaining native gap
- final closure only after Codex + Claude + Gemini agreement
