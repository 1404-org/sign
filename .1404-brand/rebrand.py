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
    squash = lambda t: re.sub(r"\s+", "", t)
    for old, new in pairs:
        # already applied? (also after the repo's formatter has reflowed our insertion)
        if new in s or squash(new) in squash(s) or (SOURCE in new and SOURCE in s and SOURCE not in old):
            continue
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
wm = ROOT / "apps/remix/public/site.webmanifest"
wm.write_text(re.sub(r'(?i)#A2E771', '#C9956B', wm.read_text()))
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
s = s.replace(block, new)
# Tailwind's stock green/lime/emerald (success states, status badges) -> the same copper scale.
if not re.search(r"green:\s*\{\s*//\s*1404", s):
    alias = "".join(f"        {c}: {{  // 1404\n          DEFAULT: '#C9956B',\n" + "".join(f"          {k}: '{hexof(l)}',\n" for k, l in ls.items()) + "        },\n"
                    for c in ("green", "lime", "emerald"))
    s = s.replace("        documenso: {", alias + "        documenso: {", 1)
tw.write_text(s)
th = ROOT / "packages/ui/styles/theme.css"
s = th.read_text()
s = s.replace("--primary: 95.08 71.08% 67.45%;", "--primary: 26.9 46.5% 60.4%;")
s = s.replace("--primary-foreground: 95.08 71.08% 10%;", "--primary-foreground: 0 3% 6%;")
s = s.replace("--ring: 95.08 71.08% 67.45%;", "--ring: 26.9 46.5% 60.4%;")
for k, l in ls.items():
    s = re.sub(rf"--new-primary-{k}: [^;]+;", f"--new-primary-{k}: 27, 47%, {round(l*100)}%;", s)
s = s.replace("--field-card: 95 74% 90%;", "--field-card: 27 47% 92%;")
s = s.replace("--field-card-border: 95.08 71.08% 67.45%;", "--field-card-border: 26.9 46.5% 60.4%;")
s = s.replace("--secondary-foreground: 95.08 71.08% 67.45%;", "--secondary-foreground: 26.9 46.5% 60.4%;")
s = s.replace("--accent-foreground: 95.08 71.08% 67.45%;", "--accent-foreground: 26.9 46.5% 60.4%;")
th.write_text(s)

s = th.read_text()
s = s.replace("--card-border-tint: 112 205 159;", "--card-border-tint: 201 149 107;")
th.write_text(s)

# Background pattern on sign-in pages: desaturate Documenso's green to a warm neutral, keep alpha.
try:
    from PIL import Image
    bp = ROOT / "packages/assets/images/background-pattern.png"
    im = Image.open(bp).convert("RGBA")
    r, g, b, a = im.split()
    vis = [c for n, c in sorted(im.getcolors(1 << 24), reverse=True)[:20] if c[3] > 0]
    if vis and sum(c[1] - c[0] for c in vis) / len(vis) > 8:  # still green-tinted
        grey = Image.merge("RGB", (r, g, b)).convert("L")
        warm = Image.merge("RGBA", (grey.point(lambda v: int(v * 0.96)), grey.point(lambda v: int(v * 0.93)), grey.point(lambda v: int(v * 0.90)), a))
        warm.save(bp, optimize=True)
except ImportError:
    missing.append("background-pattern.png: Pillow not installed, pattern left green")

# Green raster art (email icons, signing celebration, certificate PDF art, Android icons) -> copper.
def green_share(im):
    small = im.copy(); small.thumbnail((200, 200))
    px = [p for p in small.getdata() if p[3] > 40]
    g = sum(1 for r, gg, b, a in px
            if (h := colorsys.rgb_to_hsv(r / 255, gg / 255, b / 255))[1] > 0.25 and h[2] > 0.3 and 0.17 < h[0] < 0.45)
    return g / len(px) if px else 0


def to_copper(im):
    out = im.copy(); px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if s > 0.08 and 0.15 < h < 0.48:
                nr, ng, nb = colorsys.hsv_to_rgb(27 / 360, min(s * 1.05, 0.62), v * 0.93)
                px[x, y] = (round(nr * 255), round(ng * 255), round(nb * 255), a)
    return out


try:
    from PIL import Image, ImageDraw, ImageFont
    out_dir = ROOT / ".1404-brand/out"
    for f in ["apps/remix/public/static/completed.png", "packages/assets/static/completed.png", "packages/email/static/completed.png",
              "apps/remix/public/static/mail-open.png", "packages/email/static/mail-open.png",
              "packages/assets/images/connections.png", "packages/assets/images/card-paid-figure.png",
              "packages/assets/images/card-sharing-figure.png", "packages/assets/images/profile-claim-teaser.png",
              "packages/assets/images/signing-celebration.png"]:
        p2 = ROOT / f
        if not p2.exists():
            missing.append(f"{f}: not found"); continue
        im = Image.open(p2).convert("RGBA")
        if green_share(im) <= 0.01:
            continue
        im = to_copper(im)
        if f.endswith("signing-celebration.png"):
            # cover Documenso's emblem in the centre with the 1404 wordmark
            cx, cy = im.width // 2, im.height // 2
            rad = int(min(im.size) * 0.17)
            bg = (251, 247, 244, 255)  # pale copper, matches the badge interior
            d = ImageDraw.Draw(im)
            d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(*bg[:3], 255))
            ttf = out_dir / "InstrumentSerif-Regular.ttf"
            if ttf.exists():
                ft = ImageFont.truetype(str(ttf), int(rad * 0.85))
                l, t, r_, b_ = d.textbbox((0, 0), NAME, font=ft)
                d.text((cx - (r_ - l) / 2 - l, cy - (b_ - t) / 2 - t), NAME, font=ft, fill=(201, 149, 107, 255))
        im.save(p2, optimize=True)
    for size in (192, 512):
        src = out_dir / "icon-512.png"
        if src.exists():
            for d_ in ("apps/remix/public", "packages/assets"):
                Image.open(src).resize((size, size), Image.LANCZOS).save(ROOT / d_ / f"android-chrome-{size}x{size}.png")
    for wmf in ["apps/remix/public/site.webmanifest", "packages/assets/site.webmanifest"]:
        p2 = ROOT / wmf
        if p2.exists():
            t = re.sub(r'(?i)#A2E771', '#C9956B', p2.read_text())
            t = t.replace('"name": "Documenso"', f'"name": "{NAME}"').replace('"short_name": "Documenso"', f'"short_name": "{NAME}"')
            p2.write_text(t)
except ImportError:
    missing.append("raster recolour: Pillow not installed")

# Hex mirror of the theme, used by emails and PDF field rendering.
edit("packages/lib/constants/theme.ts", [
    ("fieldCard: '#e2f8d3',", "fieldCard: '#F4ECE5',"),
    ("fieldCardBorder: '#a2e771',", "fieldCardBorder: '#C9956B',"),
    ("primary: '#a2e771',", "primary: '#C9956B',"),
    ("primaryForeground: '#162c07',", "primaryForeground: '#111010',"),
    ("ring: '#a2e771',", "ring: '#C9956B',"),
])
for f in ["apps/remix/app/components/general/settings-upsell/sso-portal-upsell.tsx",
          "apps/remix/app/components/general/settings-upsell/branding-upsell.tsx"]:
    p2 = ROOT / f; p2.write_text(p2.read_text().replace("'#A2E771'", "'#C9956B'").replace("'#162C07'", "'#111010'").replace("'#F2FBEA'", "'#F4ECE5'"))

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
