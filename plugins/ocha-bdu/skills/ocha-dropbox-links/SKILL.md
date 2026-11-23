---
name: ocha-dropbox-links
description: >
  Make truly public (“anyone with the link”) Dropbox links for files and folders, through Claude, and
  check whether a Dropbox link opens for people outside OCHA. Use whenever someone asks to “share this
  file publicly”, “give me a Dropbox link”, “public link”, “download link”, “make this Dropbox file
  public”, “link for the brand portal / README / email to a partner / Canva”, or says “my Dropbox link
  doesn’t work for external people” or “the link asks people to sign in”. Includes the one-time setup
  that connects the person’s own Dropbox. NEVER use the Dropbox connector’s create_shared_link for
  these: it makes links only OCHA team members can open, and it takes the file’s one main link.
---

# Public Dropbox links

Links that open for **anyone with the link**, made with `scripts/dropbox_links.py` through the Dropbox
API. Each person connects their **own** Dropbox once (§1); after that Claude makes the links.

**Never use the Dropbox connector’s `create_shared_link`** for a link that leaves the OCHA team. It
makes a team-only link (outsiders get a sign-in page), and it takes the file’s one main link, so even
“Copy link” in Dropbox then gives the team-only one. The connector is still fine for finding files
(`search`, `list_folder`) and reading them.

`<skill>` below means this skill’s folder (the base directory shown when the skill loads). On
Windows the command is usually `python` or `py` instead of `python3`.

---

## 1. Check the setup first

```bash
python3 <skill>/scripts/dropbox_links.py status
```

`READY - connected to the Dropbox of …` → go to §2. `NOT SET UP` → walk the person through the
one-time setup below. Do every step you can yourself; they only click in the browser and paste into
private pop-ups. Tell them first, in your own words:

*“To make public Dropbox links I need a one-time setup: about 5 minutes. You create a small Dropbox
‘app’ of your own (just a key that lets me make links in your Dropbox; nobody else’s), then allow it.
Nothing goes in this chat: you paste into private pop-ups, and the key stays on your computer.”*

### Step 1 — the person creates their Dropbox app

Open the page for them:

```bash
python3 <skill>/scripts/dropbox_links.py open-console
```

Then give them these steps (sign in to Dropbox with the OCHA account first if it asks):

1. **Choose an API:** “Scoped access”.
2. **Type of access:** “Full Dropbox”.
3. **Name:** “OCHA links” and their name, e.g. “OCHA links Alex”. If the name is taken, add initials
   or a number.
4. Click **Create app**.
5. Open the **Permissions** tab and tick **files.metadata.read** (under Files and folders),
   **sharing.read** and **sharing.write** (under Collaboration). Click **Submit** at the bottom.
6. Tell Claude when it’s done. Leave that browser tab open.

Step 5 matters: the connection only gets the permissions the app had at the moment they click Allow.

### Step 2 — connect (Claude runs it, the person pastes)

Run with a **10-minute timeout** (`timeout: 600000`): it waits for the person.

```bash
python3 <skill>/scripts/dropbox_links.py setup
```

Tell them what will happen, before you run it:

1. A pop-up asks for the **App key**: on the app’s **Settings** tab, the value labelled “App key” (not
   the App secret). Copy it and paste it into the pop-up.
2. The browser opens a Dropbox page: click **Continue**, then **Allow**. Dropbox shows a code.
3. A second pop-up asks for that code. Paste it.

It ends with `Connected to the Dropbox of <name>`. That’s all: it lasts until they remove the access.

- The pop-up can open **behind other windows** (on Windows, look in the taskbar).
- The two values go only into `~/.claude/tokens.json` on that computer. Never ask for them in chat;
  never write them into a job folder, a skill or a message. If someone pastes one into chat anyway,
  carry on, and suggest they make a new app later.
- No app secret is used at all (the connection uses Dropbox’s secret-free method for desktop tools).

---

## 2. Make the links

```bash
python3 <skill>/scripts/dropbox_links.py share "<file or folder>" ["<another>" …]
```

What to pass, best first:

- **The local path** of the file in the person’s Dropbox folder on their computer
  (e.g. `~/Dropbox/<your-folder>/…/file.pdf`). The script works out the Dropbox path.
- A **Dropbox path** (`/Team folder/…`): team folders work too.
- An **id** (`id:Els7…`) from the Dropbox connector’s `search` or `list_folder`.

Each line of output is `OK` or `NOT PUBLIC`, the item, the link, and what happened. Every link is
tested as if by someone **not signed in** before it is reported `OK`. Give the person the link; report
any `NOT PUBLIC` or `FAIL` line as it is.

**Which form of the link:**

| For | Option | Link looks like |
|---|---|---|
| Showing the file (preview page) | *(none)* | `www.dropbox.com/…&dl=0` |
| Download buttons (brand portal, READMEs) | `--download` | `www.dropbox.com/…&dl=1` |
| Tools that fetch the file themselves (Canva, some web forms) | `--direct` | `dl.dropboxusercontent.com/…` |

Match what the page already uses when updating links on an existing page.

**Existing links are kept.** If the file already has a public link, that same link comes back (it may
already be on a live page). A team-only link (e.g. one the connector made) is switched to public and
keeps its address. Only when Dropbox refuses that is the old link removed and a new one made; the
output then says so, because anything that used the old team-only link stops working.

**Links follow the file.** Moving or renaming a published file or folder, or replacing it with a new
file instead of overwriting it, breaks the link. See `ocha-files-and-folders` for replacing files safely.

## 3. Check a link someone else made

```bash
python3 <skill>/scripts/dropbox_links.py check "<link>" ["<link>" …]
```

`PUBLIC` or `NOT PUBLIC` for each, as seen by someone not signed in. Needs no setup. For a
`NOT PUBLIC` link to a file in the person’s own Dropbox, offer to fix it with `share` (§2).

---

## 4. When something fails

A failing connection is a **stop**, not a detour: say what failed and how to fix it. Never fall back
to the connector’s `create_shared_link` or to making the link by hand without saying so.

| Message | Fix |
|---|---|
| `NOT SET UP` | §1 |
| `invalid_grant` / “connection stopped working” | The access was removed (or the app deleted): run `setup` again (§1, step 2) |
| “missing these permissions” / `missing_scope` | Tick the three permissions on the app’s Permissions tab, Submit, run `setup` again |
| “App key was not recognised” | Copy the App key again from the Settings tab (not the secret) |
| “code works once…” | The code expired: run `setup` again and paste the new code straight away |
| `not_found` / “can’t see this file” | The file isn’t in the connected person’s Dropbox, or Dropbox hasn’t finished syncing it |
| “not inside a Dropbox folder” | The file is only on the computer: move or copy it into the Dropbox folder first |
| “team’s sharing settings refused” | The team policy blocks public links for that folder: ask the team admin |
| Allow page says the app is invalid | The App key was mistyped, or on the Settings tab “Allow public clients” is set to Disallow: set it to Allow |

## Project Owner

Javier Cueto, Head of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)

<!-- bdu-suggest-change:start -->
**Suggesting a change to this skill.** If the person corrects you or states a rule that would apply to other jobs too, or you find this skill is wrong or missing something, say so once, at the end of your reply. Don’t do this for changes that only concern the current job, and don’t edit the skill yourself, because the next update would overwrite it. Leave out anything confidential from the job. Say:

> This could be worth adding to the OCHA BDU skills. If you agree, copy this message and send it to Javi:
> **Skill:** ocha-dropbox-links
> **Proposed rule:** [the rule, in one or two sentences]
> **Why:** [what happened, with one example]
<!-- bdu-suggest-change:end -->
