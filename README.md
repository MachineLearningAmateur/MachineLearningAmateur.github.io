# MachineLearningAmateur.github.io

This is the source for my personal site at `https://machinelearningamateur.github.io/`.

The public site is intentionally simple:

- the homepage introduces me
- the blog holds short posts and updates
- the reading page tracks notes and things I want to revisit

The content is generated from Markdown source files, and a local Flask admin UI lets me add or edit entries without hand-writing the public HTML every time.

## What Lives Here

- `index.html` is the homepage.
- `blog/` contains the generated blog index and individual posts.
- `reading/` contains the generated reading index and individual notes.
- `content/blog/` contains Markdown source files for blog posts.
- `content/reading/` contains Markdown source files for reading notes.
- `templates/site/` contains the shared public-page templates used by the static generator.
- `templates/admin/` contains the local Flask authoring UI.
- `app.py` runs the local authoring server.
- `site_builder.py` renders the static HTML pages from Markdown content.
- `assets/css/site.css` contains the shared site styling.
- `404.html` is the GitHub Pages not-found page.
- `.nojekyll` tells GitHub Pages to serve the repo as-is.

## Local authoring UI

Install the Python dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run the Flask app from the repo root:

```powershell
python app.py
```

Then open `http://127.0.0.1:5000/admin`.

The UI lets you:

- create new blog posts
- create new reading notes
- edit existing entries
- write content in Markdown
- auto-fill dates for new entries
- regenerate the static site on save
- attempt a git commit and push on save

## Content Model

Each entry is stored as a Markdown file with YAML front matter:

```md
---
title: Creating This Site
slug: creating-this-site
date: 2026-05-25
summary: A short note on why I decided to create this site.
type: blog
---

Markdown body content goes here.
```

Blog posts live under `content/blog/`. Reading notes live under `content/reading/`.

## Static Rebuild Without the UI

If you only want to regenerate the site from the current Markdown source:

```powershell
python site_builder.py
```

## Publish

The local authoring UI attempts to:

1. regenerate the affected static pages
2. stage the generated files plus the Markdown source file
3. create a git commit
4. push `main` to `origin`

If git push fails, the content and generated pages still remain saved locally.
