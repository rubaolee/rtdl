# Fresh-Student RTDL User Experience Report

Date: 2026-05-10

Repository under test:

- path: `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`
- branch: `main`
- commit: `0d6e9d4fe47dac6f980a89fdeb2fc4e6a92141c1`

Perspective:

This report treats the reviewer as a fresh RTDL learner and user. The test
starts from the public front page, follows the documented docs/tutorial/example
paths, runs first-user commands, and judges whether the language surface and
documentation feel coherent without maintainer context.

## Verdict

RTDL is learnable from the current front page, docs index, quick tutorial, and
tutorial ladder. The core language idea is now clear: Python owns the app,
RTDL owns an `input -> traverse -> refine -> emit` kernel, and backends execute
supported RT-shaped primitive paths. The first-run commands work on Windows
with the portable CPU Python reference backend.

The remaining user-experience problem is consistency after the clean front
door. Some secondary user paths still expose version-history and maintainer
language too early, especially `docs/app_example_quickstart.md`,
`examples/README.md`, and `docs/release_facing_examples.md`. A fresh student
can run RTDL, but after the first success they may become uncertain whether
they are learning a current product, a release archive, or a research project
with many historical goal boundaries.

Release recommendation from this UX test:

- Good enough as a technical release candidate for users who tolerate research
  system docs.
- Not yet ideal as a polished first-learner experience.
- Before calling the docs broadly beginner-ready, clean the secondary entry
  pages so they describe the current product first and move v0.x/v1.x/Goal
  history behind history or evidence links.

## Learning Notes By Public Entry

### Front Page: `README.md`

What I learned:

- RTDL is a Python-hosted ray-tracing DSL/runtime for non-graphics workloads.
- I should set `PYTHONPATH` and run source-tree examples.
- The language shape is small and memorable: `input -> traverse -> refine -> emit`.
- RTDL is not a renderer and not a blanket performance claim.
- There is a public 4K visual demo, but it is framed as a demo, not the core
  product definition.

Fresh-student experience:

- Strong. The opening paragraphs explain the product in plain terms.
- The first commands are immediately runnable.
- The kernel snippet gives a concrete mental model before sending me deeper.
- The performance boundary is honest and useful.

Issue:

- The front page links to many next pages. That is acceptable, but a complete
  beginner may still wonder which single app to learn after hello world.

### Docs Index: `docs/README.md`

What I learned:

- There is a recommended new-user path.
- The docs separate tutorials, feature guides, backend setup, performance
  interpretation, architecture, and history.
- The docs explicitly warn that GPU speedups are workload-specific.

Fresh-student experience:

- Good. This is the cleanest navigation page.
- The "Read By Task" table is practical and easy to follow.
- The separation of history from current docs is the right design.

Issue:

- The "Performance Evidence" section links directly to a dated dual-GPU goal
  report. That is evidence-correct, but it feels like a maintainer artifact
  inside a user docs index. A short stable "Current Performance Evidence" page
  would be easier for a new user.

### Quick Tutorial: `docs/quick_tutorial.md`

What I learned:

- How to create a Python environment.
- How to run the first command.
- How to read and write the canonical kernel shape.
- How to switch backend runners while keeping the kernel shape stable.
- How to interpret `reduce_rows` and GPU boundaries cautiously.

Fresh-student experience:

- Strong. This is the best first learning document.
- The tutorial uses simple commands and expected outputs.
- The language explanation is concise.

Issue:

- The setup section starts with Unix `python3 -m venv`, then explains Windows
  in prose. Since Windows is a common target for this repo, a dedicated Windows
  setup block would reduce friction.
- The tutorial says `cpu` auto-builds a native oracle library, while the front
  page recommends starting with `cpu_python_reference`. This is not a conflict,
  but a new user may need a clearer "only use `cpu_python_reference` until you
  intentionally want native builds" sentence.

### Tutorial Ladder: `docs/tutorials/README.md`

What I learned:

- There is a progression from hello world to feature families to app demos.
- The docs distinguish language basics, workload tutorials, and application
  demos.
- Rendering demos are explained as RTDL-plus-Python composition, not as RTDL
  being a renderer.

Fresh-student experience:

- Good. The ladder gives a believable path.
- The "three learning tracks" structure helps me choose what to read next.

Issue:

- Steps 9-13 point directly at example source files rather than tutorial pages.
  That is fine for experienced users, but less tutorial-like for students.
- The ladder could use one explicit "write your first custom kernel" exercise
  after hello world.

### App And Example Quickstart: `docs/app_example_quickstart.md`

What I learned:

- Which apps exist and what RTDL contributes to each.
- RTDL often accelerates a sub-path rather than the whole application.
- OptiX/RTX claims require exact reviewed modes.

Fresh-student experience:

- Mixed. The app table is useful, but the page quickly becomes maintainer
  language.
- Terms like "v1.6", "v1.0-era app-specific native continuations",
  "proof machinery", and "current Python+RTDL architecture milestone" make the
  page feel historical rather than like a beginner app quickstart.

Issue:

- This page currently violates the product-doc boundary more than the front
  page and docs index. A fresh user should not need to learn RTDL history before
  choosing an app.
- Recommendation: keep the app table, first commands, and "do not claim"
  boundaries; move version evolution, v1.0 inventory, and proof-machinery text
  behind a history/evidence link.

### Examples Index: `examples/README.md`

What I learned:

- There are many runnable examples and apps.
- The first few examples are clear: hello world, backend selection, feature
  cookbook, nearest-neighbor, Hausdorff, apps, visual demos.
- The repo has compatibility helpers and historical/internal materials.

Fresh-student experience:

- Mixed to weak after the initial inventory.
- The top table is useful, but it immediately includes "Current release:
  v1.6", a v1.6 release package link, a v1.0 app acceleration inventory link,
  and long v0.x/v1.x boundary sections.
- As a student, I would not know which parts are current instructions and which
  parts are archival release notes.

Issue:

- This file is the largest remaining inconsistency with the cleaned front door.
- Recommendation: split it into a compact current `examples/README.md` plus an
  `examples/HISTORY.md` or docs/history entry for old release boundaries.

### Programming Guide: `docs/rtdl/programming_guide.md`

What I learned:

- How to author kernels correctly.
- What roles, geometry types, predicates, and execution paths mean.
- The runtime input shape matters as much as the DSL syntax.

Fresh-student experience:

- Good for a second-stage learner.
- The "runtime input shapes" section is especially helpful because fresh users
  can otherwise write correct-looking kernels but pass wrong host data.

Issue:

- The guide says `rt.run_cpu(...)` is the oracle and the old Python reference
  path is still available, while the quick tutorial says start with
  `rt.run_cpu_python_reference(...)`. This is explainable, but a student may
  wonder which one is truly first-choice.
- Recommendation: explicitly label `cpu_python_reference` as beginner-safe and
  `cpu` as native-oracle/validation-oriented.

### DSL Reference: `docs/rtdl/dsl_reference.md`

What I learned:

- The accepted language is intentionally small.
- Kernels have no Python arguments.
- The implemented surface is finite and listed.
- Geometry field contracts are defined.

Fresh-student experience:

- Good reference page, not a tutorial.
- The grammar and required rules make the language feel reasonable and bounded.

Issue:

- The DSL reference does not by itself teach host-side input construction.
  That is acceptable because the programming guide covers it, but the reference
  should keep a strong cross-link to runtime input examples.

### Visual Demo Tutorial: `docs/tutorials/rendering_and_visual_demos.md`

What I learned:

- RTDL can be used as a geometry-query core inside a Python rendering-style
  demo.
- RTDL handles primary visibility and shadow-ray queries.
- Python handles scene setup, shading, animation, and output.
- The 4K hidden-star demo has a public video and work report.

Fresh-student experience:

- Good and honest.
- It correctly says RTDL is not a renderer.
- It gives a small runnable command before pointing to the 4K artifact.

Issue:

- The 4K hidden-star demo deserves a dedicated tutorial page if it is meant to
  be public-facing. The current tutorial mentions it, but does not deeply teach
  the primary-ray/shadow-ray construction or chunked scaling path.

### Release-Facing Examples: `docs/release_facing_examples.md`

What I learned:

- There is a large command archive and lots of evidence boundaries.
- Many backend and release details are preserved.

Fresh-student experience:

- Weak as a learner page.
- It is too historical and goal-heavy to be called a first-user example guide.
- It is valuable as an evidence archive, but not as a clean tutorial.

Issue:

- This page should not be in the beginner route except as "full command
  archive / evidence". The quick tutorial currently points to it as "full
  command archive", which is acceptable, but the label should make clear that
  it is not the next learning page.

## Commands Tested

All commands were run from the repository root on Windows with:

```powershell
$env:PYTHONPATH = "src;."
```

Passing commands:

```powershell
py -3 examples/rtdl_hello_world.py
py -3 examples/rtdl_hello_world_backends.py --backend cpu_python_reference
py -3 examples/rtdl_fixed_radius_neighbors.py --backend cpu_python_reference
py -3 examples/rtdl_hausdorff_distance_app.py --backend cpu_python_reference
py -3 examples/rtdl_feature_quickstart_cookbook.py
py -3 examples/visual_demo/rtdl_lit_ball_demo.py --backend cpu_python_reference --compare-backend none --width 24 --height 12 --triangles 32 --output NUL
py -3 examples/visual_demo/rtdl_hidden_star_stable_ball_demo.py --backend cpu_python_reference --compare-backend none --width 24 --height 12 --latitude-bands 4 --longitude-bands 8 --frames 1 --jobs 1 --shadow-mode rtdl_light_to_surface --output-dir build/ux_fresh_student_hidden_star_smoke
```

Observed output:

- All commands completed successfully.
- The expected JSON or ASCII output appeared.
- The visual hidden-star smoke produced
  `build/ux_fresh_student_hidden_star_smoke/frame_000.ppm`.

Minor Windows environment issue:

- Each `py -3` run printed `Could not find platform independent libraries
  <prefix>` after or before normal output.
- The commands still passed, so this appears to be local Python environment
  noise rather than an RTDL failure.
- A fresh student may misread it as a problem. If this is common on this
  machine only, ignore it; if it appears on clean Windows machines, document a
  Python install sanity check.

## Language Reasonableness

The language is reasonable for the stated goal.

Strong points:

- The kernel grammar is small and teachable.
- The same `input -> traverse -> refine -> emit` shape appears across docs.
- `probe` and `build` roles make sense once examples show query-vs-indexed
  geometry.
- Predicate names map well to workload intent: `knn_rows`,
  `fixed_radius_neighbors`, `ray_triangle_any_hit`, `visibility_rows`.
- The docs honestly separate RTDL kernel work from Python app continuation.

Confusing points:

- `backend="rtdl"` in `@rt.kernel(...)` plus `--backend embree/optix` at runtime
  can confuse beginners until explained. The docs do explain it, but this
  deserves an early one-line rule: kernel backend declares RTDL language
  lowering; runner/backend selects execution.
- `cpu`, `cpu_python_reference`, and "oracle" are not consistently introduced
  as beginner-safe vs validation/native paths.
- `reduce_rows` is a public helper, but users may assume it is always backend
  accelerated. The quick tutorial now warns against that; keep that warning
  visible.

## Consistency Judgment

Consistent:

- Front page, docs index, quick tutorial, tutorial ladder, programming guide,
  and DSL reference agree on the main language shape.
- Backend/performance boundaries are repeatedly stated and are appropriately
  conservative.
- The 4K visual demo docs honestly frame RTDL as a query core, not a renderer.

Inconsistent or still too historical:

- `docs/app_example_quickstart.md` still reads partly like a v1.6/v1.0
  transition memo rather than a current user guide.
- `examples/README.md` still contains long historical release-boundary sections.
- `docs/release_facing_examples.md` is useful evidence but too large and
  goal-heavy for learners.
- Some docs say "current release v1.6" while current release-prep work has
  v1.6.11 performance evidence. If version numbers remain in user docs, they
  must be exact and centrally managed; otherwise remove them from beginner
  pages.

## Priority Fixes

1. Productize `docs/app_example_quickstart.md`.
   Keep first commands and app table. Move v1.0/v1.6 proof-machinery discussion
   to history/evidence docs.

2. Productize `examples/README.md`.
   Keep a short current inventory and link to history for old release
   boundaries. Do not make fresh users scroll through v0.x/v1.x release
   archaeology.

3. Rename or reframe `docs/release_facing_examples.md`.
   Treat it as a command archive/evidence page, not as a learner tutorial.

4. Add one dedicated "write your first custom kernel" exercise.
   The docs show kernels well, but a student would benefit from modifying a
   small fixed-radius or any-hit example and seeing the output change.

5. Add a dedicated 4K hidden-star demo tutorial if the video is meant to be a
   public showcase.
   It should explain the small smoke run, primary rays, light-to-surface shadow
   rays, Python shading boundary, and chunked 4K scaling.

6. Clarify beginner backend naming.
   Use `cpu_python_reference` as the first-run teaching backend. Introduce
   `cpu` as native/oracle validation only after the first examples are working.

## Final UX Judgment

As a fresh RTDL student, I can learn the core language and run examples from
the current docs. The product concept is understandable and the DSL is
reasonable. The best pages are now genuinely user-facing.

The main remaining issue is that the second layer of docs still leaks project
history into the user path. That does not block technical users, but it weakens
the release polish. The next documentation pass should not change the language;
it should clean the learning route so a new user sees current RTDL first,
evidence/history only when they ask for it.
