"""Blur the code text inside the "AI-GENERATED CODE" window of the home video (assets/video/home-demo.mp4)
and its poster, keeping everything else at the same quality.

Usage:  python3 blur_home_code.py <clear source video> <clear poster jpg> <repo path>
  - Source: the high-quality clear version (crf 20, 5 MB, git 91b0a96) gives the same quality as the
    original site file (which was encoded from it with: -preset veryslow -tune film -crf 26).
  - The window sits low (y 320–590) until frame 118 and high (y 26–295) from frame 106 (cross-fade 106–118).
    The red title label stays sharp; only the code text area is blurred (Gaussian sigma 3.2).
To show the clear video again: copy the clear files over assets/video/home-demo.mp4 / home-demo-poster.jpg
and raise the ?v= numbers for both in index.html.
"""
import subprocess, sys, os
from PIL import Image, ImageFilter

SIGMA = 3.2
src, poster, repo = sys.argv[1], sys.argv[2], sys.argv[3]
out = os.path.join(repo, "assets/video/home-demo.mp4")
fc = (f"[0:v]split=5[base][a][b][la][lb];"
      f"[a]crop=400:254:29:332,gblur=sigma={SIGMA}[ab];[b]crop=400:254:29:38,gblur=sigma={SIGMA}[bb];"
      f"[la]crop=253:36:27:320[lac];[lb]crop=253:36:27:26[lbc];"
      f"[base][ab]overlay=29:332:enable='lte(n,118)'[t1];[t1][lac]overlay=27:320:enable='lte(n,118)'[t2];"
      f"[t2][bb]overlay=29:38:enable='gte(n,106)'[t3];[t3][lbc]overlay=27:26:enable='gte(n,106)',format=yuv420p[o]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", fc, "-map", "[o]", "-c:v", "libx264",
                "-preset", "veryslow", "-tune", "film", "-crf", "26", "-profile:v", "high", "-movflags", "+faststart", "-an", out], check=True)
p = Image.open(poster).convert("RGB"); lab = p.crop((27, 320, 280, 356))
box = (29, 332, 429, 586); p.paste(p.crop(box).filter(ImageFilter.GaussianBlur(SIGMA)), box[:2]); p.paste(lab, (27, 320))
p.save(os.path.join(repo, "assets/video/home-demo-poster.jpg"), quality=90)
print("ok")
