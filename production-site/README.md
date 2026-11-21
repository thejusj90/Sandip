# Dīpātma production website

This is the Vercel project root for dipatmawellness.com. The source is the supplied Impact Advisory website package, with production metadata, bundled image assets and the existing enquiry email provider restored.

- Edit page and article Markdown in `content/`, and metadata in `content/seo-meta.json`.
- Edit templates in `generate.py` and presentation in `assets/`.
- Run `python3 build.py`; generated pages and images are written to `dist/`.
- `vercel.json` serves those individual pages and retains the previous-domain redirects.
- Enquiries use the previously configured FormSubmit route to wellnesswithsandip@gmail.com. Domain activation and inbox delivery require a real submission check; an HTTP success alone does not verify inbox receipt.

The supplied photographs are illustrative. They are not presented as photographs of Dīpātma client projects.

## Release checks

Use Python 3.12 or newer to build from `production-site/`. The editable Markdown, generator and assets are the deployment source. The old compressed single-page bundle is obsolete. A release should build 17 indexable content pages, two utility pages, and the 404 page. Check image URLs, canonical links, sitemap, sector preselection and the optional project details disclosure.

The initial enquiry requires name, email, message and privacy acknowledgement. Optional project details open automatically for sector-specific enquiry links. Do not claim inbox delivery without checking a real submission with the mailbox owner.
