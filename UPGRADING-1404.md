# Upgrading the 1404 signing fork to a new Documenso release

Do this for security releases. Nothing breaks if you don't; the edge runs a pinned image.

1. Pick a release at least 2 weeks old: https://github.com/documenso/documenso/releases
2. `git fetch https://github.com/documenso/documenso.git tag vX.Y.Z --no-tags`
   `git checkout -b 1404-vX.Y.Z vX.Y.Z`
3. Bring our tooling over: `git checkout 1404-v<old> -- .1404-brand .github/workflows/1404-image.yml NOTICE-1404.md UPGRADING-1404.md`
   and `git rm -q $(ls .github/workflows/*.yml | grep -v 1404-image.yml)`
4. `cd .1404-brand && python3 make_assets.py && cd ..` (needs fonttools+brotli, Pillow)
5. `bash .1404-brand/apply.sh` (copies assets, writes logo components, runs rebrand.py). If it prints MISSING lines, upstream moved a string: fix by hand.
6. Leftover scan (should list only license notices, an enum value, the footer credit, telemetry log line):
   `grep -rnw Documenso --include=*.tsx --include=*.ts apps/remix/app packages/email packages/ui packages/lib packages/trpc packages/api | grep -vE "packages/ee|\.test\.|\.spec\.|/translations/|e2e|packages/email/preview" | grep -vE "^[^:]+:[0-9]+:\s*(//|\*|/\*)|X-Documenso"`
7. Commit "1404 branding", push the branch, tag `vX.Y.Z-1404.1`, push the tag. GitHub Actions builds
   `ghcr.io/1404-org/sign:vX.Y.Z-1404.1` (arm64, ~20-40 min).
8. On 1404-edge (`ssh -i ~/.ssh/edge_admin ubuntu@98.94.140.191` from mc-1404):
   back up first (`/opt/1404-edge/backup.sh` if present, else `docker compose exec database pg_dump`),
   set the image tag in `/opt/1404-edge/documenso/compose.yml`, `docker compose pull && docker compose up -d`.
   Rollback = previous tag in compose.yml. Check https://sign.1404.io/signin and send yourself a test document.

Never edit `packages/ee/` (commercial license).
