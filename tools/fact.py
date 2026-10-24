#!/usr/bin/env python3
"""Daily "معلومة اليوم" short video for TikTok / YouTube Shorts (1080x1920, ~13 s).

  python3 fact.py fact.json out.mp4 [--still out.jpg]

fact.json = {
  "category": "الفضاء",                # shown as a chip at the top
  "hook": "هل تعلم؟",                   # big opening line
  "lines": ["...", "...", "..."],       # the fact, 3-6 short lines (4-7 words each)
  "source": "NASA",                     # short source name shown at the end
  "number": 1,                          # episode number -> "معلومة اليوم رقم 1"
  "palette": "sun"                      # sun | sea | mint | rose | sky | sand | violet
}
Light, bold look on purpose: distinct from the dark Instagram "hikma" identity.
"""
import json, math, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make import font, tlen, text, CAIRO, LATIN  # shared Arabic text helpers

W, H = 1080, 1920
PALETTES = {  # background, ink, accent (chip + rule), soft shape
    "sun":    ((252, 244, 226), (34, 28, 22), (240, 150, 40), (250, 214, 150)),
    "sea":    ((230, 242, 246), (16, 36, 48), (20, 120, 160), (170, 214, 228)),
    "mint":   ((232, 246, 238), (18, 44, 32), (30, 150, 100), (176, 224, 196)),
    "rose":   ((250, 236, 236), (52, 22, 30), (210, 70, 90), (244, 190, 196)),
    "sky":    ((236, 240, 252), (24, 30, 60), (70, 100, 220), (190, 202, 246)),
    "sand":   ((246, 238, 226), (44, 32, 22), (180, 110, 50), (230, 206, 176)),
    "violet": ((242, 236, 250), (36, 22, 56), (130, 70, 200), (214, 196, 242)),
}


def base(p, number):
    bg, ink, acc, soft = PALETTES[p]
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    # two big soft circles for depth
    d.ellipse((-260, -200, 520, 580), fill=soft)
    d.ellipse((W - 420, H - 620, W + 300, H + 100), fill=soft)
    img = img.filter(ImageFilter.GaussianBlur(2))
    d = ImageDraw.Draw(img)
    # dotted grid accent
    for y in range(260, 420, 36):
        for x in range(W - 300, W - 120, 36):
            d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=soft)
    # footer label
    f = font(CAIRO, 34, 700)
    lbl = f"معلومة اليوم رقم {number}"
    text(d, ((W - tlen(f, lbl)) / 2, 250), lbl, f, ink)
    return img


def layers(q):
    p = q.get("palette", "sun")
    bg, ink, acc, soft = PALETTES[p]
    out = []
    # chip
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    cf = font(CAIRO, 40, 800)
    cat = q.get("category", "")
    cw = tlen(cf, cat)
    d.rounded_rectangle(((W - cw) / 2 - 40, 330, (W + cw) / 2 + 40, 410), radius=40, fill=acc)
    text(d, ((W - cw) / 2, 336), cat, cf, (255, 255, 255))
    out.append(L)
    # hook
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    hk = q.get("hook", "هل تعلم؟")
    hf = font(CAIRO, 120, 900)
    text(d, ((W - tlen(hf, hk)) / 2, 470), hk, hf, ink)
    d.rounded_rectangle((W / 2 - 70, 690, W / 2 + 70, 702), radius=6, fill=acc)
    out.append(L)
    # fact lines
    lines = q["lines"]
    size = 70
    while size > 40:
        f = font(CAIRO, size, 700)
        if all(tlen(f, l) <= W - 180 for l in lines) and len(lines) * size * 1.6 < 900:
            break
        size -= 2
    lh = int(size * 1.6)
    y = 760 + max(0, (900 - len(lines) * lh) // 2) - 60
    for line in lines:
        L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        text(ImageDraw.Draw(L), ((W - tlen(f, line)) / 2, y), line, f, ink)
        out.append(L)
        y += lh
    # source
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    sf = font(CAIRO, 36, 600)
    src = "المصدر: " + q.get("source", "")
    text(d, ((W - tlen(sf, src)) / 2, y + 50), src, sf, acc)
    out.append(L)
    return out


def frame(bgimg, L, alphas, rise):
    img = bgimg.convert("RGBA")
    for layer, a, r in zip(L, alphas, rise):
        if a <= 0:
            continue
        if a < 1:
            layer = layer.copy(); layer.putalpha(layer.split()[3].point(lambda v: int(v * a)))
        if r:
            layer = layer.transform(layer.size, Image.AFFINE, (1, 0, 0, 0, 1, -r))
        img.alpha_composite(layer)
    return img.convert("RGB")


def render(q, out, still=None, fps=30):
    bgimg = base(q.get("palette", "sun"), q.get("number", 1))
    L = layers(q)
    n = len(L)
    # timings: chip 0.2s, hook 0.5s, each fact line every 1.1s from 1.6s, source after
    starts = [0.2, 0.5] + [1.6 + 1.1 * k for k in range(n - 3)] + [1.6 + 1.1 * (n - 3) + 0.4]
    fade = 0.45
    dur = starts[-1] + fade + 5.0
    tmp = tempfile.mkdtemp()
    for i in range(int(dur * fps)):
        t = i / fps
        al, ri = [], []
        for s in starts:
            a = min(1, max(0, (t - s) / fade))
            e = 1 - (1 - a) ** 3
            al.append(e); ri.append(int((1 - e) * 30))
        frame(bgimg, L, al, ri).save(f"{tmp}/{i:04d}.jpg", quality=90)
    if still:
        frame(bgimg, L, [1] * n, [0] * n).save(still, quality=92)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{tmp}/%04d.jpg",
        "-f", "lavfi", "-t", f"{dur:.2f}", "-i", "anoisesrc=color=pink:amplitude=0.12:sample_rate=44100",
        "-f", "lavfi", "-t", f"{dur:.2f}", "-i", "sine=frequency=220:sample_rate=44100",
        "-filter_complex",
        f"[1]lowpass=f=900,highpass=f=120,volume=0.5[n];[2]volume=0.04,tremolo=f=0.25:d=0.6[s];"
        f"[n][s]amix=inputs=2,afade=t=in:d=1.2,afade=t=out:st={dur-1.5:.2f}:d=1.5[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", "-preset", "medium",
        "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out], check=True)


if __name__ == "__main__":
    q = json.load(open(sys.argv[1], encoding="utf-8"))
    still = sys.argv[sys.argv.index("--still") + 1] if "--still" in sys.argv else None
    render(q, sys.argv[2], still)
