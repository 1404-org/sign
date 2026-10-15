"""Apply the 1404 rebrand to a Documenso checkout (AGPL parts only; never touches packages/ee).

Run from the repo root:  python3 .1404-brand/rebrand.py
Idempotent. On upgrade: check out the new Documenso tag, re-run make_assets.py + this script,
fix any 'MISSING' lines it prints (upstream moved a string), build, test.
"""
import colorsys, pathlib, re, sys

ROOT = pathlib.Path(".")
NAME = "1404"
SITE = "https://1404.io"
SOURCE = "https://github.com/1404-org/sign"
missing = []


def edit(path, pairs, count_ok=True):
    p = ROOT / path
    if "packages/ee" in str(p):
        sys.exit(f"refusing to edit {p}: packages/ee is under the Documenso commercial license")
    s = p.read_text()
    orig = s
    for old, new in pairs:
        if new in s:
            continue  # already applied (keeps the script idempotent for insertions)
        if old in s:
            s = s.replace(old, new)
        elif new not in s:
            missing.append(f"{path}: {old[:70]!r}")
    if s != orig:
        p.write_text(s)


def visible_lines(path, repl=((r"\bDocumenso, Inc\.", NAME), (r"\bDocumenso Logo\b", f"{NAME} logo"), (r"\bDocumenso\b", NAME))):
    """Swap 'Documenso' for 1404 on non-comment lines only."""
    p = ROOT / path
    out = []
    for line in p.read_text().splitlines(keepends=True):
        st = line.lstrip()
        if not st.startswith(("//", "*", "/*")) and "X-Documenso" not in line:
            for a, b in repl:
                line = re.sub(a, b, line)
        out.append(line)
    p.write_text("".join(out))


# 1. User-visible strings: page text, emails, subjects, authenticator labels.
for f in [
    "packages/email/templates/organisation-account-link-confirmation.tsx",
    "packages/email/templates/confirm-team-email.tsx",
    "packages/email/templates/organisation-invite.tsx",
    "packages/email/templates/admin-user-created.tsx",
    "packages/email/templates/team-email-removed.tsx",
    "packages/email/templates/organisation-leave.tsx",
    "packages/email/template-components/template-branding-logo.tsx",
    "packages/email/template-components/template-admin-user-created.tsx",
    "apps/remix/app/routes/_unauthenticated+/verify-email.$token.tsx",
    "apps/remix/app/routes/_unauthenticated+/articles.signature-disclosure.tsx",
    "apps/remix/app/routes/_recipient+/sign.$token+/_index.tsx",
    "apps/remix/app/components/general/app-nav-mobile.tsx",
    "apps/remix/app/components/dialogs/webhook-edit-dialog.tsx",
    "apps/remix/app/components/dialogs/webhook-create-dialog.tsx",
    "apps/remix/app/components/general/settings-upsell/email-domains-upsell.tsx",
    "apps/remix/app/components/general/settings-upsell/branding-upsell.tsx",
    "packages/ui/primitives/template-flow/add-template-settings.tsx",
    "packages/ui/primitives/document-flow/add-subject.tsx",
    "packages/trpc/server/admin-router/email-transport/send-test-email-transport.ts",
    "packages/lib/server-only/team/delete-team.ts",
    "packages/lib/server-only/team/create-team-email-verification.ts",
    "packages/lib/server-only/organisation/create-organisation-member-invites.ts",
    "packages/lib/server-only/auth/send-reset-password.ts",
    "packages/lib/server-only/auth/send-forgot-password.ts",
    "packages/lib/server-only/2fa/email/generate-2fa-credentials-from-email.ts",
    "packages/lib/jobs/definitions/emails/send-admin-user-created-email.handler.ts",
    "packages/lib/server-only/2fa/setup-2fa.ts",
    "packages/lib/utils/authenticator.ts",
    "packages/lib/constants/email.ts",
    # second pass (found by the leftover scan in UPGRADING.md)
    "packages/email/templates/organisation-join.tsx",
    "packages/email/template-components/template-document-image.tsx",
    "packages/email/template-components/template-confirmation-email.tsx",
    "apps/remix/app/routes/_unauthenticated+/o.$orgUrl.signin.tsx",
    "apps/remix/app/routes/_unauthenticated+/organisation.invite.$token.tsx",
    "apps/remix/app/routes/_profile+/p.$url.tsx",
    "apps/remix/app/routes/_profile+/_layout.tsx",
    "apps/remix/app/routes/_recipient+/_layout.tsx",
    "apps/remix/app/routes/_authenticated+/o.$orgUrl.support.tsx",
    "apps/remix/app/components/general/envelope-editor/envelope-editor-settings-dialog.tsx",
    "apps/remix/app/components/general/document/document-certificate-qr-view.tsx",
    "apps/remix/app/components/general/organisations/organisation-billing-banner.tsx",
    "apps/remix/app/components/embed/embed-document-completed.tsx",
    "apps/remix/app/components/dialogs/token-create-dialog.tsx",
    "apps/remix/app/components/dialogs/envelope-distribute-dialog.tsx",
    "apps/remix/app/components/dialogs/account-delete-dialog.tsx",
    "packages/trpc/server/open-api.ts",
    "packages/api/v1/openapi.ts",
]:
    visible_lines(f)

# 2. Links to Documenso's site -> 1404.
edit("apps/remix/app/routes/_recipient+/sign.$token+/_index.tsx", [('to="https://documenso.com"', f'to="{SITE}"')])
edit("apps/remix/app/components/general/document-signing/document-signing-page-view-v2.tsx",
     [('href="https://documenso.com"', f'href="{SITE}"')])
edit("apps/remix/app/components/forms/signup.tsx",
     [("https://documen.so/terms", f"{SITE}/terms"), ("https://documen.so/privacy", f"{SITE}/privacy")])
edit("apps/remix/app/routes/_authenticated+/o.$orgUrl.support.tsx", [("https://documen.so/discord", f"{SITE}/contact")])
for f in ROOT.glob("packages/email/templates/*.tsx"):
    if "https://documenso.com" in f.read_text():
        edit(str(f), [("https://documenso.com", "https://sign.1404.io")])

# 3. Email footer: "sent using 1404", 1404 sender block, AGPL source offer.
edit("packages/email/template-components/template-footer.tsx", [
    ('href="https://documen.so/mail-footer">\n              Documenso\n            </Link>',
     f'href="{SITE}">\n              {NAME}\n            </Link>'),
    ("          Documenso, Inc.\n          <br />\n          2261 Market Street, #5211, San Francisco, CA 94114, USA",
     f"          {NAME} · 1404.io\n          <br />\n          Signing by 1404, built on open-source Documenso ({SOURCE})"),
])

# 4. Page titles / meta / share page.
(ROOT / "apps/remix/app/utils/meta.ts").write_text(f"""import {{ NEXT_PUBLIC_WEBAPP_URL }} from '@documenso/lib/constants/app';
import {{ i18n, type MessageDescriptor }} from '@lingui/core';

export const appMetaTags = (title?: MessageDescriptor) => {{
  const description = '{NAME} document signing.';

  return [
    {{
      title: title ? `${{i18n._(title)}} - {NAME}` : '{NAME}',
    }},
    {{
      name: 'description',
      content: description,
    }},
    {{
      name: 'author',
      content: '{NAME}',
    }},
    {{
      name: 'robots',
      content: 'noindex, nofollow',
    }},
    {{
      property: 'og:title',
      content: '{NAME} document signing',
    }},
    {{
      property: 'og:description',
      content: description,
    }},
    {{
      property: 'og:image',
      content: `${{NEXT_PUBLIC_WEBAPP_URL()}}/opengraph-image.jpg`,
    }},
    {{
      property: 'og:type',
      content: 'website',
    }},
  ];
}};
""")
visible_lines("apps/remix/app/routes/_share+/share.$slug.tsx", repl=(
    (r"Documenso - Join the open source signing revolution", f"{NAME} document signing"),
    (r"I just signed a document in style with Documenso!", f"I just signed a document with {NAME}"),
    (r"I just signed with Documenso!", f"I just signed with {NAME}"),
    (r"Documenso - Share", f"{NAME} - Share"),
))
edit("apps/remix/app/routes/_share+/share.$slug.tsx", [("https://documenso.com", SITE)])
edit("apps/remix/public/site.webmanifest", [('"name": "Documenso"', f'"name": "{NAME}"'), ('"short_name": "Documenso"', f'"short_name": "{NAME}"')])

# 5. Default signing reason + sender name.
edit("packages/lib/constants/app.ts", [("'Signed by Documenso'", f"'Signed by {NAME}'")])

# 6. Colours: Documenso green -> 1404 copper (#c9956b), primary foreground = 1404 ink.
def scale(h, s):
    ls = {50: .97, 100: .94, 200: .87, 300: .79, 400: .70, 500: .60, 600: .50, 700: .40, 800: .30, 900: .20, 950: .12}
    return {k: v for k, v in ls.items()}, h, s

H, S = 26.9, 0.465
def hexof(l):
    r, g, b = colorsys.hls_to_rgb(H / 360, l, S)
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))
ls, _, _ = scale(H, S)
tw = ROOT / "packages/tailwind-config/index.cjs"
s = tw.read_text()
block = re.search(r"documenso: \{.*?\n        \},", s, re.S).group(0)
new = "documenso: {\n          DEFAULT: '#C9956B',\n" + "".join(f"          {k}: '{hexof(l)}',\n" for k, l in ls.items()) + "        },"
tw.write_text(s.replace(block, new))
th = ROOT / "packages/ui/styles/theme.css"
s = th.read_text()
s = s.replace("--primary: 95.08 71.08% 67.45%;", "--primary: 26.9 46.5% 60.4%;")
s = s.replace("--primary-foreground: 95.08 71.08% 10%;", "--primary-foreground: 0 3% 6%;")
s = s.replace("--ring: 95.08 71.08% 67.45%;", "--ring: 26.9 46.5% 60.4%;")
for k, l in ls.items():
    s = re.sub(rf"--new-primary-{k}: [^;]+;", f"--new-primary-{k}: 27, 47%, {round(l*100)}%;", s)
th.write_text(s)

# 7. AGPL-3.0 section 13: offer the source to every network user (sign-in pages, signing pages, mobile menu).
SRC_LINK = (f'<a href="{SOURCE}" target="_blank" rel="noopener" className="underline underline-offset-2">'
            '<Trans>Source code (AGPL)</Trans></a>')
edit("apps/remix/app/routes/_unauthenticated+/_layout.tsx", [
    ("import { Outlet } from 'react-router';", "import { Trans } from '@lingui/react/macro';\nimport { Outlet } from 'react-router';"),
    ("          <Outlet />\n        </div>",
     "          <Outlet />\n        </div>\n\n        <p className=\"relative mt-8 text-center text-muted-foreground text-xs\">\n"
     f"          {NAME} · {SRC_LINK}\n        </p>"),
])
edit("apps/remix/app/components/general/app-nav-mobile.tsx", [
    ("            © {new Date().getFullYear()} 1404\n            <br />\n            <Trans>All rights reserved.</Trans>",
     f"            © {{new Date().getFullYear()}} 1404\n            <br />\n            {SRC_LINK}"),
])
edit("apps/remix/app/components/general/document-signing/document-signing-page-view-v2.tsx", [
    ("                  <BrandingLogo className=\"ml-2 inline-block h-[14px]\" />\n                </a>\n              )}",
     "                  <BrandingLogo className=\"ml-2 inline-block h-[14px]\" />\n                </a>\n              )}\n\n"
     f"              <a\n                href=\"{SOURCE}\"\n                target=\"_blank\"\n                rel=\"noopener\"\n"
     "                className=\"fixed bottom-0 left-0 z-40 hidden px-2 py-1 text-muted-foreground text-xs opacity-60 hover:opacity-100 lg:block\"\n"
     "              >\n                <Trans>Source code (AGPL)</Trans>\n              </a>"),
])

if missing:
    print("MISSING (upstream changed; fix by hand):")
    print("\n".join("  " + m for m in missing))
else:
    print("rebrand applied cleanly")
