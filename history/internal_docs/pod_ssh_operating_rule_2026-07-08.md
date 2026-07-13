# POD SSH Operating Rule

## Rule

Do not use naked POD SSH commands.

Use the project POD wrapper:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> preflight
py scripts/current_pod_ssh.py --host <host> --port <port> exec "<remote command>"
```

The wrapper always uses:

```text
~/.ssh/id_ed25519_rtdl_codex_current_pod
IdentitiesOnly=yes
BatchMode=yes
StrictHostKeyChecking=no
```

## Why

The current Goal5144 POD was reachable. The failure was local credential
selection: a default or old key was tried before the current project POD key.

The corrected command class is:

```text
ssh -i ~/.ssh/id_ed25519_rtdl_codex_current_pod \
  -o IdentitiesOnly=yes \
  -o BatchMode=yes \
  -o StrictHostKeyChecking=no \
  root@<host> -p <port> "<command>"
```

## Preflight Required Before Blaming POD

Before classifying a POD as down, blocked, or unauthenticated, run:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> preflight
```

Only if this wrapper fails may the failure be recorded as POD/auth/network
blocked. Otherwise the problem is local command construction.

## Current Verified Example

```text
py scripts/current_pod_ssh.py --host 213.173.108.24 --port 13502 preflight
```

Expected evidence shape:

```text
POD_OK
<hostname>
<gpu name>, <driver version>
```
