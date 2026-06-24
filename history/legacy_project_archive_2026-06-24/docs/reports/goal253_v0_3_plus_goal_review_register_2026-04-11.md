# Goal 253 Register: v0.3+ Goal Review Register

Date: 2026-04-11

This register lists every in-scope goal from Goal 161 forward with its purpose, stated status, and saved-consensus status under the current project rule.

| Goal | Status | Consensus | Purpose |
| --- | --- | --- | --- |
| 161 | unspecified | compliant | After the `v0.2.0` release, the highest-value next direction is a user-facing demo that is immediately understandable and visually attractive. |
| 163 | unspecified | compliant | After the visual-demo OptiX hitcount mismatch, the correct response is not just to patch that one case. We need a bounded retest over the historical OptiX-related task surface to know whether current `main` is still coherent. |
| 164 | unspecified | compliant | Goal 161 chartered a real `v0.3` visual demo where RTDL owns the heavy geometric-query work and Python owns scene setup, shading, and media output. |
| 165 | unspecified | compliant | Goal 164 closed the first true 3D spinning-ball backend line with row-level Linux parity across all four backends. The demo runs and the parity is clean. |
| 166 | unspecified | compliant | The first attractive `v0.3` visual artifact should be a clean, cinematic RTDL demo that users can understand immediately. |
| 167 | unspecified | compliant | Purpose |
| 168 | unspecified | compliant | After Goal 167 and the smoother `softvis` follow-up artifact, the repository needs one current-status package that says clearly: |
| 169 | unspecified | compliant | Close two bounded `v0.3` backend goals in parallel for the orbiting-star 3D demo line: |
| 170 | unspecified | compliant | Produce small, honest Linux demo artifacts for the orbiting-star 3D demo line on the two GPU-facing backends already closed in Goal 169: |
| 171 | unspecified | compliant | Refresh the front-surface documentation so the repository tells one consistent post-Goal-170 `v0.3` story: |
| 172 | unspecified | compliant | Add a bounded temporal-stability option to the orbiting-star visual demo line so the current movie path can reduce abrupt frame-to-frame lighting pops without changing the RTDL geometric-query surface. |
| 173 | unspecified | compliant | Accept the finished Windows Embree 4K movie artifact as-is under the normal review flow, without claiming that the remaining temporal blink is fully solved. |
| 174 | unspecified | compliant | Update the front-surface docs to the latest `v0.3` state after Goal 173: |
| 175 | unspecified | compliant | Build the next bounded `v0.3` 4K movie variant by extending the accepted Windows Embree orbiting-star scene from one main yellow star to two stars: |
| 176 | unspecified | compliant | Strengthen the Linux validation surface for the `v0.3` 3D orbiting-star demo on: |
| 177 | unspecified | compliant | Produce small, compare-clean Linux GIF artifacts for the synchronized two-star variant of the orbiting-star 3D demo, with both stars using the same warm yellow family and a fully symmetric equator flight path. |
| 178 | unspecified | compliant | The moving-star variants produced visible temporal blinking in dark regions, especially near the lower-left ground/ball transition. The next bounded experiment is to keep RTDL as the geometric-query core while replacing moving-light drama with smoother camera motion. |
| 179 | unspecified | compliant | Goal 178 introduced a smoother camera-orbit demo shape to replace the flicker-prone moving-light composition. Goal 179 extends that new demo to the Linux GPU backend paths so OptiX and Vulkan can both demonstrate the same smoother scene with bounded, compare-clean preview artifacts. |
| 180 | unspecified | compliant | The `v0.3` line is already strong technically, but it is not yet cleanly finished as a public-facing package. The remaining work is no longer about proving that RTDL can participate in 3D demo workloads. It is about closing the remaining flagship-demo and release-surface gaps under the repo's `2+` AI consensus rule. |
| 181 | unspecified | compliant | The moving-light orbit demos proved RTDL can participate in real graphics workloads, but they never became acceptable flagship artifacts because of visible temporal blinking. The smooth-camera line is the first bounded replacement that is structurally aimed at the real problem: |
| 182 | unspecified | compliant | Goal 179 proved that the newer smooth-camera demo shape runs compare-clean on the Linux GPU backend paths. Goal 182 is the packaging step that turns those bounded validation runs into explicit supporting `v0.3` artifacts instead of leaving them as only an execution note. |
| 184 | unspecified | compliant | The `v0.3` line needs a final bounded package that says, plainly and honestly: |
| 185 | unspecified | compliant | The moving-star orbit concept is still the most intuitive visual story in the `v0.3` demo line: |
| 186 | unspecified | compliant | The repo front surface should point readers to the strongest current public-facing video entry point for the `v0.3` visual-demo line. The previous front-surface link was valid, but the newly uploaded Shorts URL is now the preferred public video surface. |
| 187 | unspecified | compliant | The `v0.3` line now has multiple preserved demo variants, multiple review packages, and a final status package. Before treating the line as closure-ready, the repo needs one bounded audit that checks: |
| 189 | unspecified | compliant | Reconstruct the native RTDL engines so they are no longer maintained as single-file monoliths. |
| 190 | unspecified | compliant | Move the application-style 3D demo programs out of the flat `examples/` root and into a dedicated `examples/visual_demo/` package, then update the codebase and docs to use the new paths consistently. |
| 191 | unspecified | compliant | Run a comprehensive pre-release verification sweep across the RTDL stack, from the initial rayjoin-style workloads through the bounded 3D visual demo layer, using selected small artifacts rather than expensive production renders. |
| 192 | unspecified | compliant | Perform a comprehensive pre-release documentation review so that the final `v0.3` surface is internally consistent, technically honest, and easy for users to follow. |
| 193 | unspecified | compliant | Decide what `v0.4` should be after the `v0.3.0` release. |
| 194 | unspecified | compliant | Turn the `v0.4` direction decision into a concrete package the next version can start from immediately. |
| 195 | planned | compliant | Turn the settled `v0.4` nearest-neighbor direction into an executable plan with: |
| 196 | planned | compliant | Freeze the first public `v0.4` workload contract: |
| 197 | planned | compliant | Add the public DSL/Python surface for the first `v0.4` workload: |
| 198 | planned | compliant | Build the first executable truth path for `fixed_radius_neighbors`. |
| 199 | planned | compliant | Make `fixed_radius_neighbors` fully working on the correctness-first native CPU/oracle path. |
| 200 | unspecified | compliant | Close the first accelerated backend for `fixed_radius_neighbors` without changing the accepted workload contract. |
| 201 | unspecified | compliant | Add the first external baseline harness for `fixed_radius_neighbors`. |
| 202 | planned | compliant | Freeze the second public `v0.4` workload contract: |
| 203 | planned | compliant | Add the public DSL/Python surface for the second `v0.4` workload: |
| 204 | planned | compliant | Build the first executable truth path for `knn_rows`. |
| 205 | unspecified | compliant | Close the first correctness-complete native execution path for `knn_rows` by extending the RTDL CPU/oracle runtime, preserving the frozen Goal 202 contract and matching the Goal 204 Python truth path exactly. |
| 206 | unspecified | compliant | Close the first accelerated backend for `knn_rows` by extending the Embree runtime while preserving the Goal 202 contract and Goal 205 CPU/oracle semantics. |
| 207 | unspecified | compliant | Add the first external baseline harness for `knn_rows`. |
| 208 | unspecified | compliant | Add the first clean public example chain for the `v0.4` nearest-neighbor line. |
| 209 | unspecified | compliant | Close the remaining `v0.4` acceptance item requiring at least one benchmark or scaling note for the new nearest-neighbor workload family. |
| 210 | unspecified | compliant | Finish the remaining documentation acceptance items for the active `v0.4` nearest-neighbor line by adding a preview release statement and preview support matrix, then wiring those documents into the live docs index. |
| 211 | unspecified | compliant | Remove stale `v0.4` wording from the live language/feature docs now that the nearest-neighbor family is no longer merely planned. |
| 212 | unspecified | compliant | Perform one full-slice audit of the entire `v0.4` nearest-neighbor line: |
| 213 | executed | compliant | Prepare the canonical `v0.4` release-report package before the final post-`4am` Claude whole-line audit. |
| 214 | unspecified | compliant | Turn the nearest-neighbor `v0.4` line into a small application-facing package: |
| 215 | proposed | compliant | Re-open `v0.4` under the stricter project bar that new public workloads must reach GPU RT-core backends, not only CPU/oracle and Embree. |
| 216 | unspecified | compliant | Close `fixed_radius_neighbors` on OptiX for `v0.4`. |
| 217 | unspecified | compliant | Close `knn_rows` on the OptiX backend for the reopened `v0.4` GPU-required scope. |
| 218 | unspecified | compliant | Make `fixed_radius_neighbors` runnable on Vulkan for the reopened `v0.4` scope. |
| 219 | unspecified | compliant | Make `knn_rows` runnable on Vulkan for the reopened `v0.4` scope. |
| 220 | completed | compliant | Refresh the live `v0.4` status pages so they match the reopened GPU-required bar and the now-running nearest-neighbor GPU workload surfaces. |
| 222 | in progress | compliant | Close the remaining Windows and harness portability gaps that were exposed by the broad Windows pre-release reruns and by the repo-wide command/test surface. |
| 223 | in progress | compliant | Expose Vulkan through the baseline/harness surface for the new nearest-neighbor workloads so the reopened `v0.4` line no longer has a harness visibility gap. |
| 224 | in progress | compliant | Close the reopened GPU implementation goals with explicit review notes and honest status documentation. |
| 225 | unspecified | compliant | After the `v0.4` line was reopened for GPU completion, several live user-facing docs still reflected the earlier CPU/Embree-only shape or used wording that was unnecessarily narrow or inconsistent. |
| 226 | unspecified | compliant | After the reopened GPU `v0.4` line became technically closed, a small set of local cleanup changes remained outside the earlier goal commits: |
| 227 | unspecified | compliant | The existing beginner-facing docs were workable, but still too fragmented: |
| 228 | implemented | compliant | Run a heavy Linux benchmark for the reopened `v0.4` nearest-neighbor line that: |
| 229 | implemented | compliant | Fix the shared accelerated `fixed_radius_neighbors` boundary bug exposed by the heavy Linux Goal 228 benchmark, where Embree, OptiX, and Vulkan dropped the same interior neighbors on a large-coordinate Natural Earth case. |
| 230 | implemented | compliant | Create and verify a clean release-prep workspace for `v0.4` so final release goals can proceed without the unrelated local docs reorganization churn present in the primary working checkout. |
| 231 | implemented | compliant | Align the clean worktree's `v0.4` release package with the actual post-Goal-229 state so the release-facing docs no longer describe stale pre-GPU or pre-fix conditions. |
| 232 | implemented | compliant | Run the final clean-worktree pre-release verification package for `v0.4` and preserve the resulting release-decision evidence. |
| 233 | implemented | compliant | Package the final `v0.4` release-decision state in the clean release-prep worktree so the remaining action is explicit: |
| 234 | implemented | compliant | Resolve the specific public-surface issues identified by the external fresh-clone user-experience audit so the release-prep package is no longer misleading for first-time users. |
| 236 | implemented | compliant | Freeze the correct final decision boundary for `v0.4.0` and explicitly define what belongs to `v0.5`. |
| 238 | implemented | compliant | Run a final consistency-first release audit using the exact priority order that matters to users: |
| 239 | implemented | compliant | Fix the last release-adjacent public-surface consistency issues exposed by the final review set before the final release decision. |
| 240 | implemented | compliant | Prepare the final closure step for the `v0.4.0` release gate so that, once the last narrow public-surface review returns clean, the branch can move directly to the user-authorized release action. |
| 241 | implemented | compliant | Build a durable file-level audit system for the full RTDL repository so that every code and documentation file can be reviewed, tracked, and updated over time instead of handled through scattered one-off reports. |
| 242 | implemented | compliant | Record the first real file-level audit pass in the system audit database using the highest-priority user-facing surfaces: |
| 243 | unspecified | compliant | Record the next system-audit pass for the public documentation tier after the front page and tutorials. |
| 244 | unspecified | compliant | Record the next system-audit pass for the examples tier after the front page, tutorial, and public docs tiers. |
| 245 | unspecified | compliant | Record the next system-audit pass for the public code-facing surface after the front page, tutorials, docs, and examples tiers. |
| 246 | unspecified | compliant | Record the first seeded tier-6 pass for the release-critical verification surface. |
| 247 | unspecified | compliant | Seed the archive/report/history tier with a bounded representative audit pass instead of trying to flatten the entire long-tail archive at once. |
| 248 | unspecified | compliant | Reduce the existing system-audit follow-up set by fixing low-risk documentation problems and reclassifying intentional design choices that were previously tracked too aggressively as follow-up items. |
| 249 | unspecified | compliant | Close the remaining system-audit follow-ups on the public CPU/oracle runtime surface by making native-oracle failures more actionable and re-checking the released workspace behavior directly. |
| 250 | unspecified | compliant | Expand tier-3 audit coverage through the public feature reference pages and the example entrypoints they directly rely on. |
| 251 | unspecified | compliant | Expand tier-3 audit coverage through the architecture, audit-flow, release-handoff, and process-summary documents that remain easy to discover after the front-door and feature layers. |
| 252 | unspecified | compliant | Expand tier-3 audit coverage through the archive entrypoints and the early v0.1/v0.2 goal-definition documents without flattening historical planning into fake current-state docs. |
| 253 | unspecified | compliant | Audit all RTDL goals from the start of the `v0.3` line forward and check whether each goal meets the current project review rule from `refresh.md`: |
