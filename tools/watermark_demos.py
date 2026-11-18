"""Burn the lab watermark into the six demo videos (and their poster images).

Usage:  python3 watermark_demos.py <repo path>        e.g. python3 watermark_demos.py houseofdavid1.github.io
The mark sits in the free band above the step pills (top right), so it never covers
the demo's own text. To undo, restore the originals from git history:
    git checkout 360af67 -- assets/research/<name>.mp4 assets/research/<name>.jpg
"""
import subprocess, sys, os, shutil, tempfile
from PIL import Image, ImageDraw, ImageFont

TEXT = "© Laser Processing & AI Lab · UNIST"
NAMES = ["ai-monitor-demo", "ai-bead-demo", "weld-keyhole-demo", "weld-foil-demo", "sim-fsi-demo", "sim-fdtd-demo"]
FONT = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
W, H = 1600, 900


def mark_png(path):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 18)
    d.text((W - 40, 19), TEXT, font=f, fill=(214, 222, 236, 170), anchor="rm")   # right-aligned, centred in the 0–36 px band
    im.save(path)


def main(repo):
    md = os.path.join(repo, "assets/research")
    tmp = tempfile.mkdtemp()
    png = os.path.join(tmp, "wm.png"); mark_png(png)
    for n in NAMES:
        src = os.path.join(md, n + ".mp4"); out = os.path.join(tmp, n + ".mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-i", png, "-filter_complex", "[0:v][1:v]overlay=0:0,format=yuv420p",
                        "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-profile:v", "high", "-movflags", "+faststart", "-an", out], check=True)
        shutil.move(out, src)
        jp = os.path.join(md, n + ".jpg")
        im = Image.open(jp).convert("RGB")
        mk = Image.open(png)
        if im.size != (W, H): mk = mk.resize(im.size, Image.LANCZOS)
        im.paste(mk, (0, 0), mk); im.save(jp, quality=88)
        print("marked", n)


if __name__ == "__main__":
    main(sys.argv[1])
