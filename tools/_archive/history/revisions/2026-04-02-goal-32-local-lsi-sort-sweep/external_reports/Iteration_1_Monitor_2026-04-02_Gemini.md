### Gemini monitoring note

Closure criteria:
- Goal 31 parity must remain exact on the known reproducers
- the optimization must produce a measurable speedup over the Goal 31 brute-force local baseline
- the final report must keep the current local `lsi` contract explicit as `native_loop`

Invalid closure:
- any parity regression
- any performance claim against the older broken BVH path instead of the Goal 31 baseline
- any report that suggests local `lsi` returned to BVH-backed traversal
