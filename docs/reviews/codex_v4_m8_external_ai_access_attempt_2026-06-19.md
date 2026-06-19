# RTDL V4.0 M8 External AI Access Attempt

Date: 2026-06-19

Status: external Claude/Gemini review attempted, not completed.

## Verdict

The V4.0 M8 packet remains ready for external critical review, but the external
AI review gate is still open. This file is not a Claude or Gemini review. It is
an access/provenance report explaining why the required external review could
not be completed from the current Codex environment.

Per `docs/handoff/REFRESH_LOCAL_2026-04-13.md`, RTDL's release discipline
requires Codex plus at least one external AI, Claude or Gemini, for `2-AI`
consensus. Internal Codex subagents do not satisfy that external-AI side.

## Review Target

- Request: `docs/reviews/codex_v4_m8_external_review_request_2026-06-19.md`
- Packet: `docs/engineering/rtdl_v4_0_m8_release_candidate_packet_2026-06-19.md`
- Blocker manifest:
  `docs/engineering/rtdl_v4_0_release_candidate_blockers_2026-06-19.json`

## Attempted External Paths

1. Claude/Gemini connector discovery

   - `tool_search` for Claude/Gemini external review tools returned no matching
     callable tools.
   - `list_available_plugins_to_install` returned no Claude or Gemini plugin or
     connector.

2. Gemini CLI on Windows/WSL

   - `gemini` exists at `C:\Users\Lestat\AppData\Roaming\npm\gemini.ps1`.
   - A headless review attempt failed before model output with
     `IneligibleTierError: This client is no longer supported for Gemini Code
     Assist for individuals`.
   - WSL resolves to the same Windows Gemini CLI path, so it inherits the same
     authentication/client limitation.

3. Claude Code CLI through npm

   - `npx -y @anthropic-ai/claude-code --version` returned
     `2.1.183 (Claude Code)`.
   - A read-only `--print --permission-mode plan` review attempt failed with
     `401 Invalid authentication credentials`.

4. Browser sessions

   - Chrome automation opened `https://claude.ai/new`; the page redirected to
     Claude login/logout flow, so no logged-in Claude web review was available.
   - Chrome automation opened `https://gemini.google.com/app`; the page showed
     a `Sign in` state, so no logged-in Gemini web review was available.

5. Claude desktop application

   - Windows shows the Claude desktop application running.
   - The Codex Computer Use plugin could not initialize for app control:
     `Package subpath './dist/project/cua/sky_js/src/targets/windows/internal/computer_use_client_base.js' is not defined by "exports"`.
   - Because the Computer Use skill forbids falling back to ad hoc PowerShell UI
     automation after plugin failure, no desktop-app message was sent.

6. Antigravity local agent API

   - Antigravity is installed and `agentapi.bat` exists.
   - A headless Antigravity language server was started locally and `agentapi`
     reached it.
   - `agentapi new-conversation` failed before model output with
     `failed to fetch available models` and `use of closed network connection`,
     including after restarting the server with `-model_api_client_type=gemini`.

7. Other machines

   - `192.168.1.20` is reachable, but `claude` and `gemini` were not available
     on the default PATH.
   - `rtdl-mac` at `192.168.1.15` timed out on SSH.

## Release Consequence

`external_release_candidate_review` remains open. `release_candidate_ready`
must remain `false`; the final release-candidate commit remains unassigned.

No V4.0 front-door switch, release approval, package/stable-SDK wording,
true-zero-copy wording, async wording, public speedup wording, RT-core speedup
wording, or broad PyTorch/Numba/DLPack wording is authorized by this report.

## Next Required Action

Run the existing external review request through an authenticated Claude or
Gemini channel and save the actual external review output under `docs/reviews/`.
Only then should the V4.0 M8 blocker manifest be updated from access-blocked to
externally reviewed.
