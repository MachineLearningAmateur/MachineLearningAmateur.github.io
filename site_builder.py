from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from html import escape
from pathlib import Path
from typing import Iterable
import math
import re
import subprocess

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape


ROOT = Path(__file__).resolve().parent
CONTENT_ROOT = ROOT / "content"
TEMPLATE_ROOT = ROOT / "templates"
SITE_SECTIONS = ("blog", "reading")
WORDS_PER_MINUTE = 220


@dataclass(frozen=True)
class Entry:
    entry_type: str
    title: str
    slug: str
    summary: str
    published_on: date
    body_markdown: str
    body_html: str
    read_minutes: int
    source_path: Path

    @property
    def output_dir(self) -> Path:
        return ROOT / self.entry_type / self.slug

    @property
    def output_path(self) -> Path:
        return self.output_dir / "index.html"

    @property
    def display_date(self) -> str:
        return self.published_on.isoformat()

    @property
    def display_date_long(self) -> str:
        return self.published_on.strftime("%B %d, %Y")

    @property
    def section_label(self) -> str:
        return "Blog" if self.entry_type == "blog" else "Reading"


@dataclass(frozen=True)
class GitResult:
    success: bool
    summary: str
    details: str = ""


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "untitled-entry"


def estimate_read_time(text: str) -> int:
    words = re.findall(r"\b[\w'-]+\b", text)
    return max(1, math.ceil(len(words) / WORDS_PER_MINUTE))


def split_front_matter(raw: str) -> tuple[dict[str, object], str]:
    normalized = raw.replace("\r\n", "\n")

    if not normalized.startswith("---\n"):
        raise ValueError("Markdown file is missing YAML front matter.")

    closing_marker = normalized.find("\n---\n", 4)

    if closing_marker == -1:
        raise ValueError("Markdown file has an unterminated YAML front matter block.")

    metadata_text = normalized[4:closing_marker]
    body = normalized[closing_marker + 5 :].lstrip("\n")
    metadata = yaml.safe_load(metadata_text) or {}
    return metadata, body


def render_inline_markdown(text: str) -> str:
    escaped = escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    return escaped


def markdown_to_html(markdown_text: str) -> str:
    lines = markdown_text.replace("\r\n", "\n").split("\n")
    blocks: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    in_code_block = False
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            joined = " ".join(part.strip() for part in paragraph if part.strip())
            if joined:
                blocks.append(f"<p>{render_inline_markdown(joined)}</p>")
        paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            items = "".join(f"<li>{render_inline_markdown(item)}</li>" for item in list_items)
            blocks.append(f"<ul>{items}</ul>")
        list_items = []

    def flush_code_block() -> None:
        nonlocal code_lines
        code = "\n".join(code_lines)
        blocks.append(f"<pre><code>{escape(code)}</code></pre>")
        code_lines = []

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            if in_code_block:
                flush_code_block()
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(raw_line)
            continue

        if not stripped:
            flush_paragraph()
            flush_list()
            continue

        heading_match = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if heading_match:
            flush_paragraph()
            flush_list()
            level = len(heading_match.group(1))
            blocks.append(f"<h{level}>{render_inline_markdown(heading_match.group(2))}</h{level}>")
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            list_items.append(stripped[2:].strip())
            continue

        paragraph.append(stripped)

    if in_code_block:
        flush_code_block()

    flush_paragraph()
    flush_list()
    return "\n".join(blocks)


def parse_entry(path: Path) -> Entry:
    metadata, body = split_front_matter(path.read_text(encoding="utf-8"))
    entry_type = str(metadata.get("type", "")).strip().lower()
    title = str(metadata.get("title", "")).strip()
    summary = str(metadata.get("summary", "")).strip()
    slug = slugify(str(metadata.get("slug", title)).strip())
    published_on = date.fromisoformat(str(metadata.get("date", "")).strip())

    if entry_type not in SITE_SECTIONS:
        raise ValueError(f"{path} has an invalid type.")

    if not title or not summary:
        raise ValueError(f"{path} is missing required metadata.")

    cleaned_body = body.strip()
    return Entry(
        entry_type=entry_type,
        title=title,
        slug=slug,
        summary=summary,
        published_on=published_on,
        body_markdown=cleaned_body,
        body_html=markdown_to_html(cleaned_body),
        read_minutes=estimate_read_time(cleaned_body),
        source_path=path,
    )


def load_entries() -> list[Entry]:
    entries: list[Entry] = []

    for section in SITE_SECTIONS:
        section_dir = CONTENT_ROOT / section
        if not section_dir.exists():
            continue

        for path in sorted(section_dir.glob("*.md")):
            entries.append(parse_entry(path))

    return sorted(entries, key=lambda entry: (entry.published_on, entry.title.lower()), reverse=True)


def get_entry(entry_type: str, slug: str) -> Entry | None:
    for entry in load_entries():
        if entry.entry_type == entry_type and entry.slug == slug:
            return entry
    return None


def write_entry_file(
    *,
    entry_type: str,
    title: str,
    slug: str,
    summary: str,
    published_on: str,
    body_markdown: str,
) -> Path:
    section_dir = CONTENT_ROOT / entry_type
    section_dir.mkdir(parents=True, exist_ok=True)
    body = body_markdown.strip() + "\n"
    metadata = {
        "title": title,
        "slug": slug,
        "date": published_on,
        "summary": summary,
        "type": entry_type,
    }
    front_matter = yaml.safe_dump(metadata, sort_keys=False, allow_unicode=False).strip()
    payload = f"---\n{front_matter}\n---\n\n{body}"
    path = section_dir / f"{slug}.md"
    path.write_text(payload, encoding="utf-8")
    return path


def save_entry(
    *,
    original_type: str | None,
    original_slug: str | None,
    entry_type: str,
    title: str,
    slug: str,
    summary: str,
    published_on: str,
    body_markdown: str,
) -> Entry:
    old_source_path = None
    if original_type and original_slug:
        old_source_path = CONTENT_ROOT / original_type / f"{original_slug}.md"

    new_source_path = write_entry_file(
        entry_type=entry_type,
        title=title,
        slug=slug,
        summary=summary,
        published_on=published_on,
        body_markdown=body_markdown,
    )

    if old_source_path and old_source_path != new_source_path and old_source_path.exists():
        old_source_path.unlink()

    return parse_entry(new_source_path)


def build_environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATE_ROOT),
        autoescape=select_autoescape(("html", "xml")),
        keep_trailing_newline=True,
    )


def render_section_index(environment: Environment, section: str, entries: list[Entry]) -> None:
    template = environment.get_template("site/list.html")
    label = "Blog" if section == "blog" else "Reading"
    html = template.render(
        page_title=f"{label} - James Z",
        meta_description=f"{label} posts by James Z." if section == "blog" else "Reading notes and topics for James Z.",
        active_section=section,
        section_label=label,
        entries=entries,
        empty_message="No posts yet." if section == "blog" else "No reading notes yet.",
    )
    output_path = ROOT / section / "index.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def prune_stale_output(entries: Iterable[Entry]) -> None:
    active_paths = {entry.output_dir.resolve() for entry in entries}

    for section in SITE_SECTIONS:
        section_dir = ROOT / section
        if not section_dir.exists():
            continue

        for child in section_dir.iterdir():
            if child.name == "index.html" or not child.is_dir():
                continue

            if child.resolve() not in active_paths:
                for nested in child.rglob("*"):
                    if nested.is_file():
                        nested.unlink()
                for nested_dir in sorted((path for path in child.rglob("*") if path.is_dir()), reverse=True):
                    nested_dir.rmdir()
                child.rmdir()


def build_site() -> list[Entry]:
    entries = load_entries()
    environment = build_environment()
    prune_stale_output(entries)

    for section in SITE_SECTIONS:
        section_entries = [entry for entry in entries if entry.entry_type == section]
        render_section_index(environment, section, section_entries)

    post_template = environment.get_template("site/post.html")
    for entry in entries:
        html = post_template.render(
            page_title=f"{entry.title} - James Z",
            meta_description=entry.summary,
            active_section=entry.entry_type,
            entry=entry,
        )
        entry.output_dir.mkdir(parents=True, exist_ok=True)
        entry.output_path.write_text(html, encoding="utf-8")

    return entries


def collect_git_paths(entry: Entry, *, original_type: str | None, original_slug: str | None) -> list[Path]:
    paths = [
        ROOT / "blog" / "index.html",
        ROOT / "reading" / "index.html",
        entry.source_path,
        entry.output_path,
    ]

    if original_type and original_slug:
        old_source_path = CONTENT_ROOT / original_type / f"{original_slug}.md"
        old_output_path = ROOT / original_type / original_slug / "index.html"
        paths.extend((old_source_path, old_output_path))

    deduped: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        resolved = path.resolve()
        if resolved not in seen:
            deduped.append(path)
            seen.add(resolved)
    return deduped


def commit_message_for(entry: Entry, *, is_new: bool) -> str:
    noun = "blog post" if entry.entry_type == "blog" else "reading note"
    verb = "Add" if is_new else "Update"
    return f"{verb} {noun}: {entry.slug}"


def run_git_publish(paths: Iterable[Path], commit_message: str) -> GitResult:
    relative_paths = [str(path.relative_to(ROOT)) for path in paths]

    add_result = subprocess.run(
        ["git", "add", "-A", "--", *relative_paths],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if add_result.returncode != 0:
        details = "\n".join(part for part in (add_result.stdout.strip(), add_result.stderr.strip()) if part)
        return GitResult(False, "Saved locally, but git add failed.", details)

    staged_check = subprocess.run(
        ["git", "diff", "--cached", "--quiet", "--exit-code"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if staged_check.returncode == 0:
        return GitResult(True, "Saved locally. No staged changes were detected for commit.")

    commit_result = subprocess.run(
        ["git", "commit", "-m", commit_message],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if commit_result.returncode != 0:
        details = "\n".join(part for part in (commit_result.stdout.strip(), commit_result.stderr.strip()) if part)
        return GitResult(False, "Saved locally, but git commit failed.", details)

    push_result = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if push_result.returncode != 0:
        details = "\n".join(part for part in (push_result.stdout.strip(), push_result.stderr.strip()) if part)
        return GitResult(False, "Saved locally, but git push failed.", details)

    details = "\n".join(part for part in (commit_result.stdout.strip(), push_result.stdout.strip()) if part)
    return GitResult(True, "Saved, committed, and pushed successfully.", details)


def make_form_state(entry: Entry | None = None) -> dict[str, str]:
    if entry is None:
        return {
            "entry_type": "blog",
            "title": "",
            "slug": "",
            "summary": "",
            "published_on": date.today().isoformat(),
            "body_markdown": "",
        }

    return {
        "entry_type": entry.entry_type,
        "title": entry.title,
        "slug": entry.slug,
        "summary": entry.summary,
        "published_on": entry.published_on.isoformat(),
        "body_markdown": entry.body_markdown,
    }


def validate_form_data(form_data: dict[str, str]) -> dict[str, str]:
    entry_type = form_data.get("entry_type", "").strip().lower()
    title = form_data.get("title", "").strip()
    summary = form_data.get("summary", "").strip()
    body_markdown = form_data.get("body_markdown", "").strip()
    published_on = form_data.get("published_on", "").strip() or date.today().isoformat()
    slug_input = form_data.get("slug", "").strip() or title
    slug = slugify(slug_input)

    if entry_type not in SITE_SECTIONS:
        raise ValueError("Choose either Blog or Reading for the entry type.")
    if not title:
        raise ValueError("Title is required.")
    if not summary:
        raise ValueError("Summary is required.")
    if not body_markdown:
        raise ValueError("Body content is required.")

    try:
        datetime.strptime(published_on, "%Y-%m-%d")
    except ValueError as error:
        raise ValueError("Date must use YYYY-MM-DD.") from error

    return {
        "entry_type": entry_type,
        "title": title,
        "slug": slug,
        "summary": summary,
        "published_on": published_on,
        "body_markdown": body_markdown,
    }


if __name__ == "__main__":
    built_entries = build_site()
    print(f"Built {len(built_entries)} entries.")
