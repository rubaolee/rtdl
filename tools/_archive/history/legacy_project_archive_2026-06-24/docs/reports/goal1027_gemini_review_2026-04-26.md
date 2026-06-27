I will start by reading the requested files to evaluate the Goal1027 repair against the specified criteria.
ACCEPT

The Goal1027 repair correctly synchronizes the public release hygiene state with the v0.9.6 history advanced by Goal1023.

- **Stale Expectations:** `tests/goal648_public_release_hygiene_test.py` was updated to recognize `v0.9.6` (Goal1023) as the current boundary.
- **Historical Preservation:** The test explicitly verifies that `v0.9.5` release rows (Goals 645–648) remain in the history and dashboard indexes.
- **Boundary Link:** `docs/release_reports/v0_9/support_matrix.md` now correctly points to the `v0_9_6` support matrix for the current boundary.
- **No Claims:** The repair is strictly limited to metadata and link maintenance; it does not authorize new speedup claims, cloud actions, or tags.

## stderr

```
Keychain initialization encountered an error: Cannot find module '../build/Release/keytar.node'
Require stack:
- /opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/node_modules/keytar/lib/keytar.js
Using FileKeychain fallback for secure storage.
Loaded cached credentials.
```
