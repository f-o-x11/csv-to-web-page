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
