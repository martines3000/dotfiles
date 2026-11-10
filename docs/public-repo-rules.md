# What belongs in this public repository

Commit selected configuration source, not an unfiltered copy of a home directory. Review both filenames and contents before staging and pushing. Never rely on a public PR or CI scan to make a secret private again.

## Include after review

- Window-manager, bar and keyboard configuration, including intentional hardware-model IDs where needed for remapping.
- Terminal themes, shell functions, prompt configuration and editor settings without personal data or authentication.
- Small, curated dependency lists and manual setup notes. Record provenance and distinguish an archival snapshot from a tested current profile.
- Source for helpers and scripts. Rebuild binaries locally.

## Keep out

- **All SSH configuration**, keys, certificates, known hosts, agent state and authorization files, even if a particular file appears harmless.
- API tokens, passwords, recovery codes, private signing keys, `.env` files, package-registry credentials, cloud authentication, GitHub CLI state and Git credential stores.
- Full `.gitconfig` identity/work configuration, machine-generated LaunchAgent plists with copied PATH values, sudoers exports and blanket macOS defaults dumps.
- Fish universal variables, histories, completions generated from the machine, automatic application backups, caches, logs, compiled helpers and shell session state.
- VPN state, internal hostnames/addresses, private repository URLs, work-specific configuration, device addresses/serials and personal service data. Review these manually; a secret scanner cannot identify all private context.
- Browser profiles, cookies, chat/AI tool sessions, account exports, accessibility databases and other application state.

`.gitignore` and `scripts/validate.py` block common private paths and generated files. They are guardrails, not a complete privacy audit. Gitleaks adds content-based detection; it does not prove the absence of secrets.

The archive retains three already-published Fish universal-variable files and one old Alacritty `.bak` file because the original 221 files are preserved verbatim. These historical files were reviewed and scanned; their contents are checked against the original Git blobs. This exception permits no new state files or content changes, and the secret scan still covers the archive. No SSH files were present in the original tracked tree.

For this initial capture, the source tree and Git history were scanned before publishing. The three core pre-PAW configuration files were taken from the migration backup rather than from the active PAW setup. Published source hashes and any home-path normalization are recorded in the Mac v1 inventory.

If a secret is ever committed, stop publishing it and rotate it. Deleting the current file does not remove previous commits; evaluate a separate history cleanup after rotation.
