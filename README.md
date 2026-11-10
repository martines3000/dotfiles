# Dotfiles

Versioned desktop configurations, with old setups kept for reference.

| Profile | Status | Contents |
| --- | --- | --- |
| [macOS v1 — yabai](profiles/macos/v1-yabai/) | Historical snapshot | Pre-PAW yabai, skhd and Sketchybar; Karabiner, terminal and shell configuration |
| [macOS v2 — PAW](profiles/macos/v2-paw/) | Restore candidate | 55 files, curated dependencies, preview-first copies and rollback; clean macOS test pending |
| [Linux — Omarchy homelab](profiles/linux/omarchy-homelab/) | Planned | A separate desktop profile; host inventory still needed |
| [Legacy setups](archive/legacy-2023/) | Archived | All 221 previously tracked files, preserved without content changes |

See the [restructure report](docs/restructure-report.html) for the inventory, findings and next steps. Download/open the HTML file to view it; GitHub's file view shows its source.

The [structure research](docs/dotfiles-structure-research.md) compares five real repositories, including `pseudobun/dotfiles`, and reviewed copies, Stow and chezmoi. The recommendation is to keep explicit profiles now, separate configuration deployment from package/service setup, and select deployment tooling only after the active profiles and application write behavior have been tested.

```text
archive/legacy-2023/             # original README, fish and themes
profiles/
  macos/
    v1-yabai/
      home/                     # paths relative to $HOME
      inventory.json            # provenance and SHA-256 checksums
    v2-paw/                     # plan only
  linux/omarchy-homelab/         # plan only
docs/                           # report and public-repo rules
scripts/validate.py              # read-only integrity and file-boundary checks
```

## Using a profile

The live Mac configuration is separate from this checkout. V1 is a historical snapshot. The copy tool previews either saved profile by default; package installation and activation remain separate manual steps. [V2's fresh-install guide](profiles/macos/v2-paw/RESTORE.md) records the later clean-install work. No checkout or merge deploys a desktop automatically.

For daily PAW/Sketchybar experiments, use the [same-Mac v1/v2 recovery guide](profiles/macos/v2-paw/SWITCHING.md). `--profile v1-yabai` returns selected files to the pre-PAW snapshot with backups of current edits; it does not wipe the Mac or start/stop desktop services. Clean-install testing is deferred.

Choose one profile and read its README before copying anything. Do not link the whole `profiles/` tree, combine v1 and v2 window managers, or treat the archive as a current setup. Keep each profile self-contained until there is a proven reason to share a file between systems.

macOS and Linux/Omarchy are independent setups with different software, package management, startup behavior and validation. Host overrides, if needed, belong within the relevant OS profile. A Mac-only repository can inform organization without defining the Linux stack. Share individual files only when both maintained profiles actually use the same configuration; no cross-platform installer or matching application set is assumed.

## Before publishing changes

Use an explicit file allowlist. Follow the [public-repo rules](docs/public-repo-rules.md), review the diff, and scan **before pushing**:

```sh
python3 scripts/validate.py          # Python 3.11+
python3 -m unittest discover -s scripts
gitleaks dir . --redact=100
gitleaks git . --redact=100
git diff --cached --stat
git diff --cached
```

CI repeats the integrity checks and secret scan. A clean scanner result is useful evidence, not a guarantee that a file is appropriate for a public repository.
