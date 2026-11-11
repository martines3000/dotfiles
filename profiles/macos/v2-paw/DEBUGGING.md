# PAW experiments and upstream bug reports

V2 was activated on this Mac on **2026-11-10**, using PAW `0.1.0-beta.1+5249781`. The config matches the saved v2 snapshot. PAW, its Accessibility grant and the bar were checked; yabai/skhd/borders were inactive. This records a starting point, not proof that every keyboard, layout or display path works.

## Last validated PAW build — 2026-11-10

PAW `0.1.0-beta.6+13037f1`, source revision [`13037f1cf79b07a6ae54cc987601c7022b3ed3d2`](https://github.com/pseudobun/paw/commit/13037f1cf79b07a6ae54cc987601c7022b3ed3d2), was built, installed and granted Accessibility on this Mac. It includes three fixes that are now merged upstream:

- [#29 — stale minimum recovery](https://github.com/pseudobun/paw/pull/29): retry a parked window's tile size and recover if it now fits, preserving genuine constraints and newer focus requests.
- [#30 — placeholder hover focus](https://github.com/pseudobun/paw/pull/30): hovering selects a placeholder when focus-follows-mouse is enabled, while its constrained window stays parked.
- [#31 — focus after full-screen/float toggles](https://github.com/pseudobun/paw/pull/31): bring the restored window forward and give it native focus.

All **86 Swift tests** and [CI for the tested head](https://github.com/pseudobun/paw/actions/runs/42904625034) passed. The native minimum-size regression passed with animations disabled and enabled at 180 ms: a genuine minimum remained a placeholder; switching away kept the window parked; switching back restored actual visible WindowServer bounds and native keyboard focus without a corrective `find`. Label-only fixtures also passed full-screen/float restoration and native focus checks, with a WindowServer front-order check for the floating window.

The live hover check passed with a pointer move and no click on the preceding beta.5 build. Its window-manager and placeholder sources are byte-identical to the tested beta.6 build, whose AppKit hover tests passed again. Original configuration was restored byte-for-byte and all disposable windows were closed. The inventory still records the original captured beta.1 baseline; this dated validation does not recapture that snapshot.

Real multiple-display behavior, closing during the delayed callback, drag/occlusion, physical typing/shortcuts and a same-revision live A/B remain unverified. An editable-field fixture produced extra AppKit popup windows and inconclusive restoration results. The initial Arc/Brave refusal trigger was not isolated; opening Arc's command bar alone did not reliably reproduce it. Fresh-install recovery and a live v1 rollback are still pending.

The original app, config and layout state were saved in a private recovery directory outside Git. Local test bundles omit the Sparkle update key to keep the experimental binary in place. Changing an ad hoc app's signature can require removing and re-adding its existing Accessibility entry; toggling the old entry alone retained the stale signature during this test. Recheck `paw status` after every binary replacement.

## A small experiment loop

1. Start from the saved baseline or keep a private copy of the file you are about to edit. The [recovery guide](SWITCHING.md) explains returning to v1 or undoing a profile copy.
2. Change one behavior at a time. Keep the preferred focus-follows-mouse behavior and familiar Option+I/J/K/L shortcuts. Useful experiments are stack cycling, resize steps and which apps should float.
3. Run `paw config check`, then `paw reload` and `paw status`. A reload error keeps the last good config; record the error locally rather than guessing what was applied. If PAW exits, capture the failure and restart it with `open -a paw`.
4. Test the exact action that motivated the change. Write down expected and actual results, the starting layout, relevant app versions and how often it reproduces. Stop once a test answers the question; do not rearrange unrelated workspaces for coverage.
5. Keep a useful change in the live config until it feels right. Before committing it, review the selected diff, scan for private data and update its inventory hash/provenance. A good live experiment is not automatically a new saved baseline.

Do not use a whole-profile copy for every edit: it can replace other experiments. Profile copies create recovery records, but ordinary editor changes are not automatically backed up by the copy tool.

## Capture a report draft

From the dotfiles checkout:

```sh
python3 scripts/paw_diagnostics.py
```

It prints a Markdown draft under `~/Library/Logs/dotfiles/paw/<capture>/report.md`. Each capture gets a private directory. Nothing is uploaded or posted. `--output /another/local/directory` changes the output parent; paths inside this repository are refused.

The allowlisted summary includes macOS/architecture, PAW version, CLI signing validity/type, available compiler version, configuration SHA-256, whether it matches saved v2, trust/binding health, legacy process presence and aggregate layout/display counts. If PAW stopped, the version falls back to the CLI binary and is labeled accordingly. CLI signing/compiler details may differ from a separately running development build. Missing tools produce a partial report rather than a raw error dump.

It does **not** include raw configs, status errors, window titles, app/workspace names, display identifiers, hostnames, logs or crash reports. The template still needs reproduction steps, expected/actual behavior, frequency and the last known good build. Review the completed report and every attachment before sharing.

## Collect additional evidence only when needed

For an event/order problem, run this in a second terminal, reproduce once, then press Ctrl+C:

```sh
(umask 077; /usr/bin/log stream --style compact --level info \
  --predicate 'subsystem == "com.pseudobun.paw"' \
  > "/absolute/path/to/the/private/capture/repro.log")
```

For a crash, look for the matching `paw*.ips` file in `~/Library/Logs/DiagnosticReports`. Keep raw logs, configs, recordings and crash reports outside Git. They can contain paths, titles and personal activity. Extract only the useful interval or stack after review; the diagnostics tool deliberately does not collect them automatically.

## Separate configuration/integration issues from PAW bugs

- If `paw config check` fails, reduce the configuration to the smallest failing example first.
- If the direct PAW command works but the key does not, check Karabiner's actual emitted modifiers and the registered binding before blaming the window manager.
- If direct PAW queries work but the bar is stale, inspect our hook/plugin path separately. A Sketchybar integration failure belongs in dotfiles until a direct PAW reproduction establishes otherwise.
- If it reproduces with a minimal config and without the bar/hooks, preserve that reproduction as the upstream case. A crash report alone identifies an observation, not its cause.

Avoid repeatedly reproducing a crash across all real windows. Use a small set of disposable windows and preserve an easy route back to the working desktop.

## Prepare an upstream contribution

Use the PAW source checkout that matches the tested build. Record its exact revision and existing work before changing it:

```sh
cd /path/to/paw
git status --short
git rev-parse HEAD
swift test
```

The installed app's version and source checkout can differ; a passing test run against another revision is not evidence about the installed build. Consult that checkout's `TESTING.md` for desktop checks, using our configured bindings rather than assuming the upstream defaults.

For a confirmed code bug, make a focused source branch, add a regression test at the relevant behavior, observe its failure, fix it, then run the targeted test and applicable suite. For GUI-only behavior, keep an exact manual reproduction and be explicit that it is not covered by a unit test. Keep temporary diagnostics out of the final patch.

Build/test before replacing the installed app. Preserve the working bundle and use a stable signing identity where appropriate; rebuilding an ad hoc signed app can require granting Accessibility again. A new development binary may need its own permission check.

Configuration belongs here; PAW implementation changes belong in its upstream repository or an authorized fork. Do not copy private upstream source or raw diagnostics into this public dotfiles repository. Prepare a concise issue/PR with the report, minimal config, reproduction, result and validation, then review it before submitting. This workflow does not automatically open upstream issues or send reports.
