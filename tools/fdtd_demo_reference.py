"""FDTD demo video: incident-angle sweep -> time evolution (40 deg) -> polarization in a 20-deg keyhole -> measured keyholes.
usage: python3 fdtd_demo.py preview|encode
Sources (현대중공업_UNIST_기형선_최종.pptx): slide 85 (angle stills + 40° GIF), slide 86 (E-fields at 20°, s/cir/p), slide 90 (keyholes)."""
import os, sys, subprocess
from PIL import Image, ImageDraw, ImageFont

R = os.path.dirname(os.path.abspath(__file__)); MD = R + "/media/"; OUT = R + "/hq"; os.makedirs(OUT, exist_ok=True)
S85 = os.path.dirname(R) + "/fdtd/s85/"
FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"; FS = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"; FM = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
W, H, FPS = 1600, 900, 24
DARK = (14, 21, 38); CARD = (24, 34, 58); CORAL = (228, 87, 46); WHITE = (255, 255, 255)
LIGHT = (214, 222, 236); MUTED = (150, 163, 189); DIM = (92, 106, 134)
XF = 0.6  # s dip-to-dark transition between scenes
F = lambda p, s: ImageFont.truetype(p, s)


def gif(name, crop=None):
    im = Image.open(MD + name); out = []
    for k in range(im.n_frames):
        try: im.seek(k)
        except Exception: break
        fr = im.convert("RGB"); out.append(fr.crop(crop) if crop else fr)
    return out


def fit(frames, w=None, h=None):
    fw, fh = frames[0].size
    if w is None: w = round(fw * h / fh)
    if h is None: h = round(fh * w / fw)
    return [f.resize((w, h), Image.LANCZOS) for f in frames]


def rmask(w, h, r=12):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255); return m


def text(d, xy, t, f, col, anchor="la"): d.text(xy, t, font=f, fill=col, anchor=anchor)


STEPS = ["Incident angle", "Time evolution", "Polarization", "Measured keyholes"]


def chrome(step, title, desc, note=None):
    """Static frame parts: tag, step indicator, scene title and description."""
    im = Image.new("RGB", (W, H), DARK); d = ImageDraw.Draw(im)
    fb = F(FB, 26); tag = "FDTD ELECTRODYNAMICS"; tb = fb.getbbox(tag)
    d.rectangle([40, 32, 40 + tb[2] - tb[0] + 32, 76], fill=CORAL); text(d, (56, 54), tag, fb, WHITE, "lm")
    # step indicator (right aligned)
    fs = F(FS, 17); fn = F(FB, 15); x = W - 40
    for i in range(len(STEPS) - 1, -1, -1):
        lab = STEPS[i]; lw = fs.getlength(lab); bw = lw + 58; x0 = x - bw
        act = i == step
        d.rounded_rectangle([x0, 36, x, 72], radius=18, fill=CORAL if act else None, outline=None if act else (52, 64, 92), width=2)
        text(d, (x0 + 18, 54), f"{i + 1:02d}", fn, WHITE if act else DIM, "lm")
        text(d, (x0 + 46, 54), lab, fs, WHITE if act else MUTED, "lm")
        x = x0 - 10
    # scene title + description
    ft = F(FB, 36); text(d, (40, 112), f"{step + 1:02d}", ft, CORAL); text(d, (104, 112), title, ft, WHITE)
    fd = F(FM, 21); y = 166
    for line in desc:
        text(d, (40, y), line, fd, LIGHT); y += 31
    if note: text(d, (W - 40, H - 22), note, F(FM, 16), DIM, "rs")
    return im


# ---------------------------------------------------------------- scene 1: incident-angle sweep (stills)
def scene_angle():
    files = sorted(os.listdir(S85)); labs = ["0°", "10°", "20°", "30°", "40°", "50°", "60°", "70°"]
    ims = [Image.open(S85 + f).convert("RGB") for f in files]
    ims = [im.crop((2, 2, im.width - 3, im.height - 4)) for im in ims]
    base = chrome(0, "Incident angle", ["Fe surface tilted 0–70° under an s-polarized beam · wavelength enlarged 20× (1.06 → 21.2 µm, dispersive FDTD)",
                                        "Enlarging the wavelength keeps n and κ — and so the reflectance — unchanged while using ~8,000× fewer 3D grid cells"],
                  "Electric field · the computed reflectance matches the Fresnel solution at every angle")
    h = 243; gap = 18; lab_h = 40; y0 = 256
    cells = []
    for i in range(6):
        r, c = divmod(i, 3); w = round(ims[i].width * h / ims[i].height)
        cells.append((ims[i].resize((w, h), Image.LANCZOS), 40 + c * (w + gap), y0 + r * (h + lab_h + gap)))
    th = 2 * h + lab_h + gap; xr = cells[2][1] + cells[2][0].width + 34
    for i in (6, 7):
        w = round(ims[i].width * th / ims[i].height); im = ims[i].resize((w, th), Image.LANCZOS)
        cells.append((im, xr, y0)); xr += w + gap
    d = ImageDraw.Draw(base); fl = F(FB, 22)
    for (im, x, y), lab in zip(cells, labs):
        text(d, (x + im.width / 2, y + im.height + 10), lab, fl, LIGHT, "ma")
    masks = [rmask(*c[0].size) for c in cells]
    dur = 7.2

    def frame(t):
        fr = base.copy()
        for i, ((im, x, y), m) in enumerate(zip(cells, masks)):
            a = max(0.0, min(1.0, (t - 0.25 - i * 0.42) / 0.35))
            if a <= 0: continue
            dy = round((1 - a) * 14)
            fr.paste(im, (x, y + dy), m.point(lambda v: int(v * a)))
        return fr
    return dur, frame


# ---------------------------------------------------------------- scene 2: time evolution at 40°
def scene_time():
    frames = fit(gif("9db1190a68.gif", (159, 72, 1084, 799)), h=600)
    base = chrome(1, "Time evolution · 40° incidence", ["The beam comes down from the top, reflects off the tilted Fe surface and leaves to the left",
                                                        "Where incident and reflected waves overlap, a standing interference pattern builds up — a wave effect ray tracing cannot show"],
                  "Electric field · s-polarized · enlarged wavelength")
    x, y = 40, 244; m = rmask(*frames[0].size)
    d = ImageDraw.Draw(base); xr = x + frames[0].width + 60; yy = y + 30
    fh = F(FB, 24); fb2 = F(FM, 20)
    for k, (head, body) in enumerate([("Incident beam", ["A Gaussian beam enters from the top and", "hits the Fe surface tilted by 40°"]),
                                      ("Reflected beam", ["Leaves toward the left; the Fresnel equations", "set how much is reflected at this angle"]),
                                      ("Interference", ["Incident and reflected waves overlap into", "fixed bright and dark fringes"]),
                                      ("Metal (Fe)", ["The field dies within a thin skin layer —", "that layer is where the energy is absorbed"])]):
        d.rounded_rectangle([xr, yy + 4, xr + 6, yy + 92], radius=3, fill=CORAL if k < 3 else DIM)
        text(d, (xr + 24, yy), head, fh, WHITE)
        for j, b in enumerate(body): text(d, (xr + 24, yy + 36 + j * 27), b, fb2, MUTED)
        yy += 138
    n = len(frames); spf = 0.2; t0 = 0.3; dur = t0 + n * spf + 1.2

    def frame(t):
        k = min(n - 1, max(0, int((t - t0) / spf))); fr = base.copy(); fr.paste(frames[k], (x, y), m); return fr
    return dur, frame


# ---------------------------------------------------------------- scene 3: polarization in a 20° keyhole
def scene_pol():
    crop = (157, 73, 977, 797)
    sets = [("s-polarized", "65f8e31eba.gif"), ("Circularly polarized", "33214a8387.gif"), ("p-polarized", "d0b974b815.gif")]
    pw = 486; gap = 21
    seqs = [fit(gif(f, crop), w=pw) for _, f in sets]
    base = chrome(2, "Polarization · keyhole tilted 20°", ["Electric field in a fully penetrated keyhole tilted 20°: the beam reflects off the walls and partly exits at the bottom",
                                                           "An E-field along the tilt direction (p-like on the walls) is absorbed best, s the least; circular is exactly their average"],
                  "Color scale set per panel · tilting adds reflections: Fe keyhole absorptance ~25–30 % upright → 90–100 % at 45°")
    d = ImageDraw.Draw(base); fl = F(FB, 22); y = 334
    for i, (lab, _) in enumerate(sets):
        x = 40 + i * (pw + gap); text(d, (x + pw / 2, y - 16), lab, fl, WHITE, "md")
    m = rmask(pw, seqs[0][0].height)
    n = min(len(s) for s in seqs); spf = 0.2; t0 = 0.3; dur = t0 + n * spf + 1.3

    def frame(t):
        k = min(n - 1, max(0, int((t - t0) / spf))); fr = base.copy()
        for i, s in enumerate(seqs): fr.paste(s[k], (40 + i * (pw + gap), y), m)
        return fr
    return dur, frame


# ---------------------------------------------------------------- scene 4: measured keyholes
def scene_keyhole():
    names = [("DP590", "7dd8195124.gif"), ("GA DP590", "0fd1630164.gif"), ("DP590", "10a0bbe94f.gif"), ("GA DP590", "6ce07c452a.gif")]
    ph = 560; seqs = [fit(gif(f, (0, 0, 294, 734)), h=ph) for _, f in names]; pw = seqs[0][0].width
    base = chrome(3, "Measured keyhole shapes", ["FDTD on keyhole shapes measured coaxially in DP590 and zinc-coated GA DP590 welding (1070 nm, wavelength ×22)",
                                                 "Same laser, very different keyholes — zinc-coated steel absorbs much less, confirmed by its smaller melt pools"],
                  "Electric field · 1070 nm laser, wavelength enlarged ×22")
    d = ImageDraw.Draw(base); fg = F(FB, 21); fl = F(FS, 20); y = 286; gap = 14; ggap = 56
    xs = [40, 40 + pw + gap, 40 + 2 * pw + gap + ggap, 40 + 3 * pw + 2 * gap + ggap]
    for g, cond in enumerate(["1403 W · 16.3 mm/s", "1830 W · 14.3 mm/s"]):
        xa, xb = xs[2 * g], xs[2 * g + 1] + pw
        text(d, ((xa + xb) / 2, y - 16), cond, fg, WHITE, "md")
    for (lab, _), x in zip(names, xs): text(d, (x + pw / 2, y + ph + 12), lab, fl, LIGHT, "ma")
    xr = xs[3] + pw + 60; yy = y + 20; fh = F(FB, 23); fb2 = F(FM, 19)
    for head, body in [("1403 W · DP590", ["Closed bottom: energy piles up at the tip,", "heats it and forces it open again — the", "open/close cycle of uncoated steel"]),
                       ("1403 W · GA DP590", ["Open bottom and more reflections, yet", "part of the beam escapes downward"]),
                       ("1830 W", ["Both keyholes run through the plate —", "excess energy leaves through the bottom"])]:
        d.rounded_rectangle([xr, yy + 4, xr + 6, yy + 40 + len(body) * 26], radius=3, fill=CORAL)
        text(d, (xr + 24, yy), head, fh, WHITE)
        for j, b in enumerate(body): text(d, (xr + 24, yy + 36 + j * 26), b, fb2, MUTED)
        yy += 64 + len(body) * 26
    m = rmask(pw, ph, 10)
    n = min(len(s) for s in seqs); spf = 0.14; t0 = 0.3; dur = t0 + n * spf + 1.2

    def frame(t):
        k = min(n - 1, max(0, int((t - t0) / spf))); fr = base.copy()
        for s, x in zip(seqs, xs): fr.paste(s[k], (x, y), m)
        return fr
    return dur, frame


def main(mode):
    scenes = [scene_angle(), scene_time(), scene_pol(), scene_keyhole()]
    starts = []; t = 0
    for i, (dur, _) in enumerate(scenes):
        starts.append(t); t += dur - (XF if i < len(scenes) - 1 else 0)
    total = t; print("scenes", [round(s[0], 2) for s in scenes], "total", round(total, 2))

    def at(gt):
        act = [(i, gt - s) for i, s in enumerate(starts) if 0 <= gt - s < scenes[i][0]]
        if len(act) == 1: return scenes[act[0][0]][1](act[0][1])
        (i, ti), (j, tj) = act[0], act[1]
        a = max(0.0, min(1.0, tj / XF))          # dip to dark below the header; the header row switches at the midpoint
        src = scenes[i][1](ti) if a < 0.5 else scenes[j][1](tj)
        dark = Image.new("RGB", (W, H), DARK); dark.paste(src.crop((0, 0, W, 92)), (0, 0))
        return Image.blend(src, dark, 1 - abs(a - 0.5) * 2)

    if mode == "preview":
        for k, gt in enumerate([5.5, starts[1] + 3.0, starts[2] + 4.0, starts[3] + 5.0, starts[1] - 0.2]):
            at(gt).save(f"{OUT}/fdtd-demo_pv{k}.png")
        return
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-tune", "animation", "-profile:v", "high", "-pix_fmt", "yuv420p",
                          "-movflags", "+faststart", f"{OUT}/fdtd-demo.mp4"], stdin=subprocess.PIPE)
    nf = int(round(total * FPS))
    for g in range(nf):
        p.stdin.write(at(g / FPS).tobytes())
    p.stdin.close(); p.wait(); print("encoded", nf, "frames")
    at(starts[1] + 4.5).save(f"{OUT}/fdtd-demo_poster.png")


if __name__ == "__main__":
    main(sys.argv[1])
