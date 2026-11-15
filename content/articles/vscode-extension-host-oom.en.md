## A process that kept restarting

During a remote development session, the VS Code extension host repeatedly exited and the client reconnected. The [original September 2026 post](https://blog.csdn.net/ruiqideng/article/details/166041161) records a case investigation, not a general diagnosis for all remote-session failures. Some contemporaneous values in that account could not be reproduced later, and the original machine and logs were not re-examined for this revision.

The strongest evidence was an extension-host log showing `FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory`, followed by exit with `SIGABRT`. In that incident the immediate failure was a V8 heap limit reached by the extension-host process. This does not, by itself, identify which extension or retained object caused heap growth.

## Separate the symptom from the process failure

The original record describes missing extension commands after reconnect, but a missing command has several possible causes, including activation or registration failures. Correlate it with process lifetime and logs rather than treating it as proof of a restart. The log excerpt reports garbage collection near the limit followed by the V8 fatal error and the extension host exiting with `SIGABRT`.

A useful first pass is to inspect the current remote session's `remoteagent.log` and relevant `exthost.log`, correlate timestamps, and distinguish a V8 fatal allocation failure from an OS or cgroup OOM kill. A signal alone is not a unique diagnosis. Avoid recursively searching an entire log tree without checking matches: the original post records a search command appearing in logs and contaminating its own count.

```bash
# Substitute paths from the actual remote session.
grep -hE 'Reached heap limit|OOMErrorHandler|SIGABRT|SIGKILL' \
  /path/to/remoteagent.log | tail -20
```

The recorded memory limits changed between observations. That discrepancy should remain visible; the original post's conclusion was based on the V8 error and process exit, not on a single assumed container limit.

## Test the configuration path

In the recorded installation, one attempted environment setup hook did not appear to run, and restarting a window did not necessarily restart the remote server process. The investigation then examined the server's startup and child-process code for that particular installation. It reported that `NODE_OPTIONS` was removed from the extension host's environment, while an explicit Node argument was propagated through the observed startup path.

The article specifically reports a list of environment variables stripped before the child was launched, including `NODE_OPTIONS`, and an `execArgv` path that passed arguments to the child. It checked the running process command line after restart. That check establishes propagation for the observed process; it does not by itself explain why objects accumulated.

This is an installation-specific observation, not a promise about all VS Code releases, launch modes, or extensions. A negative string search is evidence about the files searched, not a complete proof that a hook does not exist. Before changing anything, determine the actual executable, version, process tree and command line; prefer a documented supported configuration where available.

## Mitigation, not a leak fix

The original report describes adding `--max-old-space-size=16384` to a local server launcher and checking that the running extension-host command line contained the argument. A later no-argument rerun of its patch script changed the configured value from 16384 to the script default of 8192 on disk; the already-running process retained its previous arguments until restart. The script was revised to report the observed configuration and preserve an existing value when no override was supplied. This is a useful example of why an idempotence check must verify the actual persisted state as well as the running process. Editing installation-managed server files is version-specific and may be overwritten by updates; it can affect other child Node processes too. The original is not a portable installation procedure.

Node documents `--max-old-space-size` as the limit for V8's old memory section, not a cap on total process RSS ([Node.js CLI documentation](https://nodejs.org/download/release/v24.19.0/docs/api/cli.html)). Increasing it can give a workload more headroom, but does not establish that a memory leak is fixed. The original record's approximately 4.19 GB default heap limit was an observation for one Node binary and environment, not a universal constant for every Node or V8 configuration.

## What remains unproven

The source reports correlation between large session payloads and crashes, but no controlled experiment or heap profile isolating the retaining component. Heap growth estimates and extrapolated survival times in the original are not measurements of a fixed rate. A process-level command line proves an argument was passed; it does not alone prove long-term stability or identify the cause of retention.

For a reproducible follow-up, preserve timestamped logs, versions and process identity, reproduce with a controlled workload, compare heap snapshots or allocation profiles, and distinguish mitigation from a fix to the retaining component. Record cgroup limits and memory use at the time of each run. This English note retains the observed failure pattern while limiting claims to what the original record supports.
