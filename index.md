---
layout: default
title: Turn a CSV into a shareable web page with Python
---

# Turn a CSV into a shareable web page with Python

Most data jobs end with a CSV that someone else needs to look at. Emailing the file works, but a link that opens as a readable table in any browser is nicer, and it is easy to get from a short Python script with no dependencies.

This walkthrough turns a CSV into a small HTML page and publishes it to a permanent HTTPS URL on [deed.page](https://deed.page) with a single PUT request. No account or sign-up step is involved.

## The script

Save this as `csv2page.py`:

```python
import csv, html, sys, json, urllib.request, pathlib

src, slug, title = sys.argv[1], sys.argv[2], sys.argv[3]
rows = list(csv.reader(open(src, newline="")))
head, body = rows[0], rows[1:]

th = "".join(f"<th>{html.escape(c)}</th>" for c in head)
tr = "".join("<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in r) + "</tr>" for r in body)
page = f"""<!doctype html><meta charset="utf-8">
<meta name="viewport" content="width=device-width">
<title>{html.escape(title)}</title>
<style>body{{font:15px system-ui;margin:2rem}}table{{border-collapse:collapse}}
td,th{{border:1px solid #ccc;padding:.4rem .7rem}}th{{background:#f4f4f4}}</style>
<h1>{html.escape(title)}</h1><table><tr>{th}</tr>{tr}</table>"""

tok_file = pathlib.Path.home() / ".config/deed-page/token"
headers = {"Content-Type": "text/html", "X-Client": "csv2page"}
if tok_file.exists():
    headers["Authorization"] = "Bearer " + tok_file.read_text().strip()

req = urllib.request.Request(f"https://deed.page/v1/sites?slug={slug}",
                             data=page.encode(), method="PUT", headers=headers)
resp = json.load(urllib.request.urlopen(req))

tok = resp.pop("token", None)
if tok:  # only the first publish returns a token
    tok_file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tok_file.write_text(tok)
    tok_file.chmod(0o600)

print(resp["url"])
```

## Run it

```bash
printf 'region,orders,revenue\nNorth,42,1260\nSouth,35,1015\n' > sales.csv
python3 csv2page.py sales.csv weekly-sales-7f3k "Weekly sales"
```

It prints something like `https://weekly-sales-7f3k.deed.page/`. Pick your own slug; short generic ones such as `my-page` are reserved, so add a random suffix.

## Updating the same link

The first publish returns an owner token, which the script writes to `~/.config/deed-page/token` with mode 600 and never prints. Every later run sends it as a Bearer header, so running the script again with the same slug replaces the page in place and the URL you shared keeps working. That makes it a good fit for a cron job that refreshes a report every morning.

Keep that token out of logs, repositories and chat transcripts. If you hand the script to an AI agent, let the script read the token file itself rather than pasting the token into the prompt, and have the agent show you a preview and ask before publishing anything.

## Removing it

```bash
curl -X DELETE "https://deed.page/v1/sites/weekly-sales-7f3k" \
  -H "Authorization: Bearer $(cat ~/.config/deed-page/token)"
```

## Notes

- The free plan covers 25 sites, 25 MB per site and 60 publishes an hour, and free pages show a small badge in the corner. Details are on the [docs page](https://deed.page/docs).
- `html.escape` matters: CSV cells can contain `<` or `&`, and escaping keeps a stray value from breaking the page.
- The same request works from any language that can send an HTTP PUT. There is also an agent skill and plugin at [github.com/f-o-x11/deed-page-skill](https://github.com/f-o-x11/deed-page-skill) for Claude Code, Codex, Cursor and other agents.

Written by the deed.page team (Avatar 8 LLC).
