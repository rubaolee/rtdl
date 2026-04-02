# Goal 29 LSI Mismatch Diagnosis

Goal 29 diagnoses and, if possible within one round, fixes the larger-slice `lsi` mismatch observed on the Linux exact-source `County ⊲⊳ Zipcode` runs.

Scope:
- reproduce the mismatch on a frozen larger-slice case
- compare `rt.run_cpu(...)` and `rt.run_embree(...)` outputs at the pair level
- identify whether the divergence is caused by reference semantics, backend semantics, or exact-source conversion assumptions
- implement a fix only if the root cause is demonstrated clearly
- otherwise close with an honest diagnosis report and next-step blocker note

Closure conditions:
- Claude reviews the plan and final diagnosis/fix
- Gemini monitors the whole round
- the round ends with either:
  - a parity fix plus passing regression, or
  - an explicit root-cause diagnosis with bounded unresolved status
