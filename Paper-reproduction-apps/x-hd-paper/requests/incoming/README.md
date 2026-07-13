# X-HD External Response Intake

Status: `empty_waiting_for_external_response`

When the owner receives an author, ACM-access, or external-review response,
save a normalized JSON copy here using:

```text
../external_response_intake_template.json
```

Do not paste private messages into public docs unless the sender has allowed
that. If a response contains private material, store only the minimum metadata
needed for the project state and keep raw private material outside the repo.

Allowed response categories:

```text
author_hash_manifest
author_input_archive
byte_identical_regeneration_script
acm_supplement_artifact_instructions
exact_equivalence_verdict
explicit_non_availability_statement
other
```

Fail-closed rule:

```text
No response may upgrade X-HD to exact paper reproduction, Figure 5
reproduction, full paper reproduction, or author-vs-RTDL performance parity
until a separate provenance ingestion goal validates it and a review accepts the
new boundary.
```
