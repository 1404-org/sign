"""Generate 1404 brand assets for the Documenso fork from the 1404.io font (Instrument Serif).
Run: python3 make_assets.py  (needs fonttools+brotli, Pillow). Outputs into ./out/."""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from PIL import Image, ImageDraw, ImageFont

INK, COPPER, PAPER = "#111010", "#c9956b", "#ffffff"
os.makedirs("out", exist_ok=True)
f = TTFont("InstrumentSerif-Regular.woff2"); f.flavor = None; f.save("out/InstrumentSerif-Regular.ttf")
f = TTFont("out/InstrumentSerif-Regular.ttf")
gs, cmap = f.getGlyphSet(), f.getBestCmap()
upm = f["head"].unitsPerEm

def word_path(text, tracking=-0.02):
    pen = SVGPathPen(gs); bp = BoundsPen(gs); x = 0
    for ch in text:
        g = cmap[ord(ch)]
        # flip y (font units are y-up)
        gs[g].draw(TransformPen(pen, (1, 0, 0, -1, x, 0)))
        gs[g].draw(TransformPen(bp, (1, 0, 0, -1, x, 0)))
        x += gs[g].width + tracking * upm
    xmin, ymin, xmax, ymax = bp.bounds
    return pen.getCommands(), (xmin, ymin, xmax - xmin, ymax - ymin)

d, (x, y, w, h) = word_path("1404")
pad = h * 0.08
vb = f"{x-pad:.0f} {y-pad:.0f} {w+2*pad:.0f} {h+2*pad:.0f}"
open("out/wordmark.path", "w").write(d)
open("out/wordmark.viewbox", "w").write(vb)
open("out/logo.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"><path fill="{INK}" d="{d}"/></svg>')
# square icon: ink tile, copper wordmark centred (same as 1404.io favicon)
S = 1000; scale = (S * 0.78) / w
tx = (S - w * scale) / 2 - x * scale; ty = (S - h * scale) / 2 - y * scale
icon = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {S} {S}"><rect width="{S}" height="{S}" rx="{S*0.125:.0f}" fill="{INK}"/>'
        f'<path transform="translate({tx:.1f} {ty:.1f}) scale({scale:.5f})" fill="{COPPER}" d="{d}"/></svg>')
open("out/icon.svg", "w").write(icon)
open("out/icon.inner", "w").write(f'{S}|{tx:.1f}|{ty:.1f}|{scale:.5f}')

ttf = "out/InstrumentSerif-Regular.ttf"
def text_img(size, text, fg, bg, box, font_px, radius=0):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(im)
    if bg: dr.rounded_rectangle([0, 0, size[0]-1, size[1]-1], radius=radius, fill=bg)
    ft = ImageFont.truetype(ttf, font_px)
    l, t, r, b = dr.textbbox((0, 0), text, font=ft)
    dr.text(((size[0]-(r-l))/2 - l, (size[1]-(b-t))/2 - t), text, font=ft, fill=fg)
    return im

def icon_png(px):
    big = text_img((px*8, px*8), "1404", COPPER, INK, None, int(px*8*0.42), radius=px)
    return big.resize((px, px), Image.LANCZOS)

for px in (16, 32, 180, 512):
    icon_png(px).save(f"out/icon-{px}.png")
icon_png(180).convert("RGB").save("out/apple-touch-icon.png")
icon_png(32).save("out/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
# logo.png (emails + PDF certificate): ink wordmark on transparent, 2x
text_img((560, 200), "1404", INK, None, None, 190).save("out/logo.png")
# logo_icon.png
icon_png(256).save("out/logo_icon.png")
# opengraph 1200x630: ink background, copper wordmark, tagline
og = Image.new("RGB", (1200, 630), INK); dr = ImageDraw.Draw(og)
ft = ImageFont.truetype(ttf, 230); l, t, r, b = dr.textbbox((0, 0), "1404", font=ft)
dr.text(((1200-(r-l))/2 - l, 190 - t), "1404", font=ft, fill=COPPER)
ft2 = ImageFont.truetype(ttf, 46); l, t, r, b = dr.textbbox((0, 0), "Document signing", font=ft2)
dr.text(((1200-(r-l))/2 - l, 470), "Document signing", font=ft2, fill="#e8e2db")
og.save("out/opengraph-image.jpg", quality=90)
print("viewBox", vb)
