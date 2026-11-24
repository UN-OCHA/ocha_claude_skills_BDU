[OCHA BDU skills - is this computer up to date?]

Source: the OCHA BDU plugin (github.com/UN-OCHA/ocha_claude_skills_BDU), maintained by Javi (Javier Cueto) and the OCHA Brand and Design Unit (ochavisual@un.org). The installed plugin's details (plugin.json) are printed next to this note; its "version" is the version on this computer. Versions are dates: 2026.11.24.2 means 24 November 2026, second update that day.

Why this check exists: on some computers the plugin's copy of the repository stops refreshing. The skills then stay old, the update button in Manage plugins is greyed out, and nobody notices.

What to do, at most once in this session, and only the first time a reply uses one of the ocha-bdu- skills:
- Read the latest version, quietly, with one quick request: https://raw.githubusercontent.com/UN-OCHA/ocha_claude_skills_BDU/main/plugins/ocha-bdu/.claude-plugin/plugin.json
- If it is the same as the installed version, or the request fails (offline, blocked), say nothing about it.
- If it is newer, finish the user's request, then end your reply with a short section headed "Update from Javi" that says, in the user's language and in plain words:
  "Javi has published a newer version of the OCHA BDU skills (you have [installed date], the latest is [latest date]). Javi recommends: quit Claude completely (on a Mac, Claude > Quit Claude or Cmd+Q; on Windows, File > Exit), open it again and wait a few minutes. The update downloads in the background and is used from the next session."
  Write the dates as day and month ("20 November"), not version numbers.
- If the user says they already did that and are still behind, or the installed date is more than 7 days older than the latest, walk them through the reinstall, which keeps their settings:
  1. Open + > Plugins > Manage plugins, find OCHA BDU and click Uninstall.
  2. Install OCHA BDU again from the same list. If it has disappeared: Add > Add marketplace > Add from a repository, paste UN-OCHA/ocha_claude_skills_BDU, click Sync, then install it.
  3. Quit Claude and open it again.
  If automatic updates are off on this computer (another OCHA BDU note says so), offer to switch them on first: that is the usual cause.
- Never change settings or files for this check.
