# RTDL Runtime Overhead Architecture

Status: current v2.3 release architecture note.

RTDL uses Python as the authoring and orchestration layer. That is the right
shape for a learner-facing eDSL, but it also means performance depends on which
parts of the app stay in Python and which parts move into RTDL engines or
partner tensor code.

## Current Execution Shape

```text
Python RTDL program
  -> compile/lower supported kernel
  -> bind arrays or compact inputs
  -> run RTDL engine traversal
  -> expose rows, witness pages, or compact summaries
  -> optional partner continuation
  -> optional Python materialization
```

The fastest paths minimize Python row materialization. They prefer compact
summaries, bounded witness pages, reusable buffers, and partner-side tensor
reductions.

## Where Time Goes

| Cost center | Why it matters | Preferred v2.x answer |
| --- | --- | --- |
| Python object construction | Large row objects are expensive to build. | Use array inputs and compact output contracts. |
| `ctypes` marshaling | Host copies and struct packing can dominate short kernels. | Reuse prepared buffers where possible. |
| Row materialization | Returning dictionaries is convenient but slow at scale. | Use compact summaries or streaming witness pages. |
| Partner handoff | Copying CPU rows into GPU tensors can erase traversal wins. | Keep data in arrays and use DLPack-compatible handoff where available. |
| Post-processing | Ranking, grouping, filtering, and reductions may dominate. | Use PyTorch, CuPy, NumPy, or app-owned native extensions outside the RTDL engine. |

## Design Rule

Python remains the control plane. The hot data plane should be RTDL engine work
or partner-side array work.

That rule is why v2.x allows PyTorch/CuPy continuation and CuPy RawKernel app
code, while still keeping the native RTDL engine app-agnostic. User-authored
partner kernels are allowed app code; app-customized native engine entry points
are not.

## Output Contracts

| Contract | Best for | Boundary |
| --- | --- | --- |
| Python rows | Debugging, teaching, small inputs | Convenience path, not the fastest path. |
| Raw rows | Lower-overhead app integration | Still may copy or materialize later. |
| Compact summary | Counts, sums, min/max, grouped outputs | Fast when the app does not need witnesses. |
| Streaming witness page | Large witness sets with bounded memory | Better than materializing an unbounded pair table. |
| Partner tensor continuation | Filtering/reducing/ranking after RTDL | Partner code, not RTDL engine customization. |

## Claim Boundary

RTDL performance reports must name the timed boundary:

- traversal only;
- traversal plus compact summary;
- traversal plus partner continuation;
- full app including validation and output.

Only the last one is a whole-app speedup claim.
