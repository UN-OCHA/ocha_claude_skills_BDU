[OCHA BDU skills - automatic updates are off on this computer]

Source: the OCHA BDU plugin (github.com/UN-OCHA/ocha_claude_skills_BDU), maintained by the OCHA Brand and Design Unit (ochavisual@un.org). The user installed it themselves from Claude's Manage plugins panel. This note appears at the start of new sessions until the user switches updates on or asks not to be asked again.

Why: the Claude desktop app switches off Claude Code's own updater, and that also stops plugins from outside Anthropic from updating. Two documented Claude Code settings turn plugin updates back on: "autoUpdate" on the plugin's marketplace, and the environment variable FORCE_AUTOUPDATE_PLUGINS (code.claude.com/docs/en/discover-plugins, section "Configure auto-updates"). Both affect plugin updates only.

What to do:
- Once in this session, at the end of your first reply, ask in your own words and make clear the question comes from the OCHA BDU plugin. For example: "The OCHA BDU plugin can't update its skills on this computer yet. Shall I switch that on? It adds two lines to your Claude settings."
- Change nothing unless the user says yes.

If they say yes: in the Claude settings file (~/.claude/settings.json on a Mac, %USERPROFILE%\.claude\settings.json on Windows; create it if missing), keep everything already there and add:
  1. Under "extraKnownMarketplaces": "ocha-bdu": {"source": {"source": "github", "repo": "UN-OCHA/ocha_claude_skills_BDU"}, "autoUpdate": true}
     If an "ocha-bdu" entry already exists with that repo, only add "autoUpdate": true to it. If it points to a different repo, change nothing and tell the user.
  2. Under "env": "FORCE_AUTOUPDATE_PLUGINS": "1"
  Check the file is still valid JSON. Then tell them: quit Claude and open it again, and from then on the skills update in the background.

If they say no: ask whether to stop asking on this computer. If yes, add only "FORCE_AUTOUPDATE_PLUGINS": "0" under "env" - this keeps updates off and silences this note. If they want to be asked again later, change nothing.

Change nothing else in the file.
