# Deadpan Status setup

## Deployment checkpoint — 2026-09-10

`GH_PAT` is configured. [Setup CI](https://github.com/timbueno/deadpan-status/actions/runs/34491647510)
and [Uptime CI](https://github.com/timbueno/deadpan-status/actions/runs/34491784376)
passed; both Leaf endpoints are up from GitHub runners. Setup CI also built and
published the site, creating `gh-pages`, so a separate initial Static Site CI run
was unnecessary. The generated page was previewed locally and successfully loaded
both services from the public repository.

GitHub Pages is configured to serve `gh-pages` at `/(root)` with custom domain
`status.deadpan.io`; its Pages deployment succeeded. Cloudflare has a DNS-only
CNAME `status` → `timbueno.github.io` (TTL 300). DNS propagation and GitHub
certificate provisioning remain pending; enable **Enforce HTTPS** when available
and verify the custom-domain page before marking launch complete.

## Automation credential

Create a fine-grained GitHub personal access token restricted to
`timbueno/deadpan-status`, with read/write Actions, Contents, Issues and Workflows
permissions (Metadata read access is implicit). Store it as the repository's
Actions secret `GH_PAT`. Set a reminder to renew it before expiry. Never put the
token in a file committed to this repository, an issue, or a workflow log.

Upptime passes `GH_PAT` separately from the `secrets: []` allowlist. Public checks
need no service credentials, Cloudflare token, or tailnet connection. The template
also supports GitHub App credentials, but a dedicated repository-scoped PAT is
the initial setup described here.

## Generate and verify

1. Enable GitHub Actions if prompted. After adding `GH_PAT`, push the configuration
   or manually run **Setup CI** from the default branch (`master`).
2. Confirm Setup CI succeeds and `history/summary.json` lists only `leaf-kosync`
   and `leaf-api`, with successful health checks. Setup regenerates workflows
   from `.upptimerc.yml`, including the empty contextual-secret allowlist.
3. Run **Static Site CI** from `master`. Its publishing action creates `gh-pages`
   if it was omitted when creating the repository from the template.
4. Run **Uptime CI** and check that both endpoints pass from the GitHub runner.
   Local probe success alone does not establish GitHub runner reachability.

The checks use HTTP 200 plus exact healthy-response fragments. KOSync sends
`Accept: application/vnd.koreader.v1+json`; without this header it returns 412.
TLS verification stays enabled. The Upptime option named
`__dangerous__body_down_if_text_missing` checks response content; it does not
turn off TLS verification. A harmless JSON formatting change may require updating
these literal fragments.

Uptime CI is scheduled every five minutes at minutes 2, 7, 12, etc. GitHub may
queue, delay or drop scheduled jobs, so these checks are not a guaranteed alerting
interval. Inspect workflow failures and expiring credentials during maintenance.

## GitHub Pages (owner setup)

After Static Site CI creates `gh-pages`:

1. Open **Settings → Pages**.
2. Choose **Deploy from a branch**, branch **gh-pages**, folder **/(root)**.
3. Set the custom domain to **status.deadpan.io** and save it before adding DNS.
4. In Cloudflare DNS, add a DNS-only CNAME: `status` → `timbueno.github.io`.
   Do not include the repository name in the CNAME target. No tunnel is needed.
5. When GitHub has issued the certificate, enable **Enforce HTTPS**.
6. Verify the page shows Deadpan Status, Leaf - KOSync and Leaf - API, and that
   history and incident links work. Remove the setup-pending note in README.md
   after the custom domain is verified.

The configuration is built for the custom domain root. For a temporary preview
at `timbueno.github.io/deadpan-status/`, remove `cname`, set
`status-website.baseUrl: /deadpan-status`, and regenerate the site. Restore the
custom-domain configuration before the final deployment.

## Incidents and additional apps

Upptime records outages and recovery in GitHub Issues. Treat issue content and
workflow output as public. Test incident behavior with a temporary test endpoint
or separate test repository rather than deliberately interrupting production.

Add other apps under `sites`, using the `<App> - <Service>` display-name pattern
and a permanent slug. For example, a future ScanBoy API check would use
`ScanBoy - API` and `scanboy-api`; its endpoint can remain on another domain and
provider. Select and verify that endpoint before adding it. Migrating ScanBoy's
infrastructure is independent of this status board.

References: [Upptime setup](https://upptime.js.org/docs/get-started/),
[configuration](https://upptime.js.org/docs/configuration/),
[GitHub Pages custom domains](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site).

## Summary freshness

The custom `refresh-summary.yml` workflow runs after successful `Uptime CI`
completion on master, including externally dispatched five-minute checks. It also
runs after the daily `Summary CI` to reconcile that output. It does not trigger
itself and can be started manually. Keep this custom file separate from generated
Upptime workflows so template updates preserve the dependency.

The workflow uses the same concurrency group as Upptime's writers and checks out
current master after acquiring it. It regenerates statistics with Upptime, then
sets each current status from the checked-out `history/<slug>.yml` and updates the
README status column. This avoids relying on GitHub's commit-history API to have
indexed a just-pushed recovery. The public site fetches `history/summary.json`;
a site rebuild is unnecessary, though browser/CDN caching can delay display.
Failed or canceled uptime runs do not trigger a refresh. A successful check that
finds a service down does trigger one: workflow success is not service health.

Run regression checks with `python3 -m unittest discover -s scripts -p 'test_*.py'`.
