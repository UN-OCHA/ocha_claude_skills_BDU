---
name: ocha-bdu-frontify
description: Drive the OCHA Frontify brand portal (brand.unocha.org) — the MCP driver setup, and the hard-won operations matrix for what works via personal token (REST and public GraphQL) vs Chrome session vs "no path exists, do it in the editor". Use whenever the user asks to read, create, update, or troubleshoot any Frontify page, block, section, or brand-portal content, or mentions Frontify, brand.unocha.org, guideline pages, or content blocks.
---

# Frontify operations

**This skill is for the Brand and Design Unit (BDU) only.** Editing the brand site is BDU’s job: nobody else has an account, and none is offered. If the person isn’t in BDU, don’t set anything up or try to get them access.

**Everyone in BDU has an admin account on the brand site.** Don’t ask whether they have rights or need to “check with the admin”. The site is `brand.unocha.org` (portal id 152622, brand id 168519). Javier Cueto is the top admin.

**Rules for every change. The site is live and has no staging copy:**

- Say what you will change and show it before touching a published page. Wait for the person’s yes.
- Rehearse anything new on the hidden test page first (see *Building a page section*).
- Prefer the reversible action: unpublish rather than delete. Deleted items can be restored in the editor for 60 days.
- **Never show one uploaded image on two blocks** (a test block and a live one, two pages). An image
  uploaded in the editor belongs to the page: removing it from **any** block deletes it from Frontify,
  and every other block showing it goes blank. Give each block its own upload, or use a library image
  (`upload_asset`), which is never deleted this way. Tested 19 Nov 2026 after the HNPW page lost its
  Teams background (18 Nov). `set_block_image` refuses both risky moves on its own (below).
- After a change, read it back from the site, then give the person the page link to check.
- Don’t run many requests at once. The site’s firewall blocks bursts for about 90 seconds; a full scan takes about 15 minutes, so run it in the background.
- Each person uses their own token. Never ask for a token in chat; `setup_connection.py` asks in a private pop-up.

How pages are organised (sections, subtitles, dividers): read `references/content-structure.md` before building anything.

## Frontify MCP — how to drive it (server lives in the brand-portal repo)

The code is `server.py` in the shared `frontify-mcp` folder (BDU’s Dropbox, under `Design/Visual_identity/assets/Brand portal/`). **Import it as a module and call its async functions directly.** It finds the person’s own token by itself. Not set up yet, or `server` won’t import? Find that folder on their computer and follow `SETUP.md` in it.

```bash
export PYTHONDONTWRITEBYTECODE=1  # the folder is shared on Dropbox: leave nothing behind
cd "$(python3 -c "import os; h=os.path.expanduser('~/.claude'); m=os.path.join(h,'frontify_server_folder.txt'); p=os.path.join(h,'skills/ocha-bdu-frontify'); f=os.path.join(p,'server_folder.txt'); print(open(m).read().strip() if os.path.exists(m) else open(f).read().strip() if os.path.exists(f) else os.path.realpath(p+'/../..'))")"
uv run --with httpx --with mcp python3 <<'PY'   # uv is usually in ~/.local/bin
import asyncio, server
async def main():
    print(await server.get_page_structure(PAGE_ID))
asyncio.run(main())
PY
```

Key doc/page IDs: Visual Identity document = **281801**; "Corporate resources" doc = **478637**; "This is OCHA" page = 3502611. Fonts page = 3068473.

## Frontify operations matrix — THREE auth surfaces (learned the hard way, May 2026)

Frontify gates operations across three auth layers: REST with the personal token, the public `/graphql` with the same token (add `X-Frontify-Beta: enabled` for anything on guideline pages), and the Chrome session. **Always reach for the personal token first; only fall back to Chrome when the token is genuinely blocked; some ops have no programmatic path.**

| Operation | Works via… | Notes |
|---|---|---|
| Read pages / blocks / structure | **Personal token** REST (`/api/document-page`, `/api/document-block/{id}`) + `/graphql-internal` reads | `get_page_structure`, `inspect_block`, `list_pages` |
| **Read colour swatches on a page** (name, HEX, RGB, CMYK, Pantone) | **Personal token**, public `/graphql` with `X-Frontify-Beta: enabled` → `get_page_colors(page_id)` | **No Chrome** (verified 29 Oct 2026 on IASC page 4243684: “IASC blue” #002E6E, RGB 0 46 110, CMYK 100 80 0 40). Query `guidelinePage(id: <opaque guideline-page id>)` → `sections.items.elements.items`, fragment `... on BrandEssentialsColorBlock { settings colors { id name description representations { rgba{name value{red green blue alpha}} hex{name value} cmyk{name value{cyan magenta yellow black}} pantone{name value} pantoneCoated{name value} pantoneUncoated{name value} } } }`. `colors` is a plain list: adding `items { }` gives HTTP 422. `settings` carries the block `view` and `enabledRepresentations`. `brands { essentials { colorPalettes } }` returns 0 palettes, so read the page blocks instead. Colour blocks are their own type, not `GuidelinePageBlock`: `get_page_structure` lists them as `ColorBlock`. A block that is only a *reference* to another page’s colour block is not followed: read the source page. |
| Create **text** — use the current **Text** block (app `2044620`) | **Personal token** REST → `create_marketplace_block(section_id, 2044620, after, {"columnNumber":"1","isColumnGutterCustom":False,"columnGutterSimple":"Auto","content": <Slate JSON string>})` | **Default for all new text** (Javier, 8 Oct 2026). Content format below. |
| Create **native text** block (shows as **“Text (legacy)”** in the editor) | **Personal token** REST → `create_native_text_block` (HTML: h2/h3/p/strong/em/ol/ul/li/a) | **Refused since autumn 2026** (400, checked 2 Nov 2026). Existing legacy blocks can still be edited. |
| Create **marketplace** block, old REST route (prefer `create_block`) | **Personal token** REST → `create_marketplace_block(section_id, app_id, after_section_element_id, initial_settings)` | The trick: create body must use `presets:{}`, NOT `settings` (settings-on-create → 500). Real settings go in a 2nd `update_block_settings` call (the wrapper does both). **Exception — Callout (`1190955`) and Divider (`405579`) 500 with `presets:{}`:** POST `/api/document-block` yourself with `presets` = the full settings of an existing block of that type, then `update_block_settings` (verified 8 Oct 2026). |
| **Create any block with its settings** (image, text, callout, divider, any app) — **the default** | **Personal token**, public `/graphql` (beta header) `createGuidelinePageBlock` → `create_block(section_id, "image"/"text"/"callout"/"divider" or a type id, FULL settings, after_block_id/after_heading_id)` | One call, settings validated against the block type's schema (errors name the missing keys). Block types are app ids like `cldju6bkp0001a8w43x1fgzzu` (image), read with `block_type_of(block_id)`, not the REST `marketplace_app_id`. Copy settings from an existing block with `get_block`; read-only keys Frontify names (a divider's `color`) are dropped and reported. Image blocks start without a picture → `set_block_image`. Verified 22 Oct 2026. |
| Create a block by **copying** an existing one (fallback) | **Personal token** REST `POST /api/document-block/{source_id}/copy` `{"target_section_id": S, "after_section_element_id": E}` → `copy_block` | Fallback if `create_block` ever fails: copies a block of the same app (REST `POST /api/document-block` 500s for image, text, divider and callout since Oct 2026). Then `update_block_settings` with the FULL settings (text, alt, caption…). The copy is independent, not a reference. Response `data.section_element_id` chains the next block. See *Creating blocks by copying* below. |
| Set the picture on an **image block** | **Personal token** REST `POST /api/document-block/{id}/asset/image` `{"asset_ids":[A]}` → `set_block_image` | POST **adds**, it doesn't replace. `GET /api/document-block/{id}/asset` lists them under `data.image`; `DELETE …/asset/image` `{"asset_ids":[old]}` removes. `set_block_image` does all three and checks only the new one is left. Upload first with `upload_asset`. **Shared page uploads:** it refuses to put a page upload (an image uploaded in the editor, project `200296`) on a second block, or to remove one from a block, because removing it deletes it everywhere. Deleting a block does not delete its image; `copy_block` gives the copy its own duplicate and now removes it, so a copied image block starts empty. Pass `allow_page_upload_change=True` only after checking no other block shows that image. Whether the editor’s 60-day restore brings a deleted image back is untested. |
| **Replace an asset's file in place** (re-rendered image, updated PDF) | **Personal token** public `/graphql` `uploadFile` + `replaceAsset` → `replace_asset(asset_id, file_path)` | Same asset id, so every block showing it updates; no block edits needed. Verified 22 Oct 2026. Prefer it to uploading a new asset when a file changes. |
| Update **marketplace** block settings | **Personal token** REST `POST /api/document-block/{id}` body `{"settings": {...}}` → `update_block_settings` | Send the FULL settings object, not a partial — server merges but partial-only can 500. |
| Create **block reference** (reuse, don't duplicate) | **Personal token** REST `POST /api/document-block-reference/{source_id}` → `create_reference` | Pass `target_section_id` + optional `after_section_element_id` to control order. |
| Delete block | **Personal token** REST `DELETE /api/document-block/{id}` → `delete_block(force=True)` | |
| Unpublish / hide a page | **Personal token** REST `PATCH /api/document-page/{id}` (`visibility:"EDITOR"`) → `unpublish_page` | |
| Footer show/hide | **Personal token** REST → `hide_footer`/`show_footer` (cover-page `footerVisibility`) | Inner-page footer lives in `template-theme-settings.documentPage.footerVisibility`. As of May 2026 it's correctly `"hide"` for doc pages, `"show"` on cover. If user "sees a footer on inner pages" it's almost always **browser cache** (hard-refresh) — the DOM `<footer>` is `tw-hidden`. |
| Create **section**, **heading**; rename heading; delete section | **Personal token**, public `/graphql` with header `X-Frontify-Beta: enabled` → `create_section(page_id, after_section_id)`, `create_heading(section_id, title, after_block_id/after_heading_id)`, `update_heading_title`, `delete_section(page_id, section_id)` | **No Chrome since Oct 2026** (verified 22 Oct on test page 4243581). Without the beta header these aren't reachable; `/graphql-internal` still 403s for the token. Inputs take plain numeric page/section ids; `afterElementId` takes the opaque id of the heading or block to follow (the tools build it). `delete_section` deletes the blocks first: deleting only the section leaves orphan blocks. |
| Update most **native** block settings (text, callout, color) | **Personal token** REST `POST /api/document-block/{id}` `{"settings":{...}}` | Body is a REPLACE — send full settings, omit `project` (auto-set; including it 500s). `update_block_settings` now removes it for you. |
| Update the native **`imagegrid`** block (columns / assets) | **NO working path found** — personal-token REST 500s on every `columns` value, `updateGuidelinePageBlockSettings` (Beta) → "Internal server error", no other mutation. **Only the Frontify editor UI works** (the `assets[]` array seems to break server-side validation on partial saves). Ask the person to set columns in the editor; give them the block IDs. |
| **Move a page**, also into a navigation section or another document | **Personal token**, public `/graphql` (beta header) → `move_page(page_id, document_id=… or category_id=…, sort=…)` | Keeps its permanent link and published state. The address with the document id and slug changes, so search the site for links to the old one. Verified Oct and 2 Nov 2026. |
| Create a **navigation section** or a **menu link** | **Personal token** → `create_nav_section(document_id, title)`, `create_nav_link(title, url, document_id=… or category_id=…)` | A new section lands at the bottom of the menu. |
| **Reorder navigation sections** | **No API.** The person drags it in the editor. | |
| Delete a heading | **Personal token** → `delete_heading(heading_id)` | |
| Delete a **block reference** (a shared copy) | **No API.** In the editor: click plain body text in the block to select it, then the trash in the block toolbar, not the section toolbar. | Clicking a reference’s “Text” label jumps to its source page. So add a reference only once the person has approved it. |
| Change the picture on an **annotated image** (native `annotations` block) | **Settings can’t be written** (500 for any settings, checked 2 Nov 2026). `replace_asset(asset_id, file_path)` swaps the file. | Labels stay where they were: if the layout changed, the person moves them in the editor. |

**Native text blocks — keep `class="link"` on anchors.** Frontify's inline link
styling comes from that class. Rewrite a paragraph without it and the links render
as grey chips/buttons rather than text links — the page still works, so it is easy
to ship without noticing. `class` is *not* stripped (an older note here claimed it
was; that was wrong and caused exactly this on the GHO page, Aug 2026). The full
anchor Frontify itself writes is:

```html
<a class="link" href="URL" data-tooltip-link-label="undefined" target="_blank">LABEL</a>
```

When updating an existing text block, read its HTML first and change only the
hrefs — do not re-author the markup from scratch.

**Text block (`2044620`) content = a Slate JSON *string*.** Node types seen on the portal:
`{"type":"p","children":[{"text":"…","bold":true}]}`, `{"type":"heading3","align":"left","children":[…]}`
(a subtitle; heading1–4 follow the same pattern), lists `{"type":"ul"|"ol","children":[{"type":"li","children":[{"type":"lic","children":[…text…]}]}]}`,
links `{"type":"a","url":"…","target":"_blank","children":[{"text":"…"}]}`. Callout text (`textValue`) uses the
same Slate format. When editing an existing block, read its JSON and change only what you need.

**Placement — read before creating anything.** A block created WITHOUT `after_section_element_id` lands
at the **TOP** of its section (above the heading), not the end. To place it, pass the section element
id of the element before it: a block's is `get_block(id)["section_element_id"]`; a **heading's** comes from
the internal GraphQL read (personal token works): `GuidelinePageHeading { id title sectionElementId }`.
Chain new blocks by passing each new block's returned `section_element_id` to the next. There is no
move API: to reorder, recreate in the right place, then delete the old copy.

**Building a page section (October 2026 method, no Chrome).**

1. `create_section(page_id, after_section_id)`, then `create_heading(section_id, title)`.
2. For each block: read the settings of an existing block of the same type (`get_block`), change
   what you need, `create_block(section_id, type, settings, after_heading_id=… / after_block_id=…)`.
   Chain by passing the previous block's id.
3. Image blocks: `upload_asset`, then `set_block_image(block_id, asset_id)`. When the image
   changes later, `replace_asset` keeps the same asset and every block updates. Moving a tested
   block to the live page: upload the image again for the live block, never reuse the test
   block’s upload, so deleting the test section can’t blank the live page.
4. Test on the hidden page `4243581` (“Test page from Claude MCP”) first; clean up with
   `delete_section(4243581, section_id)`. Editors open it at
   https://brand.unocha.org/r/Llm0vdxRniA49vWEWfgB3NudzhchT-MpOIhj4HxggfM (the document
   “TEST — Claude MCP integration”, editors only; pick the page in its sidebar). Always
   give this link, never a guessed one. Draft there, show the person, publish live on their “publish”.
   Separators: a dashed divider on each side of a new strip inside a section.

If `create_block` fails, fall back to `copy_block` (copy an existing block of the same app, then
`update_block_settings` and `set_block_image`). Known sources: image `11099595`, callout `11360197`,
divider `12145885`, text `12099207`. The “Numbers in graphics” page (`4249885`) was built that way.

**In the public API but not tested yet** (introspected 22 Oct 2026; try on the test page before
relying on them): `updateGuidelinePageBlockSettings` with the beta header — may fix the image-grid row;
`updateGuidelinePageSection` (section label, padding, border); brand-essentials colour
mutations (`createBrandEssentialsColor`, `addBrandEssentialsColorBlockColors`…) — may replace
the Chrome palette **write** tools (colour **reads** already work through the API: see the
“Read colour swatches” row). List them all with an introspection query on `/graphql` (beta header).

**Frontify’s official MCP** (`https://mcp.frontify-integrations.com/mcp`, tool packs listed at
`https://mcp.frontify-integrations.com/`): beta, OAuth, and Frontify must switch it on for the
account (ask the CSM; until then the connector says “Invalid Oauth Client”). Its guideline tools
only read (`list_guidelines`, `get_guideline_page` as Markdown); its strengths are assets
(search, metadata, comments, targets, collections), creative templates and brand-essentials
reads. Use it for those once enabled; use our server for anything that changes the brand site.

**Dividers:** change the style with `update_block_settings(id, {"style": "Dashed"})` only — touching
`isLine` 500s. House convention (Javier, 8 Oct 2026): **dashed** between subsections inside a section,
**solid** between the page's main sections.

**Showing a font: use the Font preview block, not Frontify’s old `typostyles` / `typofonts` blocks.** It shows the live font with every weight, and links to its Google Fonts page. Pages built before May 2026 may still have the old ones. To swap: `create_reference(source_id, target_section_id=…, after_section_element_id=…)` from the matching block on the Fonts page (Roboto `12103432`, Roboto Condensed `12107638`, Roboto Slab `12107636`, Roboto Mono `12107637`, Crimson Pro `12107635`), then `delete_block` on the old one. A reference stays in step with the Fonts page, but can only be removed in the editor, so show the plan first. For a different setup on one page, `copy_block` a Font preview block and change `googleFontsUrl`, `weights` and `showItalic` with `update_block_settings` (rehearsed 2 Nov 2026). Old blocks can hold sizes and sample text the new one doesn’t show: point those out before deleting.

## Custom blocks BDU built

BDU built three content blocks of its own for the brand site. They are installed on our Frontify,
so **anyone who can edit pages there finds them in the editor’s block list** (**+ Block**, then
the name below), next to Frontify’s own blocks. Nothing to install per person. Visitors only see
the result. Changing a block’s code is a different job: it needs Node 22 and the Frontify
developer login, and each block’s README in its source folder has the steps.

| In the editor | What it’s for | How to add one |
|---|---|---|
| **Font preview** (app `3306772`) | Shows a live Google Font with every weight it has, with a link to its Google Fonts page. Use it for every font on the site, never the old Frontify `typostyles` / `typofonts` blocks or a screenshot. | **Editor:** + Block → Font preview → **Change font** → type the font’s name and pick it. Sample text and italics are in the block’s sidebar. **Claude:** reuse a block from the Fonts page (*Showing a font*, just above). |
| **AI prompt** (app `3307325`) | A copy button that puts a ready-made prompt on the clipboard, optionally with a Humanitarian Icon, title, description and examples. Used on the “Working with AI” page. | **Editor:** + Block → AI prompt, then fill the sidebar. The prompt texts have one source, `AI_skills_and_prompts/ocha_general/M365_Copilot_Brand_Kit/prompts/`: change them there, not in the block. |
| **Useful links** (app `3596056`) | The grey band of links at the bottom of key pages, standing in for the footer Frontify shows only on the cover page. | **Never a new one.** There is one source block, `12148723` on the Visual Identity overview; every other page shows it as a reference: `create_reference(12148723, <last section id>, <section_element_id of that section’s last element>)` (without the last argument it lands at the top). Edit the links in the source block only; deleting it empties every page. |

Source folders: Font preview and Useful links in `Brand portal/2026/font-preview/` and
`Brand portal/2026/useful-links-block/`; AI prompt in
`AI_skills_and_prompts/ocha_general/copy-prompt-block/`.

**Claude can’t create a custom block from nothing** (the API answers “This block type cannot be
created via the API”). Reuse an existing one with `create_reference` (stays in step with the
source) or `copy_block` (an independent copy, then `update_block_settings`). If neither fits,
ask the person to add it in the editor and give them the page and position. A new custom app
must be installed first (its Marketplace page → **Install in guidelines**) before the editor
offers it.

Frontify’s own block ids: image = `2044618`, text = `2044620`, divider = `405579`. Image block `ratio` valid values are ONLY `"1:1"`, `"1:2"`, `"2:1"` — anything else (1:3, 2:3, 3:1…) 500s. The rightmost / smallest-image option in the UI = **`"1:2"`**.

## Logos and templates: a Dropbox link, not an upload

**BDU doesn’t upload logos or templates to Frontify** (Javier, 26 Nov 2026). They stay in the BDU
Dropbox, and the page gets a public Dropbox link to the file or folder. When a logo or template
changes, BDU updates it in Dropbox and the page needs no edit, because the link stays the same.
An upload would have to be replaced on Frontify by hand each time, and an old copy would keep
circulating.

- **Make the link with the `ocha-bdu-dropbox-links` skill.** It makes a truly public link that
  people outside OCHA can open. Never use the Dropbox connector’s `create_shared_link`: it makes a
  team-only link. If the person hasn’t connected their own Dropbox yet, suggest the one-time setup
  in that skill (a few minutes, done once) before going on.
- **Use the download version of the link** (`dl=1`, the Dropbox skill’s `--download` option) for
  logos and templates, so a click downloads the file straight away. The `dl=0` version opens
  Dropbox’s preview page instead. On a folder link, `dl=1` downloads the whole folder as a zip.
- **Updating a file keeps its link only when it is saved over the old one**, with the same name in
  the same folder. Moving, renaming, or deleting it and adding a new file breaks the link on the
  page. Say so when someone asks how to update a logo or template.
- **Link a folder** when a set of files changes over time (a logo pack, a template family): new
  files then appear without touching the page.
- Images shown on the page itself (pictures, examples, screenshots) are still uploaded as before.

## Links, text encoding and Chrome

**Links: always the permanent link** (Javier, 19 Nov 2026). Any link to a brand-site page, in a footer, block, callout or text, uses the page’s permanent link (`https://brand.unocha.org/r/…`), never the `/document/<id>#/<slug>` address someone pasted. The permanent link survives renames and moves. Get it with `list_pages(document_id)` or `get_page(page_id)` (`permanent_link`). Two pages can share a title (e.g. “This is OCHA” 3502611 and 4141374): match the pasted slug before choosing. Exception: a link to a section inside a page (no permanent link exists for sections) uses the section address, e.g. the footer’s “Frequently asked questions” → `/document/281801#/overview/visual-identity/frequently-asked-questions`; check it still works when that page is renamed or moved.

**Encoding gotcha:** the Frontify code-block widget mis-decodes UTF-8 → keep custom-block content ASCII-only. SVG uploads work where PNG `file_upload` is blocked by CSP.

**Chrome usage:** since October 2026 no brand-site page edit needs Chrome: sections and headings go through the public API. Reading colour swatches needs no Chrome either (`get_page_colors`, 29 Oct 2026). Chrome is left only for the palette **write** tools (`add_color_to_palette_via_chrome`, `copy_palette_contents_via_chrome`), as a fallback until the public colour mutations are tested. The remaining editor-only jobs (reordering navigation sections, removing references, image-grid columns, moving annotation labels): give the person the IDs and the steps, not a silent Chrome fallback.

## Project Owner

Javier Cueto, Head of Brand and Design Unit

## Maintained by

**OCHA Brand and Design Unit (BDU)**
- Team: ochavisual@un.org
- Focal point: Javier Cueto (cuetoj@un.org)

<!-- bdu-suggest-change:start -->
**Suggesting a change to this skill.** If the person corrects you or states a rule that would apply to other jobs too, or you find this skill is wrong or missing something, say so once, at the end of your reply. Don’t do this for changes that only concern the current job, and don’t edit the skill yourself, because the next update would overwrite it. Leave out anything confidential from the job. Say:

> This could be worth adding to the OCHA BDU skills. If you agree, copy this message and send it to Javi:
> **Skill:** ocha-bdu-frontify
> **Proposed rule:** [the rule, in one or two sentences]
> **Why:** [what happened, with one example]
<!-- bdu-suggest-change:end -->
