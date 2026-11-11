# Repository instructions

Before adding or publishing files, read [the public-repository rules](docs/public-repo-rules.md). Before pushing, run the checks in the README's “Before publishing changes” section.

## Commits and pull requests

- Use Conventional Commits for new commit subjects and PR titles: `type(scope): description`. The scope is optional.
- Use lowercase types and scopes. Choose `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`, `perf`, `build`, `style`, or `revert` to match the final change.
- Write a short imperative description, for example `feat(diagnostics): add private PAW diagnostics`, `fix(sketchybar): correct Wi-Fi status`, or `chore: refresh dependencies`.
- Keep PR descriptions focused on the final diff, using `Summary`, `Evidence`, and `Merge Danger` sections. State actual validation results, remaining limits, and relevant recovery steps. Identify the dependency/base of a stacked PR.
