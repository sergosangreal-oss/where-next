# Where Next

Where Next helps young people explore international exchanges, summer schools, volunteering, scholarships, and other opportunities.

## Live site

https://sergosangreal-oss.github.io/where-next/

## Current data status

- `site/data/sources.json` contains 51 official source directories and program pages from governments, universities, and international organizations.
- `scripts/check_sources.py` checks whether each registered source website responds. The `Refresh official source status` GitHub Actions workflow is scheduled daily and can also be run manually.
- The source register is not the same as 51 machine-readable database integrations. Many providers publish web pages without a public API or feed.
- The matcher reads `site/data/opportunities.json`. It currently has no synchronized opportunity records. Do not treat the source directory as proof that a program is currently open or that a person is eligible.
- User profile matching happens in the browser; the site does not store age, residence, citizenship, or budget.

## Deployment

GitHub Pages publishes the `site/` directory when a commit is pushed to `main`. The workflow is in `.github/workflows/pages.yml`.

## Adding a real data connector

Before ingesting listings, confirm that the provider publishes a machine-readable API/feed and permits reuse. Preserve each listing's original URL, source name, last-checked time, eligibility evidence, currency, and deadline. Leave unknown fields unset and do not recommend listings whose eligibility cannot be checked.
