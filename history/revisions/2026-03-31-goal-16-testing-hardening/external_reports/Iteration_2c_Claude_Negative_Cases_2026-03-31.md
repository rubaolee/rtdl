1. **Invalid/corrupt input mesh** — pass a degenerate or malformed geometry file; verify graceful error, no crash or silent wrong output.
2. **Out-of-range numeric parameters** — supply negative ray counts, zero-area triangles, or NaN/Inf values; confirm validation rejects or clamps with a clear message.
3. **Missing required CLI arguments** — invoke the CLI without mandatory flags; assert non-zero exit code and actionable error text, not a Python traceback.
4. **Resource exhaustion / large scene** — request a scene or buffer far exceeding available memory; confirm the runtime fails fast with a meaningful error rather than hanging or silently truncating results.

negative-cases done.
