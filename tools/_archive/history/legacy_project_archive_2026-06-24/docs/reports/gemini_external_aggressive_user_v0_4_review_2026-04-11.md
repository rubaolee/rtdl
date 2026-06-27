# Aggressive External User Review: RTDL v0.4

## Verdict
**PROVISIONAL BLOCK.**

While the core functionality of RTDL v0.4 is technically impressive, the release-wrap is currently "maintainer-hostile" to outsiders. The documentation contains multiple instances of broken internal paths, leaks private environment details (internal IPs), and uses a "Goal-based" nomenclature that is completely opaque to a public user. Until the repository is scrubbed of its "internal research lab" artifacts and the Programming Guide is synchronized with the v0.4 feature set, this is not ready for a public audience.

---

## What Worked
- **First 15 Minutes**: The `rtdl_hello_world.py` and `rtdl_fixed_radius_neighbors.py` scripts ran immediately after a standard `pip install -r requirements.txt`.
- **Cross-Platform Readiness**: The inclusion of `cmd.exe` and PowerShell environment blocks in the `README` is the best part of the onboarding experience.
- **Honesty**: The "What RTDL Does Not Claim" sections are refreshing and set correct expectations.

---

## Breakpoints
- **Missing Referenced Artifacts**: `docs/current_milestone_qa.md` (Line 31) directs the user to `build/windows_goal168_import/...`. **This directory does not exist in the repository.** A user following the "Preserved Source" links hits a 404/Not Found immediately.
- **Terminology Fog**: The documentation is obsessed with "Goal IDs" (Goal 229, Goal 187, etc.). A public user has no access to the internal tracking system where these goals originated. Highlighting "Goal 229" as a headline feature in the `Release Statement` is an immediate "Maintainer Leak."

---

## Broken Or Misleading Claims
- **v0.4 Feature Omission**: The `Programming Guide` (the primary "How to write code" doc) **fails to list the v0.4 predicates** (`fixed_radius_neighbors`, `knn_rows`) in its "Predicate families" list. A user trying to learn how to write a nearest-neighbor kernel will conclude it isn't supported yet.
- **The "Vulkan Scare"**: The documentation for Vulkan is so discouraging ("Use only when...", "Provisional", "Not validated") that it feels like a legacy feature instead of a v0.4 release target.

---

## Cross-Platform Problems
- **Absolute Path Leaks**: `docs/reports/` are full of links to `[MAINTAINER_HOME]/...`. While queste are "archived," they are linked directly from the `Docs Index` and `Release Statement`. This makes the "Public Repo" feel like a personal computer backup.

---

## Programming Experience
- **Authoring Challenge (Fail)**: Attempting to write a `fixed_radius_neighbors` kernel based on the `Programming Guide` alone is impossible because the predicate is missing from the guide's reference list.
- **Internal IP Leak**: `docs/rtdl/programming_guide.md` points to an internal IP `[VALIDATION_HOST]` for "Trusted PTX generation." This is useless to anyone outside the maintainer's local network.

---

## Aggressive User Attacks And Outcomes
- **The "Skip Prereqs" User**: Runs `examples/internal/rtdl_v0_4_nearest_neighbor_scaling_note.py` after a standard install.
  - **Outcome**: The script depends on `scipy` for full functionality, but `scipy` is missing from `requirements.txt`. The docs say `numpy` is recommended, but forget `scipy` which is used in the v0.4 comparison paths.
- **The "Implicit Path" User**: Clones to a folder named `my-rtdl-test`.
  - **Outcome**: `PYTHONPATH=src:.` works, but scripts like `rtdl_v0_4_nearest_neighbor_scaling_note.py` that rely on parent-directory resolution via `sys.path.insert(0, str(ROOT))` are fragile if the user moves files around as encouraged by the "Programming Guide."

---

## Release Risks
- **Identity Crisis**: The repo doesn't know if it's a "Research Handoff" or a "Public Library." It currently looks like a handoff that accidentally went public.
- **Documentation Drift**: The discrepancy between the `DSL Reference` (which has v0.4) and the `Programming Guide` (which doesn't) will lead to user frustration.

---

## Final Recommendation
**BLOCK.**

**Required Scrub Checklist before v0.4.0-final:**
1.  **Sync the Programming Guide**: Add `fixed_radius_neighbors` and `knn_rows` to the predicate list.
2.  **Clean the IPs**: Remove `[VALIDATION_HOST]` and any other internal network references.
3.  **Fix/Remove Broken "Build" Links**: Either include the "Goal 168" artifacts or remove the dead links from the Q\&A.
4.  **De-emphasize internal naming**: Move "Goal ID" references to a "Historical/Appendix" section; they shouldn't be in the `Release Statement`.
5.  **Audit absolute paths**: Ensure all paths in `reports/` are relative or at least acknowledge they are host-specific.
