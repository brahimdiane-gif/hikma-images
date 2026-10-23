"""Illustrated night-sky backgrounds drawn in code (no photos needed).

scene(name, W, H, seed) -> RGB image, already darkened for white text on top.
Names: cosmos, mosque, birds, desert, sea
photo_bg(path, W, H) -> a user photo, cover-cropped and darkened.
"""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageOps

SCENES = ["cosmos", "mosque", "birds", "desert", "sea"]


def vgrad(W, H, stops):
    """Vertical gradient through [(pos 0..1, (r,g,b)), ...]."""
    col = Image.new("RGB", (1, H))
    px = col.load()
    for y in range(H):
        t = y / (H - 1)
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= t <= p1:
                k = (t - p0) / max(1e-6, p1 - p0)
                px[0, y] = tuple(int(c0[i] + (c1[i] - c0[i]) * k) for i in range(3))
                break
    return col.resize((W, H))


def stars(img, rnd, n, y_max=1.0, big=0.03):
    W, H = img.size
    d = ImageDraw.Draw(img)
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for _ in range(n):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H * y_max) ** 1.0
        b = int(rnd.uniform(90, 255) * (1 - 0.6 * y / H))
        r = rnd.choice([0.6, 0.8, 1, 1, 1.3])
        d.ellipse((x - r, y - r, x + r, y + r), fill=(b, b, min(255, b + 15)))
        if rnd.random() < big:
            R = rnd.uniform(2.5, 5)
            gd.ellipse((x - R, y - R, x + R, y + R), fill=(120, 130, 160))
    return ImageChops.add(img, glow.filter(ImageFilter.GaussianBlur(4)))


def blobs(W, H, rnd, colors, n=7, blur=140, scale=1.0):
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(n):
        c = rnd.choice(colors)
        cx, cy = rnd.uniform(0, W), rnd.uniform(0, H)
        rx, ry = rnd.uniform(150, 420) * scale, rnd.uniform(90, 260) * scale
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=c)
    return layer.filter(ImageFilter.GaussianBlur(blur))


def crescent(img, cx, cy, r, color=(245, 230, 190)):
    W, H = img.size
    m = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(m)
    md.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    md.ellipse((cx - r + r * 0.45, cy - r - r * 0.12, cx + r + r * 0.45, cy + r - r * 0.12), fill=0)
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(glow).ellipse((cx - r * 2.2, cy - r * 2.2, cx + r * 2.2, cy + r * 2.2), fill=(70, 62, 45))
    img = ImageChops.add(img, glow.filter(ImageFilter.GaussianBlur(r)))
    return Image.composite(Image.new("RGB", (W, H), color), img, m.filter(ImageFilter.GaussianBlur(0.8)))


def finish(img, dark=0.35):
    """Darken + vignette so white text always reads."""
    W, H = img.size
    img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), dark)
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).ellipse((-W * 0.3, -H * 0.15, W * 1.3, H * 1.15), fill=255)
    img = Image.composite(img, Image.new("RGB", (W, H), (0, 0, 0)), vig.filter(ImageFilter.GaussianBlur(min(W, H) * 0.22)))
    noise = Image.effect_noise((W, H), 24).convert("L")
    return Image.blend(img, Image.merge("RGB", (noise,) * 3), 0.03)


# ---------------- scenes ----------------

def cosmos(W, H, rnd):
    img = vgrad(W, H, [(0, (6, 8, 22)), (0.5, (10, 10, 30)), (1, (4, 4, 12))])
    neb = blobs(W, H, rnd, [(90, 40, 120), (30, 80, 120), (120, 50, 80), (40, 60, 140)], n=9, blur=160)
    # a diagonal "milky way" band
    band = Image.new("L", (W, H), 0)
    bd = ImageDraw.Draw(band)
    a = rnd.uniform(-0.6, 0.6)
    for k in range(-3, 4):
        off = k * 60
        bd.line((0, H * 0.3 + off + a * W, W, H * 0.7 + off - a * W), fill=110 - abs(k) * 30, width=120)
    band = band.filter(ImageFilter.GaussianBlur(90))
    img = ImageChops.add(img, Image.composite(neb, Image.new("RGB", (W, H), 0), band.point(lambda v: min(255, v * 2))))
    img = ImageChops.add(img, neb.point(lambda v: int(v * 0.5)))
    img = stars(img, rnd, int(W * H / 900), big=0.02)
    # dense dust in the band
    dust = Image.new("RGB", (W, H), (0, 0, 0))
    dd = ImageDraw.Draw(dust)
    for _ in range(int(W * H / 400)):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        if band.getpixel((int(x), int(y))) > 40:
            b = rnd.randint(60, 160)
            dd.point((x, y), fill=(b, b, b))
    img = ImageChops.add(img, dust)
    return finish(img, 0.25)


def mosque_silhouette(W, H, rnd, base, color):
    d_layer = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(d_layer)
    cx = W * rnd.uniform(0.42, 0.58)
    s = W / 1080
    # ground
    d.rectangle((0, base, W, H), fill=255)
    # main prayer hall
    d.rectangle((cx - 330 * s, base - 150 * s, cx + 330 * s, base), fill=255)
    # drum + main dome
    d.rectangle((cx - 150 * s, base - 260 * s, cx + 150 * s, base - 140 * s), fill=255)
    d.pieslice((cx - 170 * s, base - 430 * s, cx + 170 * s, base - 90 * s), 180, 360, fill=255)
    d.rectangle((cx - 3 * s, base - 470 * s, cx + 3 * s, base - 420 * s), fill=255)
    d.ellipse((cx - 9 * s, base - 485 * s, cx + 9 * s, base - 467 * s), fill=255)
    # side domes
    for sx in (-1, 1):
        x = cx + sx * 230 * s
        d.pieslice((x - 80 * s, base - 230 * s, x + 80 * s, base - 70 * s), 180, 360, fill=255)
        d.rectangle((x - 2 * s, base - 250 * s, x + 2 * s, base - 225 * s), fill=255)
    # arches cut out (windows) — leave as silhouette, add faint lit arches later
    # minarets
    for sx in (-1, 1):
        x = cx + sx * 420 * s
        top = base - rnd.uniform(560, 640) * s
        d.rectangle((x - 26 * s, top, x + 26 * s, base), fill=255)
        d.rectangle((x - 40 * s, top + 120 * s, x + 40 * s, top + 140 * s), fill=255)  # balcony
        d.rectangle((x - 36 * s, top + 260 * s, x + 36 * s, top + 276 * s), fill=255)
        d.pieslice((x - 26 * s, top - 40 * s, x + 26 * s, top + 26 * s), 180, 360, fill=255)
        d.polygon([(x - 6 * s, top - 6 * s), (x + 6 * s, top - 6 * s), (x, top - 80 * s)], fill=255)
    # distant city / palms
    for _ in range(int(14 * s) + 6):
        x = rnd.uniform(0, W)
        if abs(x - cx) < 470 * s:
            continue
        h = rnd.uniform(40, 120) * s
        w = rnd.uniform(40, 110) * s
        d.rectangle((x - w / 2, base - h, x + w / 2, base), fill=255)
    return d_layer


def mosque(W, H, rnd):
    img = vgrad(W, H, [(0, (8, 12, 32)), (0.55, (24, 30, 64)), (0.78, (80, 60, 70)), (1, (40, 30, 30))])
    img = stars(img, rnd, int(W * H / 2000), y_max=0.6)
    img = crescent(img, W * rnd.choice([0.2, 0.8]), H * 0.22, W * 0.05)
    base = H * 0.86
    sil = mosque_silhouette(W, H, rnd, base, None)
    # warm lit windows in the hall
    lit = Image.new("RGB", (W, H), (0, 0, 0))
    ld = ImageDraw.Draw(lit)
    cx = W / 2
    s = W / 1080
    for i in range(-5, 6):
        x = cx + i * 52 * s
        ld.rounded_rectangle((x - 12 * s, base - 110 * s, x + 12 * s, base - 50 * s), radius=12 * s, fill=(150, 100, 40))
    img = Image.composite(Image.new("RGB", (W, H), (6, 7, 14)), img, sil)
    img = ImageChops.add(img, lit.filter(ImageFilter.GaussianBlur(3)))
    return finish(img, 0.2)


def bird(d, x, y, size, color):
    w = size
    d.line([(x - w, y - w * 0.25), (x - w * 0.45, y - w * 0.32), (x, y)], fill=color, width=max(2, int(size / 9)), joint="curve")
    d.line([(x, y), (x + w * 0.45, y - w * 0.32), (x + w, y - w * 0.25)], fill=color, width=max(2, int(size / 9)), joint="curve")


def birds(W, H, rnd):
    img = vgrad(W, H, [(0, (20, 18, 40)), (0.45, (90, 50, 60)), (0.72, (190, 110, 60)), (0.8, (220, 150, 80)), (1, (60, 35, 25))])
    sun = Image.new("RGB", (W, H), (0, 0, 0))
    sx, sy = W * rnd.uniform(0.35, 0.65), H * 0.78
    ImageDraw.Draw(sun).ellipse((sx - W * 0.4, sy - W * 0.4, sx + W * 0.4, sy + W * 0.4), fill=(120, 70, 20))
    img = ImageChops.add(img, sun.filter(ImageFilter.GaussianBlur(W * 0.15)))
    ImageDraw.Draw(img).ellipse((sx - 60, sy - 60, sx + 60, sy + 60), fill=(255, 205, 140))
    # hills
    d = ImageDraw.Draw(img)
    for k, (col, base, amp) in enumerate([((70, 40, 40), 0.82, 40), ((35, 22, 26), 0.88, 55), ((14, 10, 14), 0.93, 30)]):
        ph = rnd.uniform(0, 6)
        pts = [(x, H * base - amp * math.sin(x / W * 3 + ph) - 20 * math.sin(x / W * 9 + ph * 2)) for x in range(0, W + 20, 20)]
        d.polygon(pts + [(W, H), (0, H)], fill=col)
    # flock: loose V
    n = rnd.randint(9, 15)
    ax, ay = W * rnd.uniform(0.25, 0.75), H * rnd.uniform(0.25, 0.4)
    for i in range(n):
        side = 1 if i % 2 else -1
        k = (i + 1) // 2
        x = ax + side * k * rnd.uniform(40, 60) * W / 1080 + rnd.uniform(-12, 12)
        y = ay + k * rnd.uniform(22, 34) * W / 1080 + rnd.uniform(-10, 10)
        bird(d, x, y, rnd.uniform(14, 24) * W / 1080, (25, 16, 20))
    for _ in range(rnd.randint(3, 6)):  # stragglers
        bird(d, rnd.uniform(0.1, 0.9) * W, rnd.uniform(0.12, 0.5) * H, rnd.uniform(8, 14) * W / 1080, (40, 26, 30))
    return finish(img, 0.3)


def desert(W, H, rnd):
    img = vgrad(W, H, [(0, (5, 7, 20)), (0.55, (16, 20, 44)), (0.72, (50, 40, 60)), (1, (20, 14, 14))])
    img = stars(img, rnd, int(W * H / 700), y_max=0.7, big=0.03)
    img = crescent(img, W * rnd.choice([0.22, 0.78]), H * 0.22, W * 0.045)
    d = ImageDraw.Draw(img)
    layers = [((70, 46, 34), 0.70, 60), ((48, 30, 24), 0.78, 70), ((28, 18, 16), 0.86, 55), ((12, 8, 8), 0.93, 40)]
    for col, base, amp in layers:
        ph = rnd.uniform(0, 6)
        f = rnd.uniform(1.5, 2.6)
        def ridge(x, base=base, amp=amp, f=f, ph=ph):
            return H * base - amp * (0.5 + 0.5 * math.sin(x / W * f * math.pi + ph)) - amp * 0.3 * math.sin(x / W * 5.3 + ph * 1.7)
        pts = [(x, ridge(x)) for x in range(0, W + 10, 10)]
        d.polygon(pts + [(W, H), (0, H)], fill=col)
        if col == (48, 30, 24):
            ridge_mid = ridge
    # a small caravan on the middle dune ridge
    if rnd.random() < 0.7:
        cxs = W * rnd.uniform(0.2, 0.7)
        s = W / 1080 * 0.9
        for i in range(3):
            x = cxs + i * 70 * s
            y = ridge_mid(x) + 4
            d.ellipse((x - 26 * s, y - 50 * s, x + 26 * s, y - 25 * s), fill=(28, 18, 16))          # body
            d.ellipse((x - 10 * s, y - 70 * s, x + 12 * s, y - 40 * s), fill=(28, 18, 16))          # hump
            d.line((x + 22 * s, y - 42 * s, x + 40 * s, y - 72 * s), fill=(28, 18, 16), width=int(9 * s))  # neck
            d.ellipse((x + 34 * s, y - 80 * s, x + 52 * s, y - 68 * s), fill=(28, 18, 16))          # head
            for lx in (-18, -8, 10, 20):
                d.line((x + lx * s, y - 30 * s, x + lx * s, y), fill=(28, 18, 16), width=int(5 * s))
    return finish(img, 0.22)


def sea(W, H, rnd):
    img = vgrad(W, H, [(0, (8, 14, 34)), (0.55, (30, 50, 90)), (0.62, (120, 110, 130)), (0.63, (40, 60, 90)), (1, (6, 12, 24))])
    img = stars(img, rnd, int(W * H / 2500), y_max=0.5)
    mx, my, r = W * rnd.uniform(0.3, 0.7), H * 0.42, W * 0.07
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(glow).ellipse((mx - r * 3, my - r * 3, mx + r * 3, my + r * 3), fill=(60, 70, 90))
    img = ImageChops.add(img, glow.filter(ImageFilter.GaussianBlur(r * 1.5)))
    ImageDraw.Draw(img).ellipse((mx - r, my - r, mx + r, my + r), fill=(235, 235, 220))
    d = ImageDraw.Draw(img)
    horizon = H * 0.625
    for i in range(60):  # moon path glints
        y = horizon + (i / 60) ** 1.5 * (H - horizon)
        w = 10 + i * 4 * W / 1080
        x = mx + rnd.uniform(-w, w) * 0.6
        d.line((x - w * 0.3, y, x + w * 0.3, y), fill=(160, 165, 170), width=2)
    for i in range(120):  # wave lines
        y = horizon + rnd.uniform(0, 1) ** 1.6 * (H - horizon)
        x = rnd.uniform(0, W)
        d.line((x - 30, y, x + 30, y), fill=(50, 70, 100), width=1)
    return finish(img, 0.25)


def scene(name, W, H, seed):
    rnd = random.Random(seed)
    return {"cosmos": cosmos, "mosque": mosque, "birds": birds, "desert": desert, "sea": sea}[name](W, H, rnd)


def photo_bg(path, W, H):
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    im = ImageOps.fit(im, (W, H), Image.LANCZOS)
    im = im.filter(ImageFilter.GaussianBlur(1.2))
    return finish(im, 0.45)
