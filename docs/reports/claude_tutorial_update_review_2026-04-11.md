# Claude Tutorial Update Review — 2026-04-11

Reviewer: Claude (Sonnet 4.6)
Commit reviewed: `0af7f0c`
Files reviewed:
- `docs/quick_tutorial.md`
- `docs/tutorials/README.md`
- `docs/tutorials/hello_world.md`
- `docs/tutorials/sorting_demo.md`
- `docs/tutorials/nearest_neighbor_workloads.md`
- `docs/tutorials/segment_polygon_workloads.md`
- `docs/tutorials/rendering_and_visual_demos.md`

---

## Verdict

**Pass with minor notes.** The tutorial slice achieves its stated goals. Beginners can now follow a coherent path from first run through kernel anatomy to real workloads, without being misled about released status or backend availability. The `v0.4.0` honesty boundaries are intact. No broken commands, no stale backend claims, and no release-surface dishonesty were found. The issues below are small and none is a blocker.

---

## Findings

### 1. Teaching quality: beginners can now write RTDL programs

**Strong.** The slice now teaches kernel writing, not just demo running.

- `quick_tutorial.md` introduces the four-step kernel shape (`input -> traverse -> refine -> emit`) with annotated code and explains why Python owns the wrapper.
- `hello_world.md` does a full line-by-line walkthrough. Every `rt.*` call is explained individually. This is the best entry point for a beginner who wants to understand what is happening rather than just running something.
- `segment_polygon_workloads.md` and `nearest_neighbor_workloads.md` each show the actual kernel for every workload with parameters explained and a "use when" decision guide.
- `rendering_and_visual_demos.md` uses the demos to demonstrate the RTDL/Python composition boundary, not just to show pretty output.

The one slightly weaker tutorial on this dimension is `sorting_demo.md`, which intentionally omits the kernel code and points to source files instead. The tutorial acknowledges this is deliberate ("this is mainly for the second lesson"). That framing is acceptable; the kernel anatomy is well-covered elsewhere in the ladder.

### 2. Command style: consistent and cross-platform enough

**Acceptable, with one gap.**

The cross-platform pattern is:

- Bash: `PYTHONPATH=src:. python ...`
- A note at the top of each tutorial: "if your shell only provides `python3`, substitute `python3`"
- Windows `cmd.exe` blocks where needed

The pattern is applied in: `quick_tutorial.md`, `hello_world.md`, `sorting_demo.md`, `rendering_and_visual_demos.md`.

**Gap:** `segment_polygon_workloads.md` and `nearest_neighbor_workloads.md` include the python/python3 note but do not provide Windows `cmd.exe` equivalents for any of their run commands. For the segment/polygon tutorial this is a minor omission since those are the multi-step workload commands, but it is inconsistent with the rest of the slice. Lowest-priority finding.

### 3. `v0.4.0` honesty boundaries: preserved correctly

**Clean.**

- `nearest_neighbor_workloads.md` labels the workloads as `v0.4.0` additions at the top and does not claim more than what is released.
- The OptiX/Vulkan qualification is appropriately hedged: "availability depends on the machine and local runtime setup. Use the feature and support-matrix docs for the exact platform story." No false availability promises.
- `rendering_and_visual_demos.md` correctly frames RTDL as "not a rendering engine" and lists exactly what RTDL handles (traversal/refine/emit rows) versus what Python handles (shading, scene, animation, output).
- `segment_polygon_workloads.md` correctly labels those workloads as `v0.2.0`, not as new `v0.4.0` additions.

No stale backend claims were found. The tutorials do not reference any build system, import path, or backend contract that was known to be wrong at `v0.4.0`.

### 4. Structural issues: links, expressions, duplication, misleading claims

**One navigation oddity; no broken expressions or misleading claims.**

**Navigation oddity:** `rendering_and_visual_demos.md` is placed at step 5 (final step) in the tutorial ladder, but its "Next" section links backward to `segment_polygon_workloads.md` and `nearest_neighbor_workloads.md` — tutorials at steps 3 and 4. A beginner who finishes step 5 and clicks "Next" will be sent back to earlier material with no obvious forward path. The README's "After The Tutorials" section fills the forward gap, but it is only in `tutorials/README.md`, not in the terminal rendering tutorial itself. Low impact; a "Back to tutorial index" link would close this without adding noise.

**Kernel pattern repetition:** The four-step `input -> traverse -> refine -> emit` explanation appears in `quick_tutorial.md` (overview), `hello_world.md` (line-by-line), and is referenced again in subsequent workload tutorials. This is appropriate layered teaching, not harmful duplication. Each recurrence adds a different layer: overview, line-by-line anatomy, then concrete workload application.

**No broken links detected** within the reviewed files (all tutorial-to-tutorial links use consistent relative paths from `docs/tutorials/`). The `tutorials/README.md` "After The Tutorials" section links to `../release_facing_examples.md`, `../features/README.md`, `../rtdl/README.md`, and `../v0_4_application_examples.md`; these were not verified in this review but are not part of the tutorial slice itself.

**No misleading claims** were found. The language is careful throughout: "released workload families," "if your machine is configured for GPU backends," "bounded pathology-style overlap contract" for `polygon_set_jaccard`, and similar qualifications are used correctly and consistently.

---

## Risks

**Low.** No high-severity risks identified. The following are tracked for completeness:

| Risk | Severity | Notes |
| --- | --- | --- |
| Missing Windows cmd.exe blocks in segment/polygon and nearest-neighbor tutorials | Low | Inconsistent but not wrong; Linux/macOS users unaffected |
| `rendering_and_visual_demos.md` "Next" links point to earlier ladder steps | Low | Could confuse a beginner who follows "Next" from the final tutorial |
| "After The Tutorials" destination links not verified in this review | Low | These exist outside the tutorial slice; a dead link there would not affect beginner onboarding but would be found immediately on use |

---

## Conclusion

The tutorial-update slice is in good shape for the public `v0.4.0` surface. The three core goals are met:

1. Beginners can now read a kernel, understand each line, and write their own — not just run supplied examples.
2. Command style is consistent and cross-platform for the four most-trafficked tutorials; the two workload tutorials have a minor Windows gap.
3. The `v0.4.0` honesty boundaries — released status, backend availability, rendering framing — are correctly drawn throughout.

The two low-priority items (Windows blocks in segment/polygon and nearest-neighbor; the rendering "Next" navigation) can be deferred or addressed in a future pass without affecting the beginner experience in any significant way.
