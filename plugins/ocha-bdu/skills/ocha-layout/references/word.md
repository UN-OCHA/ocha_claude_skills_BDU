# Word guide

**Simple beats good-looking.** People using Word are rarely designers, and many hands edit the file.
Before adding a style, table or layout trick, ask whether a country office could break it.

## Template rules

- **No columns:** text runs full width.
- **Fewer styles, simpler tables.** Every style starts with the template’s prefix, to tell it apart from
  Word’s own.
- **Fonts:** Arial by default, so there’s nothing to install. Roboto and other OCHA fonts can be fine,
  depending on who will use the template.
- **Instructions go only in Word comments,** and only on how to use the template, under one author name.
  They insist on styles over manual formatting and say where the styles are.
- **Tables only when really needed,** each explained in a comment. Charts side by side may go in a table.
- **Pictures stay “In line with text”.** Floating objects on the cover only. No text boxes.
- **No QR codes** by default: too complicated for most users. Exceptions are possible. Buttons stay, as
  pictures with a link.
- **Graphics:** SVG with outlined text and a PNG fallback, so no font is needed.
- **Plainer than InDesign on purpose:** for example one header bar rather than one colour per part, which
  would need a section per part.

## What breaks, and the fix

| Problem | Fix |
|---|---|
| Contents break on Windows regions that use a semicolon as separator | Build contents from outline levels (`\u`), not a style list (`\t`) |
| Word ignores “page break before” inside a table | Start the page with a plain paragraph (a “New page” style) |
| Tables can’t have outside spacing | A thin “Gap” paragraph above and below each table |
| Word adds 5.4 pt cell margins that clip pictures | Set cell margins on every table |
| A copied list continues its numbering | Type the numbers where a block will be copied |
| A heading pasted with destination styles becomes Word’s own Heading | Comments tell people to paste as text only |
| Endnotes land after the back matter | Give them their own section (end of section, not end of file) |
| A reused endnote id makes Word report the file as damaged | Give each reference its own id |
| Removing what’s outside a picture crop also removes text touching the edge | Add padding to crops |
| A title separates from its figures or map | “Keep with next” on the title |
| Colours in styles multiply the style count | Put key-figure colours on the figure |
| French Word drops accents on automatic capitals | Type real accented capitals |

## Testing

- **Test in real Windows Word,** with Word hidden, through a virtual machine. Word for Mac opens windows
  on the screen, and any dialog stalls it.
- Test real edits as well as the file opening: typing over figures, copying a block, changing a picture.
- **Saving can’t be tested by script:** a hidden Word fails to save even a blank document. Test by hand,
  and also Change Picture and how comments display.
- Contents page numbers come from Word itself: build, open in Word to read the page numbers, build again.
- A template build in Python keeps one set of scripts, with the language as a setting.
