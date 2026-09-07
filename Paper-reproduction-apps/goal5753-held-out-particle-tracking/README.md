# Goal5753 held-out paper application: tetrahedral particle tracking

This directory is the application-only portion of the frozen Goal5753 V4
generalization exam.  The application was selected *after* the exact Goal5752
compiler, Callback IR, verifier, PTX composition, OptiX wrapper and native
runtime were frozen.

The selected paper is:

> Bin Wang, Ingo Wald, Nate Morrical, Will Usher, Lin Mu, Karsten Thompson,
> and Richard Hughes. “An GPU-accelerated particle tracking method for
> Eulerian-Lagrangian simulations using hardware ray tracing cores.”
> Computer Physics Communications 271 (2022), 108221.
> DOI: 10.1016/j.cpc.2021.108221.

The public author implementation is pinned at Git commit
`5cfe63fed227c238905a8f24082b59b5d3160966` from
`https://github.com/BinWang0213/RTXAdvect`.

## Paper algorithm contract

The RT portion constructs a triangle GAS over the unique faces of a
tetrahedral mesh.  One point-location ray starts at each particle, uses the
paper direction `(1, 1e-10, 1e-10)` and a mesh-derived maximum edge length,
and returns the containing tetrahedron from the closest face.  The selected
tetrahedron depends on the triangle front/back hit orientation and per-face
`{front_tet, back_tet}` adjacency.  The paper also uses a displacement ray for
boundary detection before CUDA neighbor walking/reflection.

This is not sphere nearest search.  The required physical inputs are triangle
vertices and indices, face-to-tetra adjacency, primitive face identity,
front/back hit orientation, query position/direction/tmax, and cell/face
outputs.

## Frozen-V4 disposition

The restricted callback in `callback_attempt.py` expresses the analytic
triangle intersection and deterministic cell payload without arbitrary Python
execution.  The independent oracle in `independent_oracle.py` defines exact
tetrahedral point-location semantics without importing the author, V2, V3 or
V4 execution path.

The frozen Goal5752 physical runtime nevertheless admits only
`V4CallbackSphere[]` and builds a custom sphere-AABB GAS.  Its execute ABI has
only four scalar query columns and item/distance/status/counter outputs.  It
has no triangle GAS, vertex/index/adjacency buffers, primitive face identity
or front/back hit-kind channel.  Goal5753 therefore must fail closed at
physical-schema admission.  The core is not changed after observing the
selected application, and no older V3 triangle primitive is substituted for
the frozen V4 runtime.
