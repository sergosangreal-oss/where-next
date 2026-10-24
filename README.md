# Where Next

Where Next helps young people discover exchanges, summer schools, volunteering projects, scholarships, and other international opportunities.

## Publish with GitHub Pages

1. Create a public GitHub repository named `where-next` and upload the **contents** of this folder (including the hidden `.github` folder).
2. In the repository, open **Settings → Pages** and choose **GitHub Actions** as the build and deployment source.
3. Push a commit to the `main` branch, or run **Publish site to GitHub Pages** from the Actions tab.
4. GitHub will show the public website URL under **Settings → Pages** after the workflow succeeds.

The site is static and does not require an API key. Its matcher reads `site/data/opportunities.json`. The file is deliberately empty until source feeds with confirmed public access and reliable eligibility fields are added. The site links to official directories in the meantime; it does not present invented or stale records as live listings.

## Catalog source requirements

For each source, confirm its terms permit reuse, a public API or feed exists, refresh limits, and which fields are exposed. A scheduled GitHub Actions job can refresh the JSON file only after those details are established. GitHub Pages publishes static files; it is not a relational database.
