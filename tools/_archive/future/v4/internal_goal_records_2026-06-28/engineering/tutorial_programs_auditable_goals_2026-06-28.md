# Tutorial Programs Auditable Goals

This file turns the current tutorial mandate into checkable goals. It is a
review checklist, not an implementation claim.

## Goal 1: Teach RTDL, Not App Algorithms

Purpose: Tutorials teach the RTDL language and runtime model, not how to build a
specific application such as RayJoin.

Acceptance checks:
- Each tutorial states the RTDL concept it teaches.
- No tutorial claims to teach a full benchmark or paper app algorithm unless it
is explicitly an app guide.
- Paper-reproduction apps are treated as exams or workloads, not curriculum.

Review evidence:
- One-row audit per tutorial file: concept taught, excluded app-specific logic,
and pass/fail.

## Goal 2: No Black-Box "Do It All" Teaching

Purpose: Tutorial programs must show the transformation from user problem to
RTDL relation/operator/continuation, not merely call a wrapper that hides the
model.

Acceptance checks:
- Each tutorial program shows input shape, lowering step, RTDL relation rows or
operator request, continuation, and output interpretation.
- A reviewer can identify where RTDL enters the program.
- Any helper call is explained as a named RTDL surface, not as magic.

Review evidence:
- For every tutorial program, record: input, lowering, RTDL operator, continuation,
output.

## Goal 3: Preserve Three Example Classes

Purpose: Examples are organized into three clean categories.

Acceptance checks:
- Tutorial programs: small concept programs.
- Benchmark apps: the 10 promoted benchmark apps.
- Paper reproduction apps: paper-specific reproduction workloads.
- Links from tutorials and docs point to the correct category.

Review evidence:
- Directory audit table covering `examples/tutorial_programs`,
  `examples/benchmark_apps`, and `examples/paper_reproduction`.

## Goal 4: Cover Core RTDL Features With Small Programs

Purpose: Tutorial programs must cover the main RTDL language features before a
user reaches benchmark apps.

Required coverage:
- hello world / first operator request
- relation rows and candidate rows
- sorting/rank/top-k as relation plus continuation
- nearest neighbor / nearest witness
- fixed-radius neighbors
- point-in-polygon
- line-segment intersection / spatial join
- AABB index predicates
- ray/triangle hits
- grouped reductions
- component union
- aggregate frontier rows
- partner choice: RTDL native, Torch, CuPy, Numba where applicable
- measurement phases
- callback planning boundaries

Acceptance checks:
- Every required feature has at least one runnable tutorial program.
- Each program has a matching tutorial or index entry.

Review evidence:
- Feature-to-program matrix with pass/fail status.

## Goal 5: Build A Progressive Learning Ladder

Purpose: Users should learn from simple RT ideas to benchmark-app building
blocks without being thrown into full apps too early.

Acceptance checks:
- Tutorial order starts from basic RT/RTDL concepts.
- Later lessons reuse concepts introduced earlier.
- Benchmark-app references appear after the small concept programs.

Review evidence:
- Ordered tutorial map showing dependency from each lesson to prior lessons.

## Goal 6: Treat Benchmark And Paper Apps As Exams

Purpose: Benchmark apps and paper reproduction apps validate whether the RTDL
teaching path is sufficient, but they are not themselves the basic lessons.

Acceptance checks:
- Benchmark app docs link back to the concept programs they require.
- Paper-reproduction docs state workload contract, inputs, and run protocol.
- No tutorial teaches external app-specific domain algorithms as RTDL content.

Review evidence:
- For each benchmark/paper app, list the prerequisite RTDL concept tutorials.

## Goal 7: Audit Every Tutorial Code File

Purpose: Every tutorial program must be reviewed for teaching quality, not just
runtime success.

Acceptance checks for each file:
- What concept does it teach?
- What should a user understand after running it?
- Does it hide the important RTDL transformation?
- Is there a clearer teaching path?
- Does it run without special hardware when intended?

Review evidence:
- One audit row per tutorial source file.

## Goal 8: Fix Sorting Tutorial Semantics

Purpose: Sorting must not be taught as plain Python `sorted()` or a hidden
sorting wrapper when the lesson is supposed to teach RTDL thinking.

Acceptance checks:
- The tutorial explains what kind of sorting/ranking problem RTDL is relevant
for.
- It shows the lowering to relation rows: predecessor, distance, hit order,
rank, or top-k.
- It shows continuation from rows to rank/top-k/grouped output.
- It clearly says opaque arbitrary comparators belong to ordinary CPU/GPU sort,
not RT cores.

Review evidence:
- Sorting tutorial audit row plus runnable output showing relation rows and
rank/top-k continuation.

## Goal 9: Fix Nearest-Neighbor Tutorial Semantics

Purpose: Nearest neighbor must teach candidate generation, distance/witness
semantics, and ranked or nearest continuation.

Acceptance checks:
- The tutorial shows queries, indexed points/objects, candidate relation, distance
or witness facts, and nearest/ranked output.
- It does not only call a complete `nearest_neighbor()` helper.
- Partner usage is explicit when Torch/CuPy/Numba is involved.

Review evidence:
- Nearest-neighbor tutorial audit row plus runnable output showing candidate or
witness rows.

## Goal 10: Keep Public Docs Clean And Current

Purpose: Users should see one clean current version, not internal history,
review debt, or old-version confusion.

Acceptance checks:
- Public docs contain no internal process language.
- Public docs contain no stale version instructions.
- Public links resolve.
- Tutorial commands run.

Review evidence:
- Public surface scan.
- Copy-paste command run log.
- Link-resolution report.

