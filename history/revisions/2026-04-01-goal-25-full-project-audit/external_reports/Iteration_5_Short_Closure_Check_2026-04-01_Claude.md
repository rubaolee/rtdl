**F1 — Resolved.** `publish_docs` now defaults to `False`, the smoke path no longer touches docs, Makefile adds an exact `eval-section-5-6-publish-2026-03-31` reproduction target, the checked-in report now includes the reproduction command, explicitly says Figure 14 was not executed, and the misleading pip text is removed.

**F2 — Resolved.** README now says "close to the current native wrapper baseline" and explicitly states the native baseline uses the same compiled Embree shared library with the gap attributed to Python/ctypes host-path overhead.

**F3 — Resolved.** Goal 18 report removes the invalid raw/prepared gap-vs-native lower-bound percentages and replaces them with a note that the Goal 15 native lower-bound is historical context only and not directly comparable.

**F4 — Resolved.** README low-overhead section now carries an explicit `native_loop` caveat for `segment_polygon_hitcount` and `point_nearest_segment`.

**F5 — Resolved.** Duplicate `docs/vision.md` entry removed from README.

**F6 — Resolved.** "complete and published" changed to "complete and checked in to this repository."

**F7 — Resolved.** Goal 15 report now uses repo-relative artifact names instead of machine-specific absolute paths.

**F8 — Resolved.** Default probe-series matches smoke constants, smoke report carries explicit smoke-note text, and `publish_docs=False` by default prevents smoke artifacts from landing in docs.

Approved
