#!/usr/bin/env python3
import os, re, glob, pathlib, datetime, frontmatter, yaml

REPO = pathlib.Path(__file__).resolve().parents[1]
ENTRIES = REPO / "entries"
README = REPO / "README.md"

def shields_badge(tag: str) -> str:
    safe = tag.replace(" ", "%20")
    return f"![{tag}](https://img.shields.io/badge/{safe}-black)"

def ensure_pretty(md_path: pathlib.Path):
    """
    If `md_path` has YAML front matter and no corresponding __pretty.md,
    create/refresh the pretty file next to it.
    """
    if md_path.name.endswith("__pretty.md"):
        return

    try:
        post = frontmatter.load(md_path)
    except Exception:
        return  # skip non-frontmatter files

    meta = post.metadata or {}
    ts = str(meta.get("date") or "")
    _id = str(meta.get("id") or "")
    author = str(meta.get("author") or "")
    agent = str(meta.get("agent") or "")
    project = str(meta.get("project") or "")
    tags = meta.get("tags") or []
    if isinstance(tags, str):
        # allow "a, b, c"
        tags = [t.strip() for t in tags.split(",") if t.strip()]

    # badges
    badge_line = " ".join(shields_badge(t) for t in tags)

    pretty_name = md_path.with_name(md_path.stem + "__pretty.md")
    body = f"""# 📝 Chat Summary — {ts}

{badge_line}

| 🆔 id | 📅 date | ✍️ author | 🤖 agent | 📁 project |
|---|---|---|---|---|
| `{_id}` | `{ts}` | **{author}** | **{agent}** | **{project}** |

---

> **Context**  
> (short context — edit as needed)

## Highlights
- (summarize key points here)

<details>
<summary><strong>Raw Notes</strong></summary>

{post.content.strip() or "(add details as needed)"}
</details>

## Decisions / Next Actions
- [ ] next step 1
- [ ] next step 2
"""

    # Only write if new or contents changed
    old = pretty_name.read_text(encoding="utf-8") if pretty_name.exists() else None
    if old != body:
        pretty_name.write_text(body, encoding="utf-8")

def build_index():
    files = sorted(glob.glob(str(ENTRIES / "*" / "*.md")))
    # exclude __pretty.md from the index (we link to source files)
    files = [f for f in files if not f.endswith("__pretty.md")]

    # Group by YYYY-MM from filename prefix
    groups = {}
    for p in files:
        base = os.path.basename(p)
        month = base[:7] if re.match(r"^\d{4}-\d{2}-", base) else "unsorted"
        groups.setdefault(month, []).append(base)

    lines = ["# Journal Index\n"]
    for month in sorted(groups.keys(), reverse=True):
        lines.append(f"## {month}")
        for base in sorted(groups[month], reverse=True):
            rel = os.path.join("entries", base[:4], base)
            lines.append(f"- [{base}]({rel})")
        lines.append("")  # blank line

    README.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")

def main():
    if not ENTRIES.exists():
        print("No entries/ directory yet. Skipping.")
        return
    for year_dir in sorted(ENTRIES.glob("*")):
        if not year_dir.is_dir():
            continue
        for md in year_dir.glob("*.md"):
            ensure_pretty(md)
    build_index()

if __name__ == "__main__":
    main()
