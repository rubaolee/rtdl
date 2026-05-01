# Verdict

The bounded dataset manifest layer proposed in Goal 268 is well-designed, technically honest, and successfully fulfills its scope. It establishes a clear framework for defining dataset subsets for local reproduction while strictly avoiding any false claims about dataset availability or acquisition status.

# Findings

*   **Technical Honesty:** The manifest layer maintains a high level of honesty. It explicitly tags the `current_status` of the bounded manifests as `"planned"` and the dataset families as `"source-identified"`. It openly distinguishes between `preferred_provenance` (exact-input) and acceptable local bounds.
*   **Deterministic Bounded Rules:** Each of the three RTNN dataset families (KITTI, Stanford, N-body) is assigned a concrete, explicit `bounded_rule`. These rules focus on freezing lists (frame lists, scan lists, snapshot IDs) and applying stable truncation, sampling, or extraction orders, guaranteeing deterministic bounds.
*   **JSON Manifest Writer Coherence:** The `write_rtnn_bounded_dataset_manifest` function is highly coherent. It successfully integrates the dataset family definition, the local experiment profile, and the bounded manifest into a single versioned JSON payload (`"rtnn_bounded_dataset_manifest_v1"`). It utilizes `dataclass.asdict` effectively and correctly ensures parent directories exist before writing formatted JSON. The unit tests validate this shape perfectly.
*   **Avoidance of Overclaiming:** The implementation completely aligns with the stated non-goals. By marking the artifacts as `"planned"`, outlining the future `acquisition_plan` (e.g., "Add a deterministic acquisition manifest..."), and refraining from including any mock file paths or download logic, it avoids making any premature claims that the datasets are currently downloaded or residing on disk.

# Risks

*   **Enforcement of Deterministic Rules:** While the `bounded_rule` strings describe deterministic processes (e.g., "stable frame-order truncation rule"), they are currently just textual descriptions. The primary risk lies in the future implementation phase; the actual downstream acquisition/truncation scripts must rigorously adhere to these textual contracts to maintain the promised determinism.
*   **Profile Mapping Vulnerability:** The manifest writer looks up the local profile by matching `manifest.bounded_profile_id` to `profile.profile_id`. If the definitions in `rtnn_reproduction.py` and `rtnn_manifests.py` drift apart (e.g., a typo in an ID), the writer will fail with a `KeyError`. While currently aligned, it's a structural coupling across files.

# Conclusion

The Goal 268 slice is a solid, responsible addition to the codebase. It creates the necessary scaffolding for local performance parity runs without falling into the trap of over-representing the current state of dataset acquisition. The code is clean, the tests are focused, and the architectural separation between exact reproduction targets and local bounded variants is cleanly maintained.
