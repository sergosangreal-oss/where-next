# Where Next — current status

The website is prepared for GitHub Pages. Netlify and the Eurodesk-specific server function have been removed from this delivery.

## What is ready

- English-language responsive static site.
- GitHub Actions workflow that publishes the `site/` folder to GitHub Pages on each push to `main` or on manual run.
- Matcher reads a static JSON catalog from `site/data/opportunities.json`.
- The empty-catalog and load-error states point visitors to official directories instead of showing demo listings as current opportunities.

## What remains before public launch

The repository must be created under an authenticated GitHub account, then the site files uploaded and GitHub Pages enabled with **GitHub Actions**. The current browser is signed out of GitHub, so the owner needs to sign in there manually; never send passwords or verification codes in chat.

## Data limitations

There is no single public database containing all international youth programs. The catalog currently has no live entries and there is no scheduled data refresh yet. A source should be connected only after its API/feed access, reuse permission, schema, and update terms have been verified. GitHub Pages is static hosting, not a database. The form performs matching in the visitor's browser and does not store profile data.
