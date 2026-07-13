# Author Patch Notes

The RT-BarnesHut author artifact is kept external and is cloned by
`scripts/setup_author_official.sh`.

Allowed compatibility edits:

- add a CUDA compile flag equivalent to `-include array` for modern CUDA/GCC;
- use CUDA device ordinal `0` on single-GPU pods when the sample hardcodes
  ordinal `1`;
- rebuild with a controlled `NUM_POINTS` value for reproduction-sized runs.
- expose an optional `RTBH_FORCE_OUT` per-body force dump after the measured
  RT-core force phase. This is comparator instrumentation; it must not be
  counted inside the reported force timing.

These edits are environment, experiment-control, and comparator-observation
patches. They do not authorize algorithm changes. If a future patch changes
tree construction, traversal, force accumulation, input loading, or output
formatting, document it here as comparator-affecting before using it in a
paper-reproduction claim.
