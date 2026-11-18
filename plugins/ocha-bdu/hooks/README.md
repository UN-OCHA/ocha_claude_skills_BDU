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

# What’s new after each update

After an update, Claude tells each colleague once, in plain words, what changed in the skills.

## Writing the note (every publish)

Before publishing, write `news/next.md`: 2 to 4 bullet lines, one per change a colleague would
notice, written for designers, not developers (what they can now do, or what works differently).
`sync_skills_to_github.sh --push` stops if the plugin gets a new version and no note exists.

The publish script runs `.github/scripts/build_whats_new.py`, which:

- moves the note into `news/CHANGES.md` under the plugin’s new version (newest first; colleagues
  can read the full history there);
- writes `news/after-<version>.md` for every version: the updates that came after it (at most
  five), with instructions for Claude. The latest version’s file is empty;
- writes `news/after-.md` for a computer that has never seen a note: the latest update only.

## How the hook knows what each computer has seen

```
cat "${CLAUDE_PLUGIN_ROOT}/news/after-${OCHA_BDU_NEWS_SEEN}${env:OCHA_BDU_NEWS_SEEN}.md"
```

Same two-shell trick as the update check above. After telling the user, Claude sets
`env.OCHA_BDU_NEWS_SEEN` in their `~/.claude/settings.json` to the latest version. From the next
session the hook prints that version’s file, which is empty until the next update.

- **Never delete an `after-*.md` file or a `CHANGES.md` entry:** a computer still pointing at that
  version would get an error at startup instead of the news.
- **The `after-*.md` files must be plain ASCII** (PowerShell 5.1, as above). The build script
  converts curly quotes, dashes and accents, and stops on anything else. `CHANGES.md` and
  `next.md` can use any characters.
- Versions stamped on GitHub after a map-skill pull request get no note. That is fine: no computer
  is ever pointed at a version without one.

Tested 18 Nov 2026 on a copy of the repo (bash): first run, an up-to-date computer, two updates in
a row, and the missing-note stop. **Not yet tested on Windows or in a live session.**
