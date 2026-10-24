# Deployment and data status

The public site is https://sergosangreal-oss.github.io/where-next/ and the public repository is https://github.com/sergosangreal-oss/where-next.

GitHub Pages deploys the `site/` folder on every push to `main`. The daily `Refresh official source status` workflow checks the registered official websites and updates `site/data/source-health.json` when a run succeeds.

`site/data/sources.json` is a directory of 51 official source pages. Only sources with a documented, reusable public API or feed should be counted as automated data integrations. At present, 51 does not mean 51 databases are connected. `site/data/opportunities.json` has no live opportunity records and there is no scheduled opportunity-feed ingestion yet.

GitHub Pages is static hosting, not a database or backend. The user's profile is matched locally in their browser and is not sent to a server. Every listing added later must preserve provenance and should be checked against the organizer's current eligibility, dates, and costs.
