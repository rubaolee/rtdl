Warning: Basic terminal detected (TERM=dumb). Visual rendering will be limited. For the best experience, use a terminal emulator with truecolor support.
Warning: 256-color support not detected. Using a terminal with at least 256-color support is recommended for a better visual experience.
Ripgrep is not available. Falling back to GrepTool.
Attempt 1 failed with status 429. Retrying with backoff... _GaxiosError: [{
  "error": {
    "code": 429,
    "message": "No capacity available for model gemini-3-flash-preview on the server",
    "errors": [
      {
        "message": "No capacity available for model gemini-3-flash-preview on the server",
        "domain": "global",
        "reason": "rateLimitExceeded"
      }
    ],
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "MODEL_CAPACITY_EXHAUSTED",
        "domain": "cloudcode-pa.googleapis.com",
        "metadata": {
          "model": "gemini-3-flash-preview"
        }
      }
    ]
  }
}
]
    at Gaxios._request (file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:8805:19)
    at process.processTicksAndRejections (node:internal/process/task_queues:104:5)
    at async _OAuth2Client.requestAsync (file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:10768:16)
    at async CodeAssistServer.requestStreamingPost (file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:272609:17)
    at async CodeAssistServer.generateContentStream (file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:272409:23)
    at async file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:273256:19
    at async file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:250163:23
    at async retryWithBackoff (file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:270357:23)
    at async GeminiChat.makeApiCallAndProcessStream (file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:292973:28)
    at async GeminiChat.streamWithRetries (file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:292811:29) {
  config: {
    url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
    method: 'POST',
    params: { alt: 'sse' },
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'GeminiCLI/0.40.1/gemini-3.1-pro-preview (darwin; arm64; terminal) google-api-nodejs-client/9.15.1',
      Authorization: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      'x-goog-api-client': 'gl-node/25.9.0'
    },
    responseType: 'stream',
    body: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
    signal: AbortSignal { aborted: false },
    retry: false,
    paramsSerializer: [Function: paramsSerializer],
    validateStatus: [Function: validateStatus],
    errorRedactor: [Function: defaultErrorRedactor]
  },
  response: {
    config: {
      url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
      method: 'POST',
      params: [Object],
      headers: [Object],
      responseType: 'stream',
      body: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      signal: [AbortSignal],
      retry: false,
      paramsSerializer: [Function: paramsSerializer],
      validateStatus: [Function: validateStatus],
      errorRedactor: [Function: defaultErrorRedactor]
    },
    data: '[{\n' +
      '  "error": {\n' +
      '    "code": 429,\n' +
      '    "message": "No capacity available for model gemini-3-flash-preview on the server",\n' +
      '    "errors": [\n' +
      '      {\n' +
      '        "message": "No capacity available for model gemini-3-flash-preview on the server",\n' +
      '        "domain": "global",\n' +
      '        "reason": "rateLimitExceeded"\n' +
      '      }\n' +
      '    ],\n' +
      '    "status": "RESOURCE_EXHAUSTED",\n' +
      '    "details": [\n' +
      '      {\n' +
      '        "@type": "type.googleapis.com/google.rpc.ErrorInfo",\n' +
      '        "reason": "MODEL_CAPACITY_EXHAUSTED",\n' +
      '        "domain": "cloudcode-pa.googleapis.com",\n' +
      '        "metadata": {\n' +
      '          "model": "gemini-3-flash-preview"\n' +
      '        }\n' +
      '      }\n' +
      '    ]\n' +
      '  }\n' +
      '}\n' +
      ']',
    headers: {
      'alt-svc': 'h3=":443"; ma=2592000,h3-29=":443"; ma=2592000',
      'content-length': '630',
      'content-type': 'application/json; charset=UTF-8',
      date: 'Mon, 25 May 2026 19:08:29 GMT',
      server: 'ESF',
      'server-timing': 'gfet4t7; dur=6335',
      vary: 'Origin, X-Origin, Referer',
      'x-cloudaicompanion-trace-id': 'c8725c50c4807de8',
      'x-content-type-options': 'nosniff',
      'x-frame-options': 'SAMEORIGIN',
      'x-xss-protection': '0'
    },
    status: 429,
    statusText: 'Too Many Requests',
    request: {
      responseURL: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse'
    }
  },
  error: undefined,
  status: 429,
  Symbol(gaxios-gaxios-error): '6.7.1'
}
Attempt 2 failed with status 429. Retrying with backoff... _GaxiosError: [{
  "error": {
    "code": 429,
    "message": "No capacity available for model gemini-3-flash-preview on the server",
    "errors": [
      {
        "message": "No capacity available for model gemini-3-flash-preview on the server",
        "domain": "global",
        "reason": "rateLimitExceeded"
      }
    ],
    "status": "RESOURCE_EXHAUSTED",
    "details": [
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "MODEL_CAPACITY_EXHAUSTED",
        "domain": "cloudcode-pa.googleapis.com",
        "metadata": {
          "model": "gemini-3-flash-preview"
        }
      }
    ]
  }
}
]
    at Gaxios._request (file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:8805:19)
    at process.processTicksAndRejections (node:internal/process/task_queues:104:5)
    at async _OAuth2Client.requestAsync (file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:10768:16)
    at async CodeAssistServer.requestStreamingPost (file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:272609:17)
    at async CodeAssistServer.generateContentStream (file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:272409:23)
    at async file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:273256:19
    at async file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:250163:23
    at async retryWithBackoff (file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:270357:23)
    at async GeminiChat.makeApiCallAndProcessStream (file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:292973:28)
    at async GeminiChat.streamWithRetries (file:///opt/homebrew/Cellar/gemini-cli/0.40.1/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-UN6XCVMJ.js:292811:29) {
  config: {
    url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
    method: 'POST',
    params: { alt: 'sse' },
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'GeminiCLI/0.40.1/gemini-3.1-pro-preview (darwin; arm64; terminal) google-api-nodejs-client/9.15.1',
      Authorization: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      'x-goog-api-client': 'gl-node/25.9.0'
    },
    responseType: 'stream',
    body: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
    signal: AbortSignal { aborted: false },
    retry: false,
    paramsSerializer: [Function: paramsSerializer],
    validateStatus: [Function: validateStatus],
    errorRedactor: [Function: defaultErrorRedactor]
  },
  response: {
    config: {
      url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
      method: 'POST',
      params: [Object],
      headers: [Object],
      responseType: 'stream',
      body: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      signal: [AbortSignal],
      retry: false,
      paramsSerializer: [Function: paramsSerializer],
      validateStatus: [Function: validateStatus],
      errorRedactor: [Function: defaultErrorRedactor]
    },
    data: '[{\n' +
      '  "error": {\n' +
      '    "code": 429,\n' +
      '    "message": "No capacity available for model gemini-3-flash-preview on the server",\n' +
      '    "errors": [\n' +
      '      {\n' +
      '        "message": "No capacity available for model gemini-3-flash-preview on the server",\n' +
      '        "domain": "global",\n' +
      '        "reason": "rateLimitExceeded"\n' +
      '      }\n' +
      '    ],\n' +
      '    "status": "RESOURCE_EXHAUSTED",\n' +
      '    "details": [\n' +
      '      {\n' +
      '        "@type": "type.googleapis.com/google.rpc.ErrorInfo",\n' +
      '        "reason": "MODEL_CAPACITY_EXHAUSTED",\n' +
      '        "domain": "cloudcode-pa.googleapis.com",\n' +
      '        "metadata": {\n' +
      '          "model": "gemini-3-flash-preview"\n' +
      '        }\n' +
      '      }\n' +
      '    ]\n' +
      '  }\n' +
      '}\n' +
      ']',
    headers: {
      'alt-svc': 'h3=":443"; ma=2592000,h3-29=":443"; ma=2592000',
      'content-length': '630',
      'content-type': 'application/json; charset=UTF-8',
      date: 'Mon, 25 May 2026 19:08:42 GMT',
      server: 'ESF',
      'server-timing': 'gfet4t7; dur=7361',
      vary: 'Origin, X-Origin, Referer',
      'x-cloudaicompanion-trace-id': '93ef2af2a97135b0',
      'x-content-type-options': 'nosniff',
      'x-frame-options': 'SAMEORIGIN',
      'x-xss-protection': '0'
    },
    status: 429,
    statusText: 'Too Many Requests',
    request: {
      responseURL: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse'
    }
  },
  error: undefined,
  status: 429,
  Symbol(gaxios-gaxios-error): '6.7.1'
}
(node:6084) [DEP0190] DeprecationWarning: Passing args to a child process with shell option true can lead to security vulnerabilities, as the arguments are not escaped, only concatenated.
(Use `node --trace-deprecation ...` to show where the warning was created)
VERDICT: ACCEPT

### Findings
1.  **Documentation Versioning**: All primary public-facing entrypoints (`README.md`, `docs/README.md`, `examples/README.md`, `docs/application_catalog.md`) have been successfully sanitized. They consistently refer to the current **v2.3/v2.x** surface, with no stale references to v0.x, v1.x, or early v2.x development versions (v2.0, v2.1) in learner-facing text.
2.  **Historical Classification**: Extensive historical data, including v0.x-v2.1 audit logs, handoffs, and release reports, has been correctly isolated in dedicated directories (`docs/audit`, `docs/history`, `docs/reports`, `docs/release_reports`). The audit script (`scripts/goal2617_current_surface_audit.py`) successfully classifies these as `historical_audit` or `historical_release_package`, ensuring they are preserved for provenance without interfering with the modern learner path.
3.  **Link Integrity**: The automated audit confirms **zero dead local links** within the `current_public` documentation surface. Link debt is strictly confined to historical/support artifacts, where it is explicitly acknowledged and tolerated as part of the "not rewritten" policy.
4.  **Runnable Surface Smoke**: The smoke test suite (`scripts/goal2617_surface_smoke.py`) verifies **54/54** cases, covering 100% of the public Python entrypoints in `examples/v2_0` and `examples/visual_demo`. This includes tutorials, feature examples, apps, partner continuations, and research benchmarks.
5.  **Validation Rigor**: The test `tests/goal2617_doc_clean_audit_test.py` enforces the audit outcomes, ensuring that any regression in public doc cleanliness or smoke test coverage will trigger a CI failure.

### Residual Risks
- **External Links**: The audit script currently bypasses external URL validation (`http/https`), so stale or dead external references are not monitored.
- **Categorization Drift**: New documentation files must be placed within recognized `CURRENT_DOC_PREFIXES` or added to the audit script's `CURRENT_TOP_LEVEL_DOCS` to remain under automated cleanliness enforcement.

### Required Fixes
- None. Goal2617 documentation cleanup and audit criteria are fully met.
