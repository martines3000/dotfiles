# Linux — Omarchy homelab (planned)

A separate desktop profile for the homelab PC, not a copy of an old Arch theme and not a server provisioning repository. The host was not accessed or modified for this PR. Its installed Omarchy version and actual paths are not yet known.

Start the follow-up with an allowlisted inventory on the PC:

- Identify the installed Omarchy version, active desktop configuration and local overrides before choosing files. Omarchy generations differ; do not assume an older `hyprland.conf`/Waybar layout or the current generation's Lua/Omarchy-shell paths match this host.
- Review desktop keybindings, input, display layout, look-and-feel, user autostart, bar/shell configuration, terminal, shell, prompt, editor configuration and custom theme source.
- Separate portable preferences from display serial numbers, hostnames, internal addresses and other machine-local values. Keep the latter outside the public repository or replace them with deliberate examples.
- Track selected user-owned overrides and the Omarchy version they were tested with. Preserve upstream-owned defaults and update behavior instead of copying the entire Omarchy installation.
- Add an explicit list of extra packages only after distinguishing user additions from packages provided by Omarchy. Keep deployment opt-in and test rollback before enabling startup behavior.

Before calling the profile deployable, record tested versions, whether each destination is owned by the user, an application or Omarchy, its copy/link policy, conflict handling and a verified rollback. For supported local overrides, document their exact location, precedence, missing-file behavior and capture exclusion. Test against a disposable target first; keep package installation and service activation separate from configuration deployment. See the [structure research](../../../docs/dotfiles-structure-research.md) for examples and manager tradeoffs.

Exclude SSH configuration, VPN/Tailscale state, Kubernetes credentials, service `.env` files, disks/mount credentials, private network topology, browser/session data and all homelab service secrets. Container stacks, infrastructure deployment and host access belong in a separate private repository if needed.

The [current official dotfiles manual](https://omarchy.org/manual/dotfiles/) describes user overrides under `~/.config` and cautions against editing Omarchy-owned files. Consult the documentation matching the PC's installed generation when capturing it.
