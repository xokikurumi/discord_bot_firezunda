# AGENTS.md

## Discord Commands

- Discord command features must support both prefix commands using `!` and slash commands using `/`.
- When adding or changing a `commands.hybrid_command` or `commands.hybrid_group` subcommand, verify that argument parsing works in both forms.
- Do not rely only on slash-command named arguments. Prefix commands parse positional text, so optional arguments, channel/user converters, free-text fields, and emoji arguments must be designed to avoid ambiguous or broken `!` usage.
- Usage text and release notes must show examples that work with `!` commands as implemented.
