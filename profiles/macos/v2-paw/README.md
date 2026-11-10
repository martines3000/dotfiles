# macOS v2 — PAW baseline

A 55-file PAW desktop profile for this Apple Silicon Mac, captured and activated on **2026-11-10**. PAW trust/binding health and bar state were checked. Copies, backups and rollback are tested against disposable directories. A fresh macOS install and physical keyboard behavior have **not** been tested.

[Experiments and debugging](DEBUGGING.md) · [Same-Mac v1/v2 recovery](SWITCHING.md) · [Fresh-install steps](RESTORE.md) · [Dependencies](Brewfile) · [Source inventory](inventory.json)

## Included

- PAW layouts, rules, focus behavior, workspace/resize shortcuts and Sketchybar hooks.
- PAW-aware Sketchybar workspace controls and the existing bar's source files; no compiled helper or obsolete yabai/skhd controls.
- Karabiner's existing device mappings, Alacritty, Fish, Starship and Zsh configuration.
- A curated Brewfile for the desktop, shell and fonts. It does not dump all installed developer tools or start services.
- A preview-first copy command with checksum checks, symlink refusal, private backups and rollback. No link manager is required.

For experiments, `--profile v1-yabai` copies the preserved pre-PAW files; `--profile v2-paw` copies this candidate (the default). Follow the same-Mac recovery guide to stop one desktop and start the other. The tool does not switch services or login items. Clean-install testing is deferred; restoring the important apps and their selected configuration is the intended later scope.

The original v1 configuration snapshot and all 221 archived files remain unchanged. `inventory.json` records source and published hashes, the PAW source revision and changes relative to the pre-activation live source. Activation replaced seven files after saving them to a private recovery directory. The active PAW config matches this saved baseline; legacy managers are stopped and their known login entries disabled.

## Deliberate v2 changes

- Keep the old Option+I/J/K/L focus, Shift+Option swaps, Option+numbers and Ctrl+Shift+numbers workspace shortcuts.
- Retain standard Hyper shortcuts and add equivalent Cmd+Ctrl+Shift+Fn aliases for the existing Caps Lock mapping, including leaving resize mode. Karabiner itself is unchanged. Verify the physical keyboard before relying on Caps Lock shortcuts.
- Use PAW-native focus borders and workspace controls; do not run yabai/skhd alongside PAW.
- Replace the removed Wi-Fi `airport` call with active interface state. The widget shows Wi-Fi/IP rather than promising SSID access; its inherited tunnel indicator is a heuristic, not a VPN security check.
- Open System Settings by its current name. Bar startup no longer unloads the system volume overlay service.
- Guard optional shell tools, use the installed fnm executable rather than an old Linux path, and remove unconditional Miniconda initialization. Historical nvm/bass helpers remain optional source; installing a full developer toolchain is outside this desktop profile.

## Configuration ownership

The restore command copies regular files into the live home directory. Karabiner and PAW can write live settings without modifying this checkout. To capture later changes, diff and review selected files, scan for secrets, and update the inventory hashes before committing. No automatic capture or private backup upload occurs.

Existing destination files are saved under `~/Library/Application Support/dotfiles/backups/` with a recovery receipt before replacement. Destination symlinks are refused so an old Stow/chezmoi link cannot redirect writes into a frozen snapshot. Runtime state, windows/workspace history, credentials and installed applications are not restored.

The copy operation does not quit applications, install packages, change the login shell, grant permissions or start services. Stop PAW, Sketchybar and Karabiner before applying to a real existing home; restart them only at the activation step. PAW's saved config requests open-at-login when the app is later launched.

macOS and Linux/Omarchy remain independent software stacks. If multiple Macs eventually need different values within this PAW generation, small host overrides could live inside this profile. No host overlay directories or cross-platform installer are introduced now.

## Known limits

PAW is a source-built beta; the recorded build was `0.1.0-beta.1+5249781`, revision `5249781ff7d3b40eab60383a2c943762389cf0f8`, signed ad hoc. Source access and signing must be handled separately on a new Mac. A Brewfile installs available versions and is not a historical package lockfile.

Permissions, keyboard models/layout, multiple displays, login startup and all bar widgets still need testing on a clean machine. GitHub and Spotify widgets require their apps/accounts; they are not restored sessions. The CPU helper is built locally on first bar startup using the Command Line Tools. Local overrides should be added per application only after documenting location, precedence, missing-file behavior and capture exclusion.
