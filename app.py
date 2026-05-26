from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, abort, flash, redirect, render_template, request, send_from_directory, url_for

from site_builder import (
    build_site,
    collect_git_paths,
    commit_message_for,
    get_entry,
    load_entries,
    make_form_state,
    run_git_publish,
    save_entry,
    validate_form_data,
)


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "local-dev-secret")
ROOT = Path(__file__).resolve().parent

READING_TEMPLATE = """## Why this paper?
Why did I choose to read this paper? The source may be straightforward (for example, a class paper or professor recommendation) or more personally derived (for example, arXiv surfing or someone's reading list). I would like to add another line describing what I'd like to gain more insight on via this paper.

## Context
How did we get to this problem? In practice, this will likely be heavily drawn from the paper's related work section, but my own goal is to remind myself how this problem ties into other research. What was the state of affairs at the time of the paper's publication, and what gap is this paper zooming in on?

## Problem Statement
What is the problem? What's the contribution?

## Notes
Methods and results that stood out to me.

## Questions
What did I not understand? Will I address these gaps? If so, how? Also, what did I not understand initially, but then resolved? How did I arrive at the resolution?

## Looking Forward
Takeaways and free space for any additional thoughts. What are my conclusions, if any? Anything I can look into that might be worth trying?
"""


@app.route("/")
def root() -> str:
    return redirect(url_for("admin_index"))


@app.route("/assets/<path:filename>")
def assets(filename: str):
    return send_from_directory(ROOT / "assets", filename)


@app.route("/admin")
def admin_index() -> str:
    entries = load_entries()
    grouped = {
        "blog": [entry for entry in entries if entry.entry_type == "blog"],
        "reading": [entry for entry in entries if entry.entry_type == "reading"],
    }
    return render_template("admin/dashboard.html", grouped=grouped, title="Authoring Dashboard - James Z")


@app.route("/entries/new", methods=["GET", "POST"])
def create_entry() -> str:
    if request.method == "POST":
        return handle_save(None)

    form_state = make_form_state()
    requested_type = request.args.get("type", "").strip().lower()
    if requested_type in {"blog", "reading"}:
        form_state["entry_type"] = requested_type
    if requested_type == "reading":
        form_state["body_markdown"] = READING_TEMPLATE
    return render_template(
        "admin/form.html",
        form_state=form_state,
        original_entry=None,
        title="Create Entry - James Z",
        reading_template=READING_TEMPLATE,
    )


@app.route("/entries/<entry_type>/<slug>/edit", methods=["GET", "POST"])
def edit_entry(entry_type: str, slug: str) -> str:
    original_entry = get_entry(entry_type, slug)
    if original_entry is None:
        abort(404)

    if request.method == "POST":
        return handle_save(original_entry)

    return render_template(
        "admin/form.html",
        form_state=make_form_state(original_entry),
        original_entry=original_entry,
        title=f"Edit {original_entry.title} - James Z",
        reading_template=READING_TEMPLATE,
    )


def handle_save(original_entry):
    raw_form = {
        "entry_type": request.form.get("entry_type", ""),
        "title": request.form.get("title", ""),
        "slug": request.form.get("slug", ""),
        "summary": request.form.get("summary", ""),
        "published_on": request.form.get("published_on", ""),
        "body_markdown": request.form.get("body_markdown", ""),
    }

    try:
        clean_form = validate_form_data(raw_form)
        saved_entry = save_entry(
            original_type=original_entry.entry_type if original_entry else None,
            original_slug=original_entry.slug if original_entry else None,
            **clean_form,
        )
        build_site()

        git_result = run_git_publish(
            collect_git_paths(
                saved_entry,
                original_type=original_entry.entry_type if original_entry else None,
                original_slug=original_entry.slug if original_entry else None,
            ),
            commit_message_for(saved_entry, is_new=original_entry is None),
        )
        flash(git_result.summary, "success" if git_result.success else "error")
        if git_result.details:
            flash(git_result.details, "note")
        return redirect(url_for("edit_entry", entry_type=saved_entry.entry_type, slug=saved_entry.slug))
    except ValueError as error:
        flash(str(error), "error")
        fallback_entry = original_entry
        return (
            render_template(
                "admin/form.html",
                form_state=raw_form,
                original_entry=fallback_entry,
                title="Fix Entry - James Z",
                reading_template=READING_TEMPLATE,
            ),
            400,
        )


if __name__ == "__main__":
    build_site()
    app.run(debug=True)
