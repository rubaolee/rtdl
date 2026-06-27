## Claude independent proposal

- Root cause: the current local `lsi` candidate path still truncates through float-based Embree ray/bounds internals and remains structurally fragile for exact-source GIS segments.
- Preferred fix: replace the BVH/`rtcIntersect1` path with a parity-safe native double-precision candidate path.
- Claude's recommended optimization form was a native sort-sweep candidate pass.
- Claude explicitly approved removing the broken BVH path from active local `lsi` execution.

Claude recommendation:

> APPROVE the parity-safe native replacement of the current BVH path. Treat any future BVH-backed redesign as a later optimization round.
