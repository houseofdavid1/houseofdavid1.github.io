# 참고용: Research의 "AI THERMAL MONITORING" 합성 동영상(ht-duo.mp4)을 만든 스크립트. 원본 동영상 경로는 당시 업로드 위치.
"""Merged heat-treatment monitoring dashboard: phase map (left) + hardness map (right), both from surface IR video."""
import subprocess, os, sys
from PIL import Image, ImageDraw, ImageFont
R = os.path.dirname(os.path.abspath(__file__)); OUT = R + "/hq"; os.makedirs(OUT, exist_ok=True)
A = "/mnt/user-data/attachments/a9dc3d8a-129c-5cc5-a7ee-d0cd275ae232"
FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"; FS = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"; FM = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
W, H = 1600, 940
BG = (238, 242, 247); CARD = (255, 255, 255); LINE = (214, 221, 232); INK = (27, 42, 78); MUTED = (92, 104, 128)
CORAL = (228, 87, 46); MINT = (15, 124, 122); DARK = (14, 21, 38)
PH = A + "/fb1c2ce7-Demo_video____________.mp4"; HD = A + "/641e6098-__________________.mp4"
DUR = 20.33
# (input index, crop x,y,w,h, dst x,y,w)
ITEMS = [
 (0, (1023, 171, 358, 268), (50, 152, 332)),     # phase: IR input
 (0, (1021, 533, 374, 138), (431, 152, 340)),    # phase: ground truth map
 (0, (1020, 702, 375, 133), (431, 286, 340)),    # phase: AI map
 (0, (120, 186, 865, 68), (50, 452, 720)),       # phase: top surface
 (0, (40, 270, 960, 520), (50, 518, 720)),       # phase: width/depth plots
 (1, (1291, 293, 339, 253), (830, 152, 332)),    # hardness: IR input
 (1, (1310, 772, 302, 72), (1211, 214, 340)),    # hardness: AI map (live)
 (1, (345, 150, 900, 130), (830, 452, 720)),     # hardness: top/side bead
 (1, (275, 290, 987, 430), (830, 566, 720)),     # hardness: width/depth plots
]


def h_of(c, w): return round(c[3] * w / c[2] / 2) * 2


def jet(t):
    t = max(0.0, min(1.0, t))
    r = max(0.0, min(1.0, 1.5 - abs(4 * t - 3))); g = max(0.0, min(1.0, 1.5 - abs(4 * t - 2))); b = max(0.0, min(1.0, 1.5 - abs(4 * t - 1)))
    return (int(r * 255), int(g * 255), int(b * 255))


def base():
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    fb = ImageFont.truetype(FB, 30); fm = ImageFont.truetype(FM, 22)
    tag = "AI THERMAL MONITORING"; sub = "Surface IR video  →  cross-sectional phase & hardness maps, predicted in real time"
    tb = fb.getbbox(tag); bw = tb[2] - tb[0] + 34
    d.rectangle([30, 28, 30 + bw, 78], fill=CORAL)
    d.text((47, 53 - (tb[1] + tb[3]) / 2), tag, font=fb, fill="white")
    sb = fm.getbbox(sub); d.text((30 + bw + 22, 53 - (sb[1] + sb[3]) / 2), sub, font=fm, fill=MUTED)
    # cards
    for (x, y, w, h, dark) in [(30, 140, 372, 284, True), (412, 140, 378, 284, True), (30, 438, 760, 480, False),
                               (810, 140, 372, 284, True), (1192, 140, 378, 284, True), (810, 438, 760, 480, False)]:
        d.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=DARK if dark else CARD, outline=None if dark else LINE, width=2)
    fl = ImageFont.truetype(FB, 17); ft = ImageFont.truetype(FS, 20); fs = ImageFont.truetype(FM, 17)

    def chip(x, y, k, col):
        kb = fl.getbbox(k); kw = kb[2] - kb[0] + 18
        d.rounded_rectangle([x, y, x + kw, y + 28], radius=6, fill=col)
        d.text((x + 9, y + 14 - (kb[1] + kb[3]) / 2), k, font=fl, fill="white"); return x + kw + 12

    def txt(x, y, t, f=ft, col=INK):
        b = f.getbbox(t); d.text((x, y + 14 - (b[1] + b[3]) / 2), t, font=f, fill=col); return x + f.getlength(t)

    # column titles + legends
    x = chip(30, 100, "PHASE MAP", MINT)
    for c, t in [((228, 40, 40), "Melted"), ((40, 190, 60), "Heat-treated"), ((30, 60, 220), "Heat-affected")]:
        d.rectangle([x, 107, x + 16, 121], fill=c); x = txt(x + 22, 100, t, fs, INK) + 16
    txt(x + 4, 100, "solid: measured · dashed: AI", fs, MUTED)
    x = chip(810, 100, "HARDNESS MAP", MINT)
    txt(x, 100, "Hardened width & depth · blue: measured, black: AI", fs, MUTED)
    # small labels inside dark cards
    lab = ImageFont.truetype(FS, 15)
    for (x0, y0, t) in [(50, 398, "IR camera · input"), (830, 398, "IR camera · input")]:
        d.text((x0, y0), t, font=lab, fill=(200, 210, 228))
    d.text((1211, 176), "AI prediction (live)", font=ImageFont.truetype(FS, 18), fill="white")
    # hardness colour bar
    bx, by, bw2, bh = 1211, 330, 340, 16
    for i in range(bw2):
        d.line([bx + i, by, bx + i, by + bh], fill=jet(i / (bw2 - 1)))
    f12 = ImageFont.truetype(FM, 15)
    for v in (220, 400, 600, 810):
        xx = bx + (v - 220) / (810 - 220) * (bw2 - 1); tw = f12.getlength(str(v))
        d.text((xx - tw / 2 if v not in (220, 810) else (xx if v == 220 else xx - tw), by + bh + 6), str(v), font=f12, fill=(200, 210, 228))
    d.text((bx, by + bh + 28), "Hardness (HV)", font=f12, fill=(200, 210, 228))
    # arrows between input and output cards
    for ax in (402, 1182):
        d.polygon([(ax + 2, 274), (ax + 9, 282), (ax + 2, 290)], fill=MUTED)
    p = f"{OUT}/ht-duo_base.png"; im.save(p); return p


def run(preview):
    bp = base()
    n0 = sum(1 for it in ITEMS if it[0] == 0); n1 = len(ITEMS) - n0
    parts = [f"[0:v]setpts=PTS/1.5,fps=24,split={n0}" + "".join(f"[a{i}]" for i in range(n0)),
             f"[1:v]setpts=PTS/0.492,fps=24,split={n1}" + "".join(f"[b{i}]" for i in range(n1))]
    ia = ib = 0; labels = []
    for k, (src, (x, y, w, h), (dx, dy, dw)) in enumerate(ITEMS):
        if src == 0: lab = f"a{ia}"; ia += 1
        else: lab = f"b{ib}"; ib += 1
        parts.append(f"[{lab}]crop={w}:{h}:{x}:{y},scale={dw}:{h_of((x, y, w, h), dw)}:flags=lanczos[c{k}]")
    prev = "[2:v]"
    for k, (_, _, (dx, dy, dw)) in enumerate(ITEMS):
        parts.append(f"{prev}[c{k}]overlay={dx}:{dy}:shortest=1[o{k}]"); prev = f"[o{k}]"
    parts.append(f"{prev}format=yuv420p[v]")
    fc = ";".join(parts)
    if preview:
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", "24", "-i", PH, "-ss", "8", "-i", HD, "-loop", "1", "-i", bp, "-filter_complex", fc, "-map", "[v]", "-frames:v", "1", f"{OUT}/ht-duo_pv.png"]
    else:
        cmd = ["ffmpeg", "-v", "error", "-y", "-t", "30.5", "-i", PH, "-t", "10", "-i", HD, "-loop", "1", "-t", str(DUR), "-i", bp, "-filter_complex", fc, "-map", "[v]", "-an", "-t", str(DUR),
               "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-tune", "animation", "-profile:v", "high", "-movflags", "+faststart", f"{OUT}/ht-duo.mp4"]
    subprocess.run(cmd, check=True); print("ht-duo ok")


if __name__ == "__main__":
    run(sys.argv[1] == "preview")
