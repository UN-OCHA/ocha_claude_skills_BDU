# Working in this repository

This is the public plugin of OCHA’s shared design skills. Everything committed here is public.

## Updating the map skill

The map skill, `plugins/ocha-bdu/skills/ocha-mapping/`, is maintained directly in this repository
by the mapping focal point. All other skills are published here by a script and must not be changed
by hand: changes to them are overwritten at the next publish.

1. Work in your own copy of this repository, on your own computer and outside Dropbox. Git folders
   break when Dropbox syncs them between people.
2. Change only files inside `plugins/ocha-bdu/skills/ocha-mapping/`. If another file seems to need
   changing, stop and tell the person, who can raise it with ochavisual@un.org.
3. **Test on a real map before sending anything.** The installed OCHA plugin still holds the published
   version, so read the skill from this folder (`SKILL.md` and `references/`) and follow that copy,
   not the installed one.
4. Send the change on a new branch, as a pull request to `main`, and describe in plain words what
   changed and why: that description is what BDU receives by email. Direct pushes to `main` are refused.
5. An automatic check runs on the pull request. It fails if anything outside the map folder changed,
   or if it finds a key or a personal path. When it passes, merge it. No review is needed. If it
   fails, its log says which file and line: fix that and push again. Never try to get around it.
6. After a merge, the plugin’s version is updated automatically, and colleagues get the change with
   their next plugin update. To undo a change, open a pull request that reverts it.

Before starting, get the latest `main` and start a new branch from it.

Never commit keys, passwords, or paths that name a person: write Dropbox paths as
`~/OCHA DMU Dropbox/<your-name>/…`.
