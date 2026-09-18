# Automatic-update check

The Claude desktop app starts every Claude Code session with `DISABLE_AUTOUPDATER=1`, and that also
stops plugins from outside Anthropic from updating, even when the marketplace has `autoUpdate`
switched on. Two settings in the user’s `~/.claude/settings.json` turn plugin updates back on:

- `extraKnownMarketplaces.ocha-bdu.autoUpdate: true`
- `env.FORCE_AUTOUPDATE_PLUGINS: "1"`, documented under
  [Configure auto-updates](https://code.claude.com/docs/en/discover-plugins#configure-auto-updates)

At the start of each new session, `hooks.json` shows Claude the note in `autoupdate.md`. Claude then
asks the user once and adds the settings only if they say yes. After that the hook says nothing.

## How the hook stays quiet — don’t “simplify” the command

```
cat "${CLAUDE_PLUGIN_ROOT}/hooks/autoupdate${FORCE_AUTOUPDATE_PLUGINS}${env:FORCE_AUTOUPDATE_PLUGINS}.md"
```

The file it prints depends on the variable:

| `FORCE_AUTOUPDATE_PLUGINS` | File printed | Result |
|---|---|---|
| not set | `autoupdate.md` | Claude asks once |
| `1` (user said yes) | `autoupdate1.md`, empty | silent |
| `0` (user said no, don’t ask again) | `autoupdate0.md`, empty | silent. `0` keeps updates off |

The command has to run in both shells a hook can get: bash (Mac, and Windows with Git Bash) and
PowerShell (Windows without Git Bash).

- **Bash** reads `${FORCE_AUTOUPDATE_PLUGINS}` as the variable, and `${env:…}` as an empty substring.
- **PowerShell** reads `${env:FORCE_AUTOUPDATE_PLUGINS}` as the variable, and `${FORCE_AUTOUPDATE_PLUGINS}`
  as an unset PowerShell variable, which is empty.
- `cat` exists in both.
- Claude Code fills in `${CLAUDE_PLUGIN_ROOT}` before the shell runs.

**Keep the two empty files:** deleting them makes the hook fail once the user has answered.
**Keep `autoupdate.md` plain ASCII:** Windows PowerShell 5.1 garbles UTF-8 without a BOM.

## Tested (18 Sept 2026, Claude Code 2.1.271, the desktop app’s own binary and environment)

- The hook fires and delivers the note when the variable isn’t set. It says nothing when it’s `1` or `0`.
- `0` leaves updates off: `Plugin autoupdate: skipped`.
- With both settings in place, a stale copy updated itself in the background.
- Sonnet, given the note, asked first, changed only the two keys, and kept the file valid. Tested for
  “yes”, “no, stop asking” and no settings file yet.
- **Not yet tested on Windows.**
