# Fresh-install and restore steps

This restores selected desktop configuration on an Apple Silicon Mac. It does not restore documents, credentials, app sessions or all development environments. Keep a separate full backup before erasing a Mac. Start with a disposable target; a clean-macOS test is still pending.

For PAW experiments on the current Mac, use the [same-Mac switch-back guide](SWITCHING.md). Clean-install testing is deferred; the later goal is the important applications and selected configs rather than exact machine replication.

## 1. Prepare the tools and packages

Install Apple's Command Line Tools (`xcode-select --install`) and Homebrew using the [official instructions](https://brew.sh/). Open a new shell with `/opt/homebrew/bin` on PATH, then clone this **public** repository:

```sh
git clone https://github.com/martines3000/dotfiles.git "$HOME/dotfiles"
cd "$HOME/dotfiles"
brew bundle install --no-upgrade --file profiles/macos/v2-paw/Brewfile
brew bundle check --file profiles/macos/v2-paw/Brewfile
```

Review the Brewfile first. No cleanup/uninstall or service activation is included. `--no-upgrade` avoids explicitly upgrading existing packages, but dependencies may still change during installation; it does not pin historical versions. If Homebrew asks for tap trust, review the named Sketchybar formula before trusting it. See [Homebrew Bundle documentation](https://docs.brew.sh/Brew-Bundle-and-Brewfile).

## 2. Validate and preview the copies

Use Homebrew's Python 3.11+; the Python bundled with Command Line Tools may be older.

```sh
python3 scripts/validate.py
python3 -m unittest discover -s scripts
python3 scripts/restore_macos.py
```

The last command previews changes to `$HOME`; it writes nothing. You can test in another directory with `--target /absolute/path/to/disposable-home`. The script refuses targets inside this repository, destination symlinks, changed source checksums and unsupported destination types before copying.

On an existing Mac, quit PAW, stop Sketchybar and quit Karabiner before applying. Review the preview, then copy:

```sh
python3 scripts/restore_macos.py --apply
```

The recovery directory is printed before destination changes. Existing files are backed up and a receipt is written before destination changes. Other files are left alone; nothing removes yabai/skhd, their configs or unrelated applications. Files are copied atomically one at a time, so an I/O failure can still interrupt a multi-file restore. Keep the recovery record until the desktop is verified.

## 3. Install PAW separately

The recorded source revision is `5249781ff7d3b40eab60383a2c943762389cf0f8` from `pseudobun/paw`. This repository contains configuration only, not PAW source or a signed app. Verify release/cask availability when restoring. If source access is still required, sign in to GitHub locally; no credentials belong here.

For the recorded source build, after authenticating and confirming access:

```sh
gh repo clone pseudobun/paw "$HOME/src/paw"
cd "$HOME/src/paw"
git checkout 5249781ff7d3b40eab60383a2c943762389cf0f8
just local-cert
just bundle
```

The local certificate step may require keychain interaction. The bundle script otherwise falls back to ad hoc signing, which may require granting Accessibility again after rebuilding. Inspect the build output. On a fresh Mac with no existing `/Applications/paw.app` or `paw` CLI link, install the built bundle:

```sh
ditto build.noindex/paw.app /Applications/paw.app
ln -s /Applications/paw.app/Contents/MacOS/paw /opt/homebrew/bin/paw
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f /Applications/paw.app
```

If either destination already exists, stop and review that installation first. These commands do not start PAW.

## 4. Activate and verify the desktop

1. Make sure competing window managers and skhd are stopped and are not scheduled to start at login. Review existing LaunchAgents on an older Mac; the restore script does not alter them.
2. Open Karabiner-Elements and complete its keyboard/input permissions. The saved mapping includes keyboard-model-specific rules; verify them on the keyboard you actually use.
3. Run `open -a paw` and grant Accessibility in System Settings. Screen Recording is optional for overview thumbnails.
4. Run `paw config check` and `paw status`; expect `trusted: yes` and `bindings: ok`. Test Option+I/J/K/L, workspace switching, Caps Lock shortcuts and resize mode.
5. Run `brew services start sketchybar`. Check workspace highlighting, fonts, helper/CPU, network state, audio and the optional account-dependent widgets. Sign into GitHub (`gh auth login`) and Spotify if desired.
6. Open Alacritty. It launches Fish itself; changing the account's login shell is optional and is not automated. Choose/install language toolchains separately.
7. Test PAW startup after login/reboot and display reconnects. Use one native Space per display as recommended by the PAW version you install. Tune macOS tiling/Spaces settings manually if they conflict.

Do not call the restore verified until these checks pass on the fresh machine.

## Undo a copy

Use the exact recovery directory printed by the restore command. Preview first:

```sh
python3 scripts/restore_macos.py --rollback "/absolute/path/to/recovery-directory"
python3 scripts/restore_macos.py --rollback "/absolute/path/to/recovery-directory" --apply
```

Use the same `--target` if restoring a disposable home. Rollback restores backed-up files and removes files created by that restore only while they still match the deployed bytes. Later edits or symlinks cause preflight refusal before any rollback write; review those files manually. Recovery files are retained. This undoes configuration copies only, not packages, accounts, permissions or services.
