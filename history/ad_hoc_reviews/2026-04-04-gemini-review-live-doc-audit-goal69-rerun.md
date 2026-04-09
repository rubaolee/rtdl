Gemini 3.1 Pro rerun was attempted after local doc fixes, but the model quota was exhausted before a verdict was returned.

Observed error:
- TerminalQuotaError / QUOTA_EXHAUSTED
- reset after approximately 2h40m at the time of the request

Fallback required:
- rerun the live-doc confirmation with `gemini-3-flash-preview`
