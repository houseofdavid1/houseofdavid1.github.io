"""Research videos: high-quality re-encode + burned-in caption tag (hero-video style).
usage: python3 vbuild.py preview|encode [name ...]"""
import json, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont

R = os.path.dirname(os.path.abspath(__file__))
A = "/mnt/user-data/attachments/a9dc3d8a-129c-5cc5-a7ee-d0cd275ae232"
OUT = R + "/hq"; os.makedirs(OUT, exist_ok=True)
FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FM = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
FIXFS = {"sim-magdrop": 22, "sim-magpress": 22}
CORAL = (228, 87, 46); NAVY = (27, 42, 78)
HOLD = {"sim-keyhole-fdtd": 1.5}   # s: freeze the last frame before looping

# name, src, dur, speed, scale, precrop, mode(overlay|pad), tag, sub, crf, tune
V = [
 ("ai-keyhole-detect", "media/f42d30c8ad.avi", 14, 1, 2, "", "overlay", "KEYHOLE DETECTION", "Coaxial camera · Al alloy · 1740 W · 7.6 mm/s", 19, ""),
 ("ai-bead-monitor", "/mnt/user-data/uploads/demo_top_bead_depth.mp4", 24, 1, 1, "", "pad", "REAL-TIME MONITORING", "Top bead width & penetration depth — AI vs. measured", 19, "animation"),
 ("ai-defect", "media/8785fd2ac1.mp4", 16, 1, 2, "", "overlay", "AI DEFECT DETECTION", "Weld bead inspection in real time", 19, ""),
 ("v2c-demo", A + "/b8aedeef-demo_video_v2.mp4", 23.2, 1, 1, "crop=1440:828:0:126", "overlay", "VISION-TO-CODE", "Camera image → control code → autonomous 3D weld", 20, ""),
 ("sim-keyhole", "media/0ec4dc3c52.gif", 26, 1, 2, "", "pad", "KEYHOLE WELDING SIMULATION", "3D level set · ray tracing · temperature field", 18, "animation"),
 ("sim-drilling", "media/97391f5f0b.gif", 11, 1, 2, "", "pad", "LASER DRILLING SIMULATION", "Hole shape · beam intensity · temperature  (10⁸ W/cm²)", 18, "animation"),
 ("sim-keyhole-fdtd", "media/65f8e31eba.gif", 3, 0.5, 1.25, "crop=820:724:157:73", "pad", "FDTD ELECTRODYNAMICS", "Laser beam in a keyhole tilted 20° · s-polarized", 18, "animation"),
 ("sim-fs-silicon", "media/af98a41238.gif", 30, 1, 2, "", "pad", "FEMTOSECOND LASER × SILICON", "80 fs pulse · two-temperature + ionization model", 18, "animation"),
 ("sim-plasma", "media/fbdaa829fb.gif", 42, 1.5, 960/396, "crop=396:396:52:24", "pad", "LASER–PLASMA INTERACTION", "Lattice Boltzmann · CO₂ laser in weakly ionized He", 18, "animation"),
 ("sim-mhd", "media/8d78986825.gif", 40, 1, 960/574, "crop=574:574:12:12", "pad", "MAGNETOHYDRODYNAMICS", "Lattice Boltzmann · Orszag–Tang vortex", 18, "animation"),
 ("sim-magdrop", "media/ea5d757eba.gif", 12, 1, 2, "crop=244:492:98:64", "pad", "MAGNETIC FIELD", "Field lines & interfacial force", 18, "animation"),
 ("sim-bounce", "media/0783a27e24.gif", 18.2, 1, 984/786, "crop=290:786:8:8", "pad", "BOUNCING BALL", "Unified momentum equation",  18, "animation"),
 ("sim-fsi", "media/2950267f95.gif", 152, 4, 2, "", "pad", "THERMAL RESIDUAL STRESS", "Unified momentum equation · temperature (top) & stress (bottom)", 19, "animation"),
 ("sim-lid", "media/9fe5cd7f2e.gif", 27, 1, 2, "crop=416:316:48:6", "pad", "FLUID–STRUCTURE INTERACTION", "Cavity flow & induced stress in the solid wall", 18, "animation"),
 ("ht-sim", A + "/88a341d4-____________3_____.mp4", 7, 1, 1.5, "", "pad", "3D THERMAL SIMULATION", "Laser heat treatment of a steel specimen", 18, "animation"),
 ("weld-keyhole-hs", "media/a70e642fae.mp4", 26.5, 1, 1.5, "", "overlay", "HIGH-SPEED IMAGING", "Keyhole & melt pool in laser welding", 19, ""),
 ("weld-coaxial-grid", "media/4b792ee510.avi", 30, 1, 2, "", "pad", "COAXIAL KEYHOLE IMAGING", "Top-aperture views at 5,000 fps · various conditions", 25, ""),
 ("weld-foil", "media/493558aa1a.mp4", 20, 1, 1.5, "", "overlay", "ULTRA-THIN FOIL WELDING", "50 µm AM 350 foil on 1 mm SUS 304", 19, ""),
 ("weld-foil-grid", "media/2c19dcf937.mp4", 20, 1, 1.5, "", "pad", "FOIL WELDING PROCESS MAP", "Laser power (rows) × welding speed (columns)", 19, ""),
 ("ai-monitor-sys", "media/7fd693efd0.mp4", 53, 2, 0.926, "crop=1378:858:31:161", "pad", "ABSORPTANCE MONITORING", "Al alloy · two cameras vs. one camera · red: weld defect", 25, ""),
 ("sim-plasma4", "comp/sim-plasma4.mp4", 42, 1.5, 0.75, "", "pad", "LASER–PLASMA INTERACTION", "Lattice Boltzmann · CO₂ laser (2 × 10⁷ W/cm²) in weakly ionized He", 18, "animation"),
 ("sim-fs-compare", "comp/sim-fs-compare.mp4", 4.5, 0.75, 0.8, "", "pad", "FEMTOSECOND LASER × SILICON", "80 fs pulse · without vs. with ionization", 18, "animation"),
 ("sim-em-keyhole", "comp/sim-em-keyhole.mp4", 2.8, 0.5, 1, "", "pad", "FDTD IN KEYHOLES", "Measured keyhole shapes · 1403 W · 16.3 mm/s", 18, "animation"),
]

def src_path(s):
    return s if s.startswith("/") else R + "/" + s


def probe(s):
    o = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", s])
    st = json.loads(o)["streams"][0]; return st["width"], st["height"]


def geom(v):
    name, s, dur, sp, sc, crop = v[:6]
    w, h = probe(src_path(s))
    if crop:
        c = crop.split("=")[1].split(":"); w, h = int(c[0]), int(c[1])
    W, H = int(round(w * sc / 2)) * 2, int(round(h * sc / 2)) * 2
    return w, h, W, H


def font(p, size): return ImageFont.truetype(p, size)


def build_overlay(v, W, H, padcol):
    """Return (png path, pad height). Text sized to ~3.1% of width (min 18 px)."""
    name, mode, tag, sub = v[0], v[6], v[7], v[8]
    fs = FIXFS.get(name) or max(18, round(W * 0.031)); ss = max(14, round(fs * 0.74))
    fb, fm = font(FB, fs), font(FM, ss)
    px, py = round(fs * 0.55), round(fs * 0.32)          # tag inner padding
    m = round(fs * 0.75)                                  # outer margin
    tb = fb.getbbox(tag); tw, th = tb[2] - tb[0], fs
    boxw, boxh = tw + 2 * px, round(th * 1.0) + 2 * py
    if mode == "pad":
        P = (boxh + 2 * m + 1) // 2 * 2
        img = Image.new("RGBA", (W, H + P), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        lum = sum(padcol) / 3
        d.rectangle([m, m, m + boxw, m + boxh], fill=CORAL + (255,))
        d.text((m + px, m + py - tb[1] + (boxh - 2 * py - (tb[3] - tb[1])) / 2), tag, font=fb, fill="white")
        # subtitle to the right of the tag, shrink if needed
        x0 = m + boxw + round(fs * 0.7); avail = W - x0 - m
        while fm.getlength(sub) > avail and ss > 11:
            ss -= 1; fm = font(FM, ss)
        sb = fm.getbbox(sub)
        col = (60, 70, 92, 255) if lum > 128 else (225, 230, 240, 255)
        d.text((x0, m + boxh / 2 - (sb[1] + sb[3]) / 2), sub, font=fm, fill=col)
        # thin accent rule under the header
        rc = (0, 0, 0, 28) if lum > 128 else (255, 255, 255, 34)
        d.rectangle([0, P - 1, W, P - 1], fill=rc)
    else:
        P = 0
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        d.rectangle([m, m, m + boxw, m + boxh], fill=CORAL + (255,))
        d.text((m + px, m + py - tb[1] + (boxh - 2 * py - (tb[3] - tb[1])) / 2), tag, font=fb, fill="white")
        sb = fm.getbbox(sub); sw = sb[2] - sb[0]; sh = ss
        sx, sy = m, m + boxh; spx, spy = round(ss * 0.6), round(ss * 0.38)
        d.rectangle([sx, sy, sx + sw + 2 * spx, sy + sh + 2 * spy], fill=(14, 21, 38, 200))
        d.text((sx + spx, sy + spy - sb[1] + (sh - (sb[3] - sb[1])) / 2), sub, font=fm, fill=(235, 240, 248, 255))
    p = f"{OUT}/{name}_ov.png"; img.save(p); return p, P


def pad_color(v, W, H):
    name, s = v[0], src_path(v[1]); crop = v[5]
    tmp = f"{OUT}/{name}_f0.png"
    vf = ",".join(x for x in [crop, f"scale={W}:{H}:flags=lanczos"] if x)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", s, "-vf", vf, "-frames:v", "1", tmp], check=True)
    im = Image.open(tmp).convert("RGB"); row = [im.getpixel((x, 1)) for x in range(0, W, 4)]
    row.sort(key=sum); c = row[len(row) // 2]; return c


def run(v, preview):
    name, s, dur, sp, sc, crop, mode, tag, sub, crf, tune = v
    w, h, W, H = geom(v)
    pc = (255, 255, 255) if name in ("sim-magpress", "sim-bounce") else (14, 21, 38) if name in ("sim-plasma", "sim-mhd", "sim-plasma4", "sim-keyhole-fdtd") else (pad_color(v, W, H) if mode == "pad" else (0, 0, 0))
    ov, P = build_overlay(v, W, H, pc)
    hexc = "0x%02X%02X%02X" % pc
    chain = [x for x in [crop, f"setpts=PTS/{sp}", f"scale={W}:{H}:flags=lanczos"] if x]
    if P: chain.append(f"pad={W}:{H + P}:0:{P}:color={hexc}")
    chain.append("fps=24")
    if name in HOLD: chain.append(f"tpad=stop_mode=clone:stop_duration={HOLD[name]}")
    fc = f"[0:v]{','.join(chain)}[b];[b][1:v]overlay=0:0:format=auto,format=yuv420p[o]"
    if preview:
        t = min(dur * 0.55, dur - 0.2)
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(t * 1.0), "-i", src_path(s), "-i", ov, "-filter_complex", fc, "-map", "[o]", "-frames:v", "1", f"{OUT}/{name}_pv.jpg"]
    else:
        cmd = ["ffmpeg", "-v", "error", "-y", "-t", str(dur), "-i", src_path(s), "-i", ov, "-filter_complex", fc, "-map", "[o]", "-an",
               "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-profile:v", "high", "-movflags", "+faststart"] + (["-tune", tune] if tune else []) + [f"{OUT}/{name}.mp4"]
    subprocess.run(cmd, check=True)
    print(name, W, H + P, "pad" if P else "ov", flush=True)


if __name__ == "__main__":
    mode = sys.argv[1]; only = set(sys.argv[2:])
    for v in V:
        if not only or v[0] in only:
            run(v, mode == "preview")
    print("ALLDONE")
