Keychain initialization encountered an error: Cannot find module '../build/Release/keytar.node'
Require stack:
- /opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/node_modules/keytar/lib/keytar.js
Using FileKeychain fallback for secure storage.
Loaded cached credentials.
I will start by locating the review packet and the cited evidence files to understand the proposed wording and the supporting data.
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
    at Gaxios._request (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:6570:19)
    at process.processTicksAndRejections (node:internal/process/task_queues:104:5)
    at async _OAuth2Client.requestAsync (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:8533:16)
    at async CodeAssistServer.requestStreamingPost (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:275986:17)
    at async CodeAssistServer.generateContentStream (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:275786:23)
    at async file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:276624:19
    at async file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:253666:23
    at async retryWithBackoff (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:273586:23)
    at async GeminiChat.makeApiCallAndProcessStream (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:308672:28)
    at async GeminiChat.streamWithRetries (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:308515:29) {
  config: {
    url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
    method: 'POST',
    params: { alt: 'sse' },
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'GeminiCLI/0.36.0/gemini-3.1-pro-preview (darwin; arm64; terminal) google-api-nodejs-client/9.15.1',
      Authorization: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      'x-goog-api-client': 'gl-node/25.8.2'
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
      date: 'Wed, 06 May 2026 12:27:03 GMT',
      server: 'ESF',
      'server-timing': 'gfet4t7; dur=7268',
      vary: 'Origin, X-Origin, Referer',
      'x-cloudaicompanion-trace-id': '9b0386a165463409',
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
    at Gaxios._request (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:6570:19)
    at process.processTicksAndRejections (node:internal/process/task_queues:104:5)
    at async _OAuth2Client.requestAsync (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:8533:16)
    at async CodeAssistServer.requestStreamingPost (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:275986:17)
    at async CodeAssistServer.generateContentStream (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:275786:23)
    at async file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:276624:19
    at async file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:253666:23
    at async retryWithBackoff (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:273586:23)
    at async GeminiChat.makeApiCallAndProcessStream (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:308672:28)
    at async GeminiChat.streamWithRetries (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:308515:29) {
  config: {
    url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
    method: 'POST',
    params: { alt: 'sse' },
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'GeminiCLI/0.36.0/gemini-3.1-pro-preview (darwin; arm64; terminal) google-api-nodejs-client/9.15.1',
      Authorization: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      'x-goog-api-client': 'gl-node/25.8.2'
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
      date: 'Wed, 06 May 2026 12:27:13 GMT',
      server: 'ESF',
      'server-timing': 'gfet4t7; dur=6676',
      vary: 'Origin, X-Origin, Referer',
      'x-cloudaicompanion-trace-id': '57fe416d2eb09e1c',
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
Attempt 3 failed with status 429. Retrying with backoff... _GaxiosError: [{
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
    at Gaxios._request (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:6570:19)
    at process.processTicksAndRejections (node:internal/process/task_queues:104:5)
    at async _OAuth2Client.requestAsync (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:8533:16)
    at async CodeAssistServer.requestStreamingPost (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:275986:17)
    at async CodeAssistServer.generateContentStream (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:275786:23)
    at async file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:276624:19
    at async file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:253666:23
    at async retryWithBackoff (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:273586:23)
    at async GeminiChat.makeApiCallAndProcessStream (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:308672:28)
    at async GeminiChat.streamWithRetries (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:308515:29) {
  config: {
    url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
    method: 'POST',
    params: { alt: 'sse' },
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'GeminiCLI/0.36.0/gemini-3.1-pro-preview (darwin; arm64; terminal) google-api-nodejs-client/9.15.1',
      Authorization: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      'x-goog-api-client': 'gl-node/25.8.2'
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
      date: 'Wed, 06 May 2026 12:27:27 GMT',
      server: 'ESF',
      'server-timing': 'gfet4t7; dur=6216',
      vary: 'Origin, X-Origin, Referer',
      'x-cloudaicompanion-trace-id': '33411adb84a661e4',
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
Attempt 4 failed with status 429. Retrying with backoff... _GaxiosError: [{
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
    at Gaxios._request (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:6570:19)
    at process.processTicksAndRejections (node:internal/process/task_queues:104:5)
    at async _OAuth2Client.requestAsync (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:8533:16)
    at async CodeAssistServer.requestStreamingPost (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:275986:17)
    at async CodeAssistServer.generateContentStream (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:275786:23)
    at async file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:276624:19
    at async file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:253666:23
    at async retryWithBackoff (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:273586:23)
    at async GeminiChat.makeApiCallAndProcessStream (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:308672:28)
    at async GeminiChat.streamWithRetries (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:308515:29) {
  config: {
    url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
    method: 'POST',
    params: { alt: 'sse' },
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'GeminiCLI/0.36.0/gemini-3.1-pro-preview (darwin; arm64; terminal) google-api-nodejs-client/9.15.1',
      Authorization: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      'x-goog-api-client': 'gl-node/25.8.2'
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
      date: 'Wed, 06 May 2026 12:27:51 GMT',
      server: 'ESF',
      'server-timing': 'gfet4t7; dur=7311',
      vary: 'Origin, X-Origin, Referer',
      'x-cloudaicompanion-trace-id': '3ba1df428f831cd1',
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
Attempt 5 failed with status 429. Retrying with backoff... _GaxiosError: [{
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
    at Gaxios._request (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:6570:19)
    at process.processTicksAndRejections (node:internal/process/task_queues:104:5)
    at async _OAuth2Client.requestAsync (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:8533:16)
    at async CodeAssistServer.requestStreamingPost (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:275986:17)
    at async CodeAssistServer.generateContentStream (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:275786:23)
    at async file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:276624:19
    at async file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:253666:23
    at async retryWithBackoff (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:273586:23)
    at async GeminiChat.makeApiCallAndProcessStream (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:308672:28)
    at async GeminiChat.streamWithRetries (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:308515:29) {
  config: {
    url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
    method: 'POST',
    params: { alt: 'sse' },
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'GeminiCLI/0.36.0/gemini-3.1-pro-preview (darwin; arm64; terminal) google-api-nodejs-client/9.15.1',
      Authorization: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      'x-goog-api-client': 'gl-node/25.8.2'
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
      date: 'Wed, 06 May 2026 12:28:32 GMT',
      server: 'ESF',
      'server-timing': 'gfet4t7; dur=7127',
      vary: 'Origin, X-Origin, Referer',
      'x-cloudaicompanion-trace-id': '3ad86f69f81d8129',
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
Attempt 6 failed with status 429. Retrying with backoff... _GaxiosError: [{
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
    at Gaxios._request (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:6570:19)
    at process.processTicksAndRejections (node:internal/process/task_queues:104:5)
    at async _OAuth2Client.requestAsync (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:8533:16)
    at async CodeAssistServer.requestStreamingPost (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:275986:17)
    at async CodeAssistServer.generateContentStream (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:275786:23)
    at async file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:276624:19
    at async file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:253666:23
    at async retryWithBackoff (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:273586:23)
    at async GeminiChat.makeApiCallAndProcessStream (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:308672:28)
    at async GeminiChat.streamWithRetries (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:308515:29) {
  config: {
    url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
    method: 'POST',
    params: { alt: 'sse' },
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'GeminiCLI/0.36.0/gemini-3.1-pro-preview (darwin; arm64; terminal) google-api-nodejs-client/9.15.1',
      Authorization: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      'x-goog-api-client': 'gl-node/25.8.2'
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
      date: 'Wed, 06 May 2026 12:29:00 GMT',
      server: 'ESF',
      'server-timing': 'gfet4t7; dur=6543',
      vary: 'Origin, X-Origin, Referer',
      'x-cloudaicompanion-trace-id': '37c7d5504296fac6',
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
Attempt 7 failed with status 429. Retrying with backoff... _GaxiosError: [{
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
    at Gaxios._request (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:6570:19)
    at process.processTicksAndRejections (node:internal/process/task_queues:104:5)
    at async _OAuth2Client.requestAsync (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:8533:16)
    at async CodeAssistServer.requestStreamingPost (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:275986:17)
    at async CodeAssistServer.generateContentStream (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:275786:23)
    at async file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:276624:19
    at async file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:253666:23
    at async retryWithBackoff (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:273586:23)
    at async GeminiChat.makeApiCallAndProcessStream (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:308672:28)
    at async GeminiChat.streamWithRetries (file:///opt/homebrew/Cellar/gemini-cli/0.36.0/libexec/lib/node_modules/@google/gemini-cli/bundle/chunk-QVTX2M5J.js:308515:29) {
  config: {
    url: 'https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse',
    method: 'POST',
    params: { alt: 'sse' },
    headers: {
      'Content-Type': 'application/json',
      'User-Agent': 'GeminiCLI/0.36.0/gemini-3.1-pro-preview (darwin; arm64; terminal) google-api-nodejs-client/9.15.1',
      Authorization: '<<REDACTED> - See `errorRedactor` option in `gaxios` for configuration>.',
      'x-goog-api-client': 'gl-node/25.8.2'
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
      date: 'Wed, 06 May 2026 12:29:32 GMT',
      server: 'ESF',
      'server-timing': 'gfet4t7; dur=7174',
      vary: 'Origin, X-Origin, Referer',
      'x-cloudaicompanion-trace-id': '55d0b4522629eac7',
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


[gemini_timeout=240s]
