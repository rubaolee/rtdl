I will begin by confirming the existence of the required files and then read their contents to evaluate the Goal 23 plan against the specified review criteria.
I will now read the specified files to analyze the Goal 23 plan, the reproduction program, and the provenance rules, ensuring I have all the necessary information to evaluate the review criteria.
I will verify the existence and usability of the dataset and provenance machinery by checking `src/rtdsl/datasets.py`, as mentioned in the Goal 22 documentation, to ensure that Goal 23 can proceed with its implementation.
I will now read `src/rtdsl/datasets.py` and `src/rtdsl/rayjoin_artifacts.py` to confirm they correctly implement the fidelity labels and status labels as defined in the Goal 22 deliverables.
The Goal 23 plan for bounded Embree reproduction has been reviewed against the repository's current state and frozen objectives.

### Findings
- **Honest Boundaries**: The plan explicitly distinguishes between executed and reported-only content, utilizing the `exact-input`, `derived-input`, and `synthetic-input` fidelity labels established in Goal 21. The implementation boundary is machine-checkable via the `current_status` (e.g., `source-identified` vs. `acquired`) and `fidelity` metadata already implemented in `src/rtdsl/datasets.py` and `src/rtdsl/rayjoin_artifacts.py`.
- **Provenance Preservation**: The Goal 23 strategy consumes the frozen Goal 21 matrix and Goal 22 generator/reporting machinery without alteration. It strictly adheres to the rule that no artifact may imply full paper coverage for families that are still only "source-identified."
- **Readiness**: The infrastructure for automated generation of partial Table 3 and overlay-seed analogues (Table 4/Figure 15) is already present in `src/rtdsl/rayjoin_artifacts.py`. The local runtime policy (5–10 minutes) is clearly defined and consistent with previous scalability runs.

### Decision
The Goal 23 setup is well-founded, providing a transparent bridge between the current Embree-based local execution and the eventual full-scale NVIDIA reproduction. The clear labeling of missing rows and synthetic analogues ensures the integrity of the reproduction report.

Consensus to begin implementation.

Keychain initialization encountered an error: Cannot find module '../build/Release/keytar.node'
Require stack:
- /opt/homebrew/Cellar/gemini-cli/0.35.3/libexec/lib/node_modules/@google/gemini-cli/node_modules/keytar/lib/keytar.js
Using FileKeychain fallback for secure storage.
Loaded cached credentials.
