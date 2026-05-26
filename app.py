from __future__ import annotations

import os

from flask import Flask, abort, flash, redirect, render_template, request, url_for

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


@app.route("/")
def root() -> str:
    return redirect(url_for("admin_index"))


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
    return render_template(
        "admin/form.html",
        form_state=form_state,
        original_entry=None,
        title="Create Entry - James Z",
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
            ),
            400,
        )


if __name__ == "__main__":
    build_site()
    app.run(debug=True)
