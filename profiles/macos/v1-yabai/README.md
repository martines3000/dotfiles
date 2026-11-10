# macOS v1 — yabai, skhd and Sketchybar

Historical configuration captured on **2026-11-10**, before the PAW configuration is added to this repository. This profile is an archival backup, not a claim that every component still works on current macOS.

## What was captured

The 60 files in `home/` mirror their destination paths beneath `$HOME`:

| Component | Saved files | Source |
| --- | --- | --- |
| yabai | `.yabairc`, `.config/yabai/presentation-mode.sh` | `.yabairc` from the pre-PAW backup; unchanged companion script from the Mac |
| skhd | `.skhdrc` | Pre-PAW backup |
| Sketchybar | `.config/sketchybar/` | Entry point from the pre-PAW backup; unchanged scripts and helper source from the Mac |
| Karabiner-Elements | `.config/karabiner/karabiner.json` | Local configuration last modified 2026-11-05 |
| Alacritty | `.config/alacritty/alacritty.toml` | Local terminal configuration |
| Fish | `.config/fish/config.fish`, `functions/`, `conf.d/` | Local shell configuration and source files |
| Starship | `.config/starship.toml` | Local prompt configuration |
| Zsh | `.zshrc`, `.zprofile` | Local initialization files |

The pre-PAW backup was made during the Mac's PAW migration. The Sketchybar entry point restores its `spaces.sh` and `yabai.sh` imports; the newly created PAW scripts and compiled `helper` executable are excluded. Helper C sources and the makefile are included so the binary can be rebuilt.

The terminal, shell and Karabiner files were collected during this audit. They were not all independently backed up before PAW was installed, so this is a reconstructed window-manager snapshot with companion configuration, not a full point-in-time Mac backup.

`inventory.json` records each file's source, source checksum, published checksum and normalization. Only three files changed during capture: user-specific `/Users/...` and `/home/...` paths in `.zshrc`, Fish's `config.fish` and `conf.d/fnm.fish` became `$HOME`. Other source contents are unchanged.

## Dependencies recorded on the Mac

These are observed versions, not a lockfile or a tested installation recipe.

| Component | Observed version | Installed source / requirement |
| --- | --- | --- |
| yabai | 7.1.25 | `asmvik/formulae` fork |
| skhd | 0.3.9 | `koekeishiya/formulae` |
| Sketchybar | 2.24.1 | `felixkratz/formulae` |
| borders | 1.9.0 | `felixkratz/formulae`; launched by `.yabairc` |
| Karabiner-Elements | 16.3.0 | macOS application |
| Alacritty | 0.17.0 | macOS application |
| Fish / Starship | 4.9.3 / 1.27.0 | Shell and prompt |
| jq / GitHub CLI | 1.8.2 / 2.103.3 | Bar scripts; authenticate `gh` locally |

The terminal uses JetBrainsMono Nerd Font; bar labels use sketchybar-app-font and SF Pro/SF Symbols. Shell files also reference fnm, nvm/bass, eza, bat, Miniconda, Jabba, SDKMAN, RVM, Android tools and optional tabtab initialization. Their data, installations and authentication are not backed up here. This is why a complete Brewfile is deferred rather than inferred from every package installed on the Mac.

## Known limits to carry into the next profile

- **Caps Lock is not standard Hyper.** The Karabiner description says Command+Control+Option+Shift, but the actual output is Shift+Command+Control+Fn. A separate rule maps that chord plus V to another keystroke. Device-specific modifier swaps and the ISO keyboard setting are preserved. Decide explicitly how this should map to PAW's `hyper` modifier in v2.
- **Modern macOS compatibility:** the Wi-Fi widget still calls the removed `airport` utility; the Apple menu opens the old `System Preferences` name. These were preserved, not silently repaired in a historical snapshot.
- **Privileged yabai features:** `.yabairc` invokes `sudo yabai --load-sa`. Scripting-addition support, OS security settings and any narrowly scoped sudo setup must be reviewed for the target macOS version. No sudoers or security-setting changes are included.
- **Native Spaces:** skhd and Sketchybar control yabai's native Spaces. This is a different model from PAW's virtual workspaces.
- **External state:** macOS permissions, Spaces, login items, fonts, private credentials and application state cannot be restored from these files alone.
- **Shell drift:** multiple language/version managers are referenced, and the Fish fnm initializer originally contained a Linux home path. The path was made portable; version-manager cleanup belongs in a later profile.

## If this profile ever needs restoring

1. Back up the destination files and read the diff against this profile. Do not overwrite a live PAW setup while it is running.
2. Review and install the desired dependencies; rebuild Sketchybar's helper with its makefile. Authenticate tools on the machine without storing credentials in this repository.
3. Copy only the files you have reviewed from `home/` to the corresponding paths under `$HOME`. An application may need to be stopped before replacing its configuration. Keep file permissions from the snapshot.
4. Grant required macOS permissions and configure startup on that machine. Machine-generated LaunchAgent plists were deliberately omitted.
5. Test terminal startup, actual keyboard chords, display/Space behavior, bar widgets and resize mode before making this the login setup.

The current copy tool supports `python3 scripts/restore_macos.py --profile v1-yabai` (preview) and the same command with `--apply` (back up and copy). Follow the [same-Mac recovery guide](../v2-paw/SWITCHING.md) for stopping PAW and reactivating the existing yabai/skhd services. The saved configuration still has the compatibility limits above; service switching and login items remain manual.
