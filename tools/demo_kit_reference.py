"""Shared toolkit for the research demo videos (same look as the FDTD demo).
A demo = list of scenes; each scene = (duration, frame_fn(t) -> PIL.Image 1600x900).
Scenes are joined with a dip-to-dark transition below the header row."""
import json, subprocess
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1600, 900, 24
DARK = (14, 21, 38); CORAL = (228, 87, 46); WHITE = (255, 255, 255)
LIGHT = (214, 222, 236); MUTED = (150, 163, 189); DIM = (92, 106, 134); PANEL = (24, 34, 58)
FB = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"; FS = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"; FM = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
XF = 0.6
_fc = {}


def F(p, s):
    k = (p, s)
    if k not in _fc: _fc[k] = ImageFont.truetype(p, s)
    return _fc[k]


def rmask(w, h, r=12):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255); return m


def wrap(text, font, width):
    words = text.split(" "); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.getlength(t) <= width or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines


def chrome(tag, steps, step, title, desc, note=None):
    im = Image.new("RGB", (W, H), DARK); d = ImageDraw.Draw(im)
    fb = F(FB, 26); tb = fb.getbbox(tag)
    d.rectangle([40, 32, 40 + tb[2] - tb[0] + 32, 76], fill=CORAL); d.text((56, 54), tag, font=fb, fill=WHITE, anchor="lm")
    fs = F(FS, 17); fn = F(FB, 15); x = W - 40
    for i in range(len(steps) - 1, -1, -1):
        lab = steps[i]; bw = fs.getlength(lab) + 58; x0 = x - bw; act = i == step
        d.rounded_rectangle([x0, 36, x, 72], radius=18, fill=CORAL if act else None, outline=None if act else (52, 64, 92), width=2)
        d.text((x0 + 18, 54), f"{i + 1:02d}", font=fn, fill=WHITE if act else DIM, anchor="lm")
        d.text((x0 + 46, 54), lab, font=fs, fill=WHITE if act else MUTED, anchor="lm")
        x = x0 - 10
    ft = F(FB, 36); d.text((40, 112), f"{step + 1:02d}", font=ft, fill=CORAL); d.text((104, 112), title, font=ft, fill=WHITE)
    y = 166
    for line in desc:
        if F(FM, 21).getlength(line) > W - 80: print('WARNING desc too wide:', line[:60])
        d.text((40, y), line, font=F(FM, 21), fill=LIGHT); y += 31
    if note: d.text((W - 40, H - 22), note, font=F(FM, 16), fill=DIM, anchor="rs")
    return im


class Callouts:
    """Vertical list of (head, body) items with a coral bar, revealed one after another."""
    def __init__(self, x, y, width, items, gap=34, t0=0.6, dt=0.7, muted_last=False, times=None):
        self.items = []; yy = y; fh = F(FB, 24); fbd = F(FM, 20)
        for k, (head, body) in enumerate(items):
            lines = wrap(body, fbd, width - 24); h = 34 + len(lines) * 27
            self.items.append((head, lines, yy, h, DIM if (muted_last and k == len(items) - 1) else CORAL)); yy += h + gap
        if yy - gap > H - 40: print('WARNING callouts overflow:', items[0][0], yy - gap)
        self.x, self.t0, self.dt, self.fh, self.fbd = x, t0, dt, fh, fbd
        self.times = times or [t0 + k * dt for k in range(len(items))]

    def draw(self, im, t):
        d = ImageDraw.Draw(im)
        for k, (head, lines, y, h, bar) in enumerate(self.items):
            a = max(0.0, min(1.0, (t - self.times[k]) / 0.35))
            if a <= 0: continue
            mix = lambda c: tuple(int(DARK[i] + (c[i] - DARK[i]) * a) for i in range(3))
            dx = round((1 - a) * 12)
            d.rounded_rectangle([self.x + dx, y + 4, self.x + dx + 6, y + h - 6], radius=3, fill=mix(bar))
            d.text((self.x + 24 + dx, y), head, font=self.fh, fill=mix(WHITE))
            for j, l in enumerate(lines): d.text((self.x + 24 + dx, y + 36 + j * 27), l, font=self.fbd, fill=mix(MUTED))


def probe(path):
    o = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", path])
    s = json.loads(o)["streams"][0]; return s["width"], s["height"]


def fit_box(w, h, bw, bh):
    s = min(bw / w, bh / h); return int(round(w * s / 2) * 2), int(round(h * s / 2) * 2)


class Video:
    """Lazily decoded clip, scaled to (w, h). frame(k) must be called with non-decreasing k (holds the last frame)."""
    def __init__(self, path, box, start=0.0, dur=None, speed=1.0, crop=None, size=None, overlay=None):
        if crop:
            c = [int(v) for v in crop.split("=")[1].split(":")]; sw, sh = c[0], c[1]
        else:
            sw, sh = probe(path)
        self.w, self.h = size if size else fit_box(sw, sh, *box)
        self.path, self.start, self.dur, self.speed, self.crop = path, start, dur, speed, crop
        self.overlay = overlay  # optional PNG (same size as the cropped source) drawn on top, e.g. to relabel text
        self.n = int(dur / speed * FPS) if dur else None
        self.p = None; self.k = -1; self.last = None

    def _open(self):
        tail = ",".join([f"setpts=PTS/{self.speed}", f"fps={FPS}", f"scale={self.w}:{self.h}:flags=lanczos"])
        inp = ["ffmpeg", "-v", "error", "-ss", str(self.start)] + (["-t", str(self.dur)] if self.dur else []) + ["-i", self.path]
        if self.overlay:
            fc = f"[0:v]{self.crop + ',' if self.crop else ''}format=rgba[c];[c][1:v]overlay=0:0,{tail}[o]"
            cmd = inp + ["-loop", "1", "-i", self.overlay, "-filter_complex", fc, "-map", "[o]"]
        else:
            cmd = inp + ["-vf", ",".join(x for x in [self.crop, tail] if x)]
        cmd += ["-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    def frame(self, k):
        if self.p is None: self._open()
        if self.n is not None: k = min(k, self.n - 1)
        while self.k < k:
            need = self.w * self.h * 3; b = b""
            while len(b) < need:  # a pipe can return short reads; keep reading until a full frame or EOF
                chunk = self.p.stdout.read(need - len(b))
                if not chunk: break
                b += chunk
            if len(b) < need: self.n = self.k + 1; break
            self.last = Image.frombytes("RGB", (self.w, self.h), b); self.k += 1
        return self.last

    def seconds(self):
        return self.dur / self.speed


def image(path, box, crop=None):
    im = Image.open(path).convert("RGB")
    if crop: im = im.crop(crop)
    w, h = fit_box(im.width, im.height, *box); return im.resize((w, h), Image.LANCZOS)


def video_scene(base, vid, pos, t0=0.3, hold=1.0, callouts=None, label=None):
    m = rmask(vid.w, vid.h); dur = t0 + vid.seconds() + hold

    def frame(t):
        k = max(0, int((t - t0) * FPS)); fr = base.copy(); f = vid.frame(k)
        if f is not None: fr.paste(f, pos, m)
        if callouts: callouts.draw(fr, t)
        return fr
    return dur, frame


def image_scene(base, img, pos, dur, callouts=None, fade=0.4):
    m = rmask(*img.size)

    def frame(t):
        fr = base.copy(); a = max(0.0, min(1.0, t / fade))
        fr.paste(img, (pos[0], pos[1] + round((1 - a) * 10)), m.point(lambda v: int(v * a)))
        if callouts: callouts.draw(fr, t)
        return fr
    return dur, frame


def render(scenes, out, preview=None, crf=22):
    starts = []; t = 0
    for i, (dur, _) in enumerate(scenes):
        starts.append(t); t += dur - (XF if i < len(scenes) - 1 else 0)
    total = t

    def at(gt):
        act = [(i, gt - s) for i, s in enumerate(starts) if 0 <= gt - s < scenes[i][0]]
        if not act: act = [(len(scenes) - 1, scenes[-1][0] - 1e-3)]
        if len(act) == 1: return scenes[act[0][0]][1](act[0][1])
        (i, ti), (j, tj) = act[0], act[1]; a = max(0.0, min(1.0, tj / XF))
        if a < 0.5: src = scenes[i][1](ti); scenes[j][1](tj)
        else: scenes[i][1](ti); src = scenes[j][1](tj)
        dark = Image.new("RGB", (W, H), DARK); dark.paste(src.crop((0, 0, W, 92)), (0, 0))
        return Image.blend(src, dark, 1 - abs(a - 0.5) * 2)

    print("scenes", [round(s[0], 1) for s in scenes], "total", round(total, 1), flush=True)
    if preview:
        # previews are taken in time order so the lazy decoders keep working
        for k, gt in enumerate(sorted(preview)):
            at(gt).save(out.replace(".mp4", f"_pv{k}.png"))
        return total
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-profile:v", "high", "-pix_fmt", "yuv420p",
                          "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for g in range(int(round(total * FPS))): p.stdin.write(at(g / FPS).tobytes())
    p.stdin.close(); p.wait(); return total
