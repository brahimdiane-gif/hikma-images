#!/usr/bin/env python3
"""Hikma Instagram generator.

  python3 make.py post     quote.json    out.jpg      # 1080x1350 feed image
  python3 make.py carousel carousel.json outdir/      # 1080x1350 slides: 01.jpg, 02.jpg ...
  python3 make.py story    story.json    out.jpg      # 1080x1920 story (Quran verse, Amiri)
  python3 make.py reel     reel.json     out.mp4      # 1080x1920, ~10 s, lines fade in, soft ambient sound

quote.json    {"title": ["..."], "lines": ["..."], "source": "...", "theme": "ember", "seed": 7}
carousel.json {"cover": ["سطر", "سطر"], "subtitle": "...", "slides": [{"lines": [...], "source": "..."}, ...], "theme": "sand", "seed": 3}
story.json    {"lines": ["..."], "source": "...", "theme": "night", "seed": 5}
reel.json     {"lines": ["..."], "source": "...", "theme": "ink", "seed": 9, "quran": false}

Fonts are read from FONTS (google/fonts sparse checkout: ofl/cairo + ofl/amiri).
"""
import json, math, os, random, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

FONTS = os.environ.get("HIKMA_FONTS", "/home/claude/gfonts/ofl")
CAIRO = "cairo/Cairo[slnt,wght].ttf"
AMIRI = "amiri/Amiri-Bold.ttf"
SAVE_HINT = "احفظها لتعود إليها"

THEMES = {  # top, bottom, glow, accent
    "ember": ((18, 14, 12), (6, 5, 5), (150, 80, 40), (214, 150, 90)),
    "night": ((12, 18, 30), (4, 6, 12), (60, 90, 140), (170, 195, 230)),
    "sand":  ((34, 26, 18), (10, 8, 6), (170, 130, 80), (230, 200, 150)),
    "olive": ((20, 24, 16), (6, 8, 5), (100, 120, 60), (200, 210, 150)),
    "ink":   ((22, 16, 24), (7, 5, 8), (120, 70, 110), (215, 180, 210)),
}
WHITE = (250, 246, 238)
LATIN = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")


def font(path, size, wght=None):
    f = ImageFont.truetype(f"{FONTS}/{path}", size, layout_engine=ImageFont.Layout.RAQM)
    if wght:
        try:
            f.set_variation_by_axes([wght, 0])
        except Exception:
            pass
    return f


def tlen(f, s):
    return f.getlength(s.translate(LATIN), direction="rtl", language="ar")


def text(d, xy, s, f, fill):
    d.text(xy, s.translate(LATIN), font=f, fill=fill, direction="rtl", language="ar")


# ---------- backgrounds ----------

def background(W, H, theme, seed, centered=False):
    top, bot, glow, accent = THEMES[theme]
    rnd = random.Random(seed)
    grad = Image.linear_gradient("L").resize((W, H))
    img = Image.composite(Image.new("RGB", (W, H), bot), Image.new("RGB", (W, H), top), grad)
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    if centered:
        d.ellipse((W / 2 - 520, H * 0.42 - 520, W / 2 + 520, H * 0.42 + 520), fill=tuple(int(g * 0.6) for g in glow))
    for _ in range(2 if centered else 3):
        cx, cy = rnd.randint(150, W - 150), rnd.randint(150, H - 300)
        r = rnd.randint(300, 520)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=tuple(int(g * (0.3 if centered else 0.55)) for g in glow))
    img = ImageChops.add(img, layer.filter(ImageFilter.GaussianBlur(200 if centered else 160)))
    orn = Image.new("L", (W, H), 0)
    od = ImageDraw.Draw(orn)
    if centered:  # eight-point star rosette
        cx, cy = W / 2, H * 0.44
        for rr in (300, 360, 420):
            for rot in (0, math.pi / 4):
                pts = [(cx + rr * math.cos(rot + k * math.pi / 2), cy + rr * math.sin(rot + k * math.pi / 2)) for k in range(4)]
                od.polygon(pts, outline=26)
    else:  # corner rings
        ox, oy = rnd.choice([(W - 120, 140), (120, 140), (W - 140, H - 260)])
        for k in range(8):
            rr = 60 + k * 38
            for j in range(8):
                a = j * math.pi / 4
                cx, cy = ox + rr * 0.35 * math.cos(a), oy + rr * 0.35 * math.sin(a)
                od.ellipse((cx - rr * 0.6, cy - rr * 0.6, cx + rr * 0.6, cy + rr * 0.6), outline=22, width=1)
    img = Image.composite(Image.new("RGB", (W, H), accent), img, orn.filter(ImageFilter.GaussianBlur(0.6)))
    noise = Image.effect_noise((W, H), 28).convert("L")
    img = Image.blend(img, Image.merge("RGB", (noise,) * 3), 0.04)
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).ellipse((-W * 0.28, -H * 0.12, W * 1.28, H * 1.12), fill=255)
    return Image.composite(img, Image.new("RGB", (W, H), (0, 0, 0)), vig.filter(ImageFilter.GaussianBlur(240)))


def with_shadow(img, layer, blur=9, off=(3, 7)):
    sh = Image.new("L", img.size, 0)
    sh.paste(layer.split()[3].filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * 0.85)), off)
    img = Image.composite(Image.new("RGB", img.size, (0, 0, 0)), img, sh)
    img.paste(layer, mask=layer)
    return img


def fit(lines, path, max_w, start, wght=None, floor=30):
    size = start
    while size > floor:
        f = font(path, size, wght)
        if all(tlen(f, l) <= max_w for l in lines):
            return f, size
        size -= 2
    return font(path, size, wght), size


def footer(d, W, H, accent, source, hint=True, counter=None):
    if hint:
        hf = font(CAIRO, 28, 500)
        text(d, ((W - tlen(hf, SAVE_HINT)) / 2, 70), SAVE_HINT, hf, accent + (200,))
    if counter:
        cf = font(CAIRO, 30, 600)
        d.text((80, 70), counter, font=cf, fill=accent)
    if source:
        sf = font(CAIRO, 34, 600)
        sw = tlen(sf, source)
        sy = H - 150
        d.line(((W - sw) / 2 - 60, sy + 26, (W - sw) / 2 - 22, sy + 26), fill=accent, width=2)
        d.line(((W + sw) / 2 + 22, sy + 26, (W + sw) / 2 + 60, sy + 26), fill=accent, width=2)
        text(d, ((W - sw) / 2, sy), source, sf, accent)


# ---------- feed post ----------

def post_image(q, counter=None, hint=True):
    W, H = 1080, 1350
    theme = q.get("theme", "ember")
    accent = THEMES[theme][3]
    img = background(W, H, theme, q.get("seed", 1))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    margin, x_right = 110, W - 110
    max_w = W - 2 * margin
    title = q.get("title") or []
    if isinstance(title, str):
        title = [t for t in title.split("\n") if t]
    body = q.get("lines") or []
    tf, ts = fit(title, CAIRO, max_w, 86, 800) if title else (None, 0)
    bf, bs = fit(body, CAIRO, max_w, 64 if title else 72, 700) if body else (None, 0)
    t_lh, b_lh = int(ts * 1.45), int(bs * 1.55)
    gap = 70 if title and body else 0
    total = len(title) * t_lh + gap + len(body) * b_lh
    while total > H - 440 and (bs > 34 or ts > 50):
        if bs > 34:
            bs -= 2; bf = font(CAIRO, bs, 700); b_lh = int(bs * 1.55)
        if title and ts > 50:
            ts -= 2; tf = font(CAIRO, ts, 800); t_lh = int(ts * 1.45)
        total = len(title) * t_lh + gap + len(body) * b_lh
    y = max(180, (H - 120 - total) // 2)
    for line in title:
        text(d, (x_right - tlen(tf, line), y), line, tf, WHITE)
        y += t_lh
    if gap:
        y += gap // 2 - 6
        d.rounded_rectangle((x_right - 90, y, x_right, y + 6), radius=3, fill=accent)
        y += gap // 2
    for line in body:
        text(d, (x_right - tlen(bf, line), y), line, bf, (244, 240, 232))
        y += b_lh
    img = with_shadow(img, layer)
    footer(ImageDraw.Draw(img, "RGBA"), W, H, accent, q.get("source"), hint=hint, counter=counter)
    return img


def carousel(c, outdir):
    os.makedirs(outdir, exist_ok=True)
    theme, seed = c.get("theme", "sand"), c.get("seed", 1)
    n = len(c["slides"]) + 2
    paths = []
    # cover
    W, H = 1080, 1350
    accent = THEMES[theme][3]
    img = background(W, H, theme, seed)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cf, cs = fit(c["cover"], CAIRO, W - 200, 120, 800)
    lh = int(cs * 1.35)
    y = (H - len(c["cover"]) * lh) // 2 - 60
    for line in c["cover"]:
        text(d, ((W - tlen(cf, line)) / 2, y), line, cf, WHITE)
        y += lh
    d.rounded_rectangle((W / 2 - 50, y + 50, W / 2 + 50, y + 56), radius=3, fill=accent)
    if c.get("subtitle"):
        sf = font(CAIRO, 40, 600)
        text(d, ((W - tlen(sf, c["subtitle"])) / 2, y + 90), c["subtitle"], sf, accent)
    img = with_shadow(img, layer)
    dd = ImageDraw.Draw(img)
    swipe = "اسحب لترى المزيد"
    sw = font(CAIRO, 34, 700)
    text(dd, ((W - tlen(sw, swipe)) / 2, H - 140), swipe, sw, accent)
    p = os.path.join(outdir, "01.jpg"); img.save(p, quality=92); paths.append(p)
    # slides
    for i, s in enumerate(c["slides"], start=2):
        q = {"title": s.get("title") or s["lines"][:1], "lines": s.get("body") or s["lines"][1:],
             "source": s.get("source"), "theme": theme, "seed": seed + i}
        if not q["lines"]:
            q = {"title": [], "lines": s["lines"], "source": s.get("source"), "theme": theme, "seed": seed + i}
        img = post_image(q, counter=f"{i}/{n}", hint=False)
        p = os.path.join(outdir, f"{i:02d}.jpg"); img.save(p, quality=92); paths.append(p)
    # closing slide
    img = background(W, H, theme, seed + 99)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    lines = c.get("closing") or ["أيّها لمس قلبك؟", "اكتب رقمها في التعليقات"]
    ff, fs = fit(lines, CAIRO, W - 220, 84, 800)
    y = H // 2 - len(lines) * fs
    for line in lines:
        text(d, ((W - tlen(ff, line)) / 2, y), line, ff, WHITE)
        y += int(fs * 1.5)
    small = ["احفظ المنشور وأرسله لمن تحب"]
    sf = font(CAIRO, 40, 600)
    text(d, ((W - tlen(sf, small[0])) / 2, y + 60), small[0], sf, accent)
    img = with_shadow(img, layer)
    p = os.path.join(outdir, f"{n:02d}.jpg"); img.save(p, quality=92); paths.append(p)
    return paths


# ---------- story ----------

def story_layer(q, W=1080, H=1920):
    """Returns (background, list of per-line RGBA layers, source layer)."""
    theme = q.get("theme", "night")
    accent = THEMES[theme][3]
    bg = background(W, H, theme, q.get("seed", 1), centered=True)
    lines = q["lines"]
    quran = q.get("quran", True)
    path = AMIRI if quran else CAIRO
    wght = None if quran else 800
    size = 96 if quran else 84
    max_w = W - 2 * 120
    while size > 44:
        f = font(path, size, wght)
        if all(tlen(f, l) <= max_w for l in lines) and len(lines) * size * 1.9 < H * 0.5:
            break
        size -= 2
    lh = int(size * (1.9 if quran else 1.6))
    y = int(H * 0.44 - len(lines) * lh / 2 - size * 0.25)
    layers = []
    for line in lines:
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        text(ImageDraw.Draw(L), ((W - tlen(f, line)) / 2, y), line, f, WHITE)
        layers.append(L)
        y += lh
    S = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(S)
    ry = y + 40
    sd.rounded_rectangle((W / 2 - 45, ry, W / 2 + 45, ry + 5), radius=2, fill=accent)
    sf = font(CAIRO, 40, 600)
    src = q.get("source", "")
    text(sd, ((W - tlen(sf, src)) / 2, ry + 40), src, sf, accent)
    return bg, layers, S


def compose(bg, layers, alphas):
    out = bg.copy()
    full = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    for L, a in zip(layers, alphas):
        if a <= 0:
            continue
        if a < 1:
            L = L.copy(); L.putalpha(L.split()[3].point(lambda v: int(v * a)))
        full = Image.alpha_composite(full, L)
    return with_shadow(out, full, blur=10, off=(3, 8))


def story(q, out):
    bg, layers, S = story_layer(q)
    compose(bg, layers + [S], [1] * (len(layers) + 1)).save(out, quality=90)


# ---------- reel ----------

def reel(q, out, fps=30):
    bg, layers, S = story_layer(q)
    n = len(layers)
    step, fade, hold = 1.4, 0.8, 4.0
    dur = 0.6 + n * step + 0.6 + hold
    frames = int(dur * fps)
    tmp = tempfile.mkdtemp()
    last_key, last = None, None
    for i in range(frames):
        t = i / fps
        key = tuple(round(min(1, max(0, (t - 0.6 - k * step) / fade)), 2) for k in range(n + 1))
        if key != last_key:
            last_key, last = key, compose(bg, layers + [S], key)
        z = 1 + 0.04 * (t / dur)
        w, h = last.size
        zw, zh = int(w * z), int(h * z)
        fr = last.resize((zw, zh), Image.BILINEAR).crop(((zw - w) // 2, (zh - h) // 2, (zw - w) // 2 + w, (zh - h) // 2 + h))
        fr.save(f"{tmp}/{i:04d}.jpg", quality=88)
    # soft ambient sound: filtered brown noise (wind/room tone), no music
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{tmp}/%04d.jpg",
        "-f", "lavfi", "-t", f"{dur:.2f}", "-i", "anoisesrc=color=brown:amplitude=0.25:sample_rate=44100",
        "-af", f"lowpass=f=500,highpass=f=60,volume=0.6,afade=t=in:d=1.5,afade=t=out:st={dur-1.5:.2f}:d=1.5",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "23", "-preset", "medium",
        "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out], check=True)


if __name__ == "__main__":
    kind, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
    q = json.load(open(src, encoding="utf-8"))
    if kind == "post":
        post_image(q).save(out, quality=92)
    elif kind == "carousel":
        print("\n".join(carousel(q, out)))
    elif kind == "story":
        story(q, out)
    elif kind == "reel":
        reel(q, out)
    else:
        sys.exit("kind must be post|carousel|story|reel")
