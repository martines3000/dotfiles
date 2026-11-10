# macOS v2 — PAW (planned)

Reserved for a separate, reviewed PAW profile. This directory contains no deployable configuration yet. The working PAW files on the Mac are intentionally outside this PR's snapshot.

For the follow-up PR:

1. Capture `.config/paw/config.json5` and the PAW-aware Sketchybar entry point, items and plugins with their own provenance. Keep v1 frozen.
2. Resolve Karabiner's actual Caps Lock chord versus PAW's standard `hyper` modifier, then verify the physical shortcuts on the keyboards in use.
3. Carry over the familiar focus/swap keys, layouts, resize mode, terminal launcher, gaps and bar reservation. Document native Spaces versus PAW workspaces and any mouse-control differences.
4. Validate app rules, multi-display behavior, workspace restoration and startup. Preserve a tested way to return to v1, with only one window manager/hotkey daemon active.
5. Record the PAW source/release and signing method. Recheck the Homebrew tap before publishing an installation recipe; do not assume a cask is available.
6. Fix the old bar's obsolete Wi-Fi/System Settings integrations and trim unused widgets only after testing them.
7. Consider a curated Brewfile and an explicit, backup-first linking workflow once the profile is stable. Do not capture the machine's entire package inventory or introduce shared configuration until both profiles need the same file.

Terminal, shell and prompt files can be copied from v1 and intentionally updated. Do not symlink v2 back into the immutable v1 snapshot.
