# Call For Review - Goal5059 Legacy Public Export Boundary Amendment

Date: 2026-07-06

Please review:

```text
history/internal_docs/goal5059_v2_14_4_legacy_public_export_boundary_amendment_2026-07-06.md
```

Related amended reports:

```text
history/internal_docs/goal5050_v2_14_4_public_private_boundary_audit_2026-07-06.md
history/internal_docs/goal5051_v2_14_4_api_consolidation_closeout_packet_2026-07-06.md
scripts/goal5053_v2144_release_preflight.py
tests/goal5059_v2144_legacy_public_export_boundary_test.py
```

## Requested Review Questions

1. Does Goal5059 correctly fix the overclaim that RayJoin-named Python helpers
   were not public API names, given that several remain in `rtdsl.__all__`?
2. Is the classification `legacy public exports / compatibility debt; not new
   v2.14.4 public generic API` accurate?
3. Is it acceptable to retain those exports for compatibility in v2.14.4 rather
   than remove them immediately?
4. Does the new preflight check `legacy_rayjoin_public_exports_disclosed`
   prevent future reports from hiding or denying these compatibility exports?
5. Does the amendment preserve the core principle that RTDL is the generic
   system and RayJoin is an app, without pretending all legacy exports are
   already clean?
6. Should public release remain blocked until external review debt, including
   Goal5059, is retired?

## Requested Verdict Label

```text
approve_goal5059_legacy_public_export_boundary_amendment
```

or

```text
revise_goal5059_before_v2_14_4_release_boundary
```
