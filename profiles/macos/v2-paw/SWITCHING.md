# Experiment with PAW and return to v1 on this Mac

No macOS reinstall or data wipe is needed. The saved v1 profile restores the selected yabai/skhd/Sketchybar, keyboard, terminal and shell files. Existing yabai/skhd installations and their LaunchAgents remain on this Mac. Window positions, native Spaces and app sessions are not part of this configuration snapshot.

There are two different recovery actions:

- **Copy v1:** return the selected configuration files to the known pre-PAW snapshot, backing up their current contents first.
- **Undo a copy:** use its recovery receipt to return to the files immediately before that copy. This can bring back experimental settings that were overwritten by copying v1.

The tool handles configuration files. Starting/stopping window managers and changing login startup remain explicit steps; never run both sets together. The commands below are instructions, not actions performed by this PR.

## Return to the v1 desktop

1. Preview the v1 files before stopping anything:

   ```sh
   python3 scripts/restore_macos.py --profile v1-yabai
   ```

2. Disable PAW's start-at-login setting so it does not return on the next login. Stop the bar, quit PAW and temporarily quit Karabiner before replacing files:

   ```sh
   brew services stop sketchybar
   paw quit
   ```

   If PAW already stopped or crashed, skip its quit command. Restarting PAW and quitting normally can recover windows it had hidden; do not start yabai while PAW is still managing them.

3. Copy the v1 files. Keep the printed recovery directory if you may want your experimental configuration back:

   ```sh
   python3 scripts/restore_macos.py --profile v1-yabai --apply
   ```

   This backs up replaced files. It leaves the PAW config and unused PAW bar scripts in place; the restored Sketchybar entry point uses v1's controls. Other files and personal data are untouched.

4. Start Karabiner again. Check Accessibility grants for yabai/skhd in System Settings; grant them again if required. The installed skhd currently refuses a CLI invocation from the agent session without Accessibility, so its live activation still needs verification. Re-enable and load the existing LaunchAgents on **this Mac**, then start Sketchybar:

   ```sh
   launchctl enable "gui/$(id -u)/com.asmvik.yabai"
   launchctl enable "gui/$(id -u)/com.koekeishiya.skhd"
   launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.asmvik.yabai.plist"
   launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.koekeishiya.skhd.plist"
   brew services start sketchybar
   ```

   The labels above were read from this Mac's existing setup. Another installation may use different labels or need services installed separately. Do not copy machine-generated LaunchAgent plists into the repository.

5. Check focus/swap keys, native Spaces, floating windows and the bar. V1 preserves old widget quirks and any yabai scripting-addition requirements; it is not an upgrade to those components. If the current macOS version no longer supports a v1 feature, inspect it rather than changing OS security settings automatically.

## Return to the saved PAW v2 candidate

Stop yabai/skhd and the bar, then preview/copy v2 and activate it using the [activation steps](RESTORE.md#4-activate-and-verify-the-desktop):

```sh
launchctl bootout "gui/$(id -u)/com.asmvik.yabai"
launchctl bootout "gui/$(id -u)/com.koekeishiya.skhd"
launchctl disable "gui/$(id -u)/com.asmvik.yabai"
launchctl disable "gui/$(id -u)/com.koekeishiya.skhd"
brew services stop sketchybar
python3 scripts/restore_macos.py --profile v2-paw
python3 scripts/restore_macos.py --profile v2-paw --apply
```

If a LaunchAgent is already unloaded, skip its bootout step. Quit Karabiner before copying its configuration and restart it afterward. The commands disable the two old login entries; the copy tool itself does not make that change. PAW's saved v2 configuration requests start-at-login when the app is later launched.

## Bring back the experiment you had before copying v1

Stop v1's window manager/hotkey daemon and the bar first. Preview the exact receipt printed by that v1 copy, then undo it:

```sh
python3 scripts/restore_macos.py --rollback "/absolute/path/to/recovery-directory"
python3 scripts/restore_macos.py --rollback "/absolute/path/to/recovery-directory" --apply
```

Rollback is independent of `--profile`, so those options cannot be combined. Later edits cause refusal before rollback writes; review those files manually instead of overwriting them. PAW-only files not touched by the v1 copy remain as they were. Reactivate PAW and its startup settings explicitly afterward.

Only configuration copy/recovery has been tested in disposable directories. The live desktop has not been switched to v1 and back as part of this change. Clean-install recovery is a later task; its intended scope is the important apps and selected configuration, not an exact machine image.
