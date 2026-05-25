# MachineLearningAmateur.github.io

Static root-site repository for `https://machinelearningamateur.github.io/`.

## Structure

- `index.html` is the homepage.
- `about/`, `projects/`, and `writing/` contain the public pages.
- `writing/<slug>/index.html` holds individual posts.
- `assets/css/site.css` contains the shared site styling.
- `assets/img/` contains lightweight local image assets.
- `404.html` is the GitHub Pages not-found page.
- `.nojekyll` tells GitHub Pages to serve the repo as-is.

## Local preview

Use any static file server from the repo root. Example:

```powershell
python -m http.server 8000
```

Then open `http://localhost:8000`.

## Editing model

- Add or update writing entries directly in `writing/index.html`.
- Create a new post by adding a new `writing/<slug>/index.html` file.
- Update featured project cards in `projects/index.html` and, if needed, the homepage.

## Publish

Push the `main` branch to the GitHub repository named `MachineLearningAmateur.github.io`.
