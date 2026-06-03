# Future Version To-Do List

This file catches design ideas that should not interrupt the current release or internal-preview lane.

## Generic Adapter Naming

- Consider introducing a generic alias for the Hausdorff adapter shape now named `directed_hausdorff_2d_partner_columns`.
- Candidate generic concept: `directed_max_of_nearest_distance_2d` or `max_distance_nearest_candidate_2d`.
- Rationale: the current native/runtime layers remain app-agnostic, but the adapter name carries algorithm vocabulary. A generic primary name plus `hausdorff` as a discovery alias would improve reuse and align with the primitive discovery duplicate gate.
- Boundary: do not rename the public benchmark app casually; preserve user compatibility and only add aliases/migration helpers when this becomes a real versioned goal.
