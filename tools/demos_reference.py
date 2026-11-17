"""Research demo videos built with demo_kit.  usage: python3 demos.py NAME preview|encode
NAME: mon (Process Monitoring 01) · bead (PM 02) · keyhole (Laser Processing 01) · foil (LP 03) · fsi (Simulation 07)
Scene texts follow the papers: one-camera / two-camera / partial-penetration absorptance monitoring, bead-geometry monitoring,
coaxial keyhole observation + keyhole dynamics, foil welding, unified momentum equation (flow-induced stress, thermal residual stress)."""
import os, sys
from demo_kit import *

R = os.path.dirname(os.path.abspath(__file__)); MD = R + "/media/"; OUT = R + "/hq"
SITE = os.path.dirname(R) + "/demo/keep/"  # copies of the site figures/videos used as sources (removed from the repo)
UP = "/mnt/user-data/uploads/"
Y0 = 236  # top of the content area


def demo_mon():
    tag = "ABSORPTANCE MONITORING"; st = ["Keyhole openings", "Keyhole → absorptance", "Live monitoring", "Partial penetration"]
    sc = []
    v = Video(MD + "f42d30c8ad.avi", (520, 620), start=0, dur=8.5)
    b = chrome(tag, st, 0, "Seeing the keyhole openings", [
        "Al 5052 · 1740 W · 7.6 mm/s — one high-speed camera looks straight down the laser axis into the keyhole",
        "Absorptance cannot be measured during welding, but the keyhole shape fixes it — so we watch the keyhole"])
    c = Callouts(640, Y0 + 30, 680, [
        ("Top and bottom at once", "In full penetration the keyhole is a tunnel: through its top opening (Al_t) the camera also sees the bottom opening (Al_b)"),
        ("Deep-learning detection", "YOLOR finds both openings in every frame (precision 0.98, recall 0.99) — no second camera under the plate"),
        ("Why the openings matter", "Whatever leaves through the bottom opening is lost; the rest bounces inside and heats the weld")])
    sc.append(video_scene(b, v, (40, Y0 + 2), callouts=c, hold=0.8))

    im = image(SITE + "fig-ai-keyhole-recon.jpg", (800, 624))
    b = chrome(tag, st, 1, "From openings to absorptance", [
        "The two openings are joined into a 3D keyhole, and ray tracing tells how much of the beam it traps",
        "A ResNet-34 trained on ray-tracing results replaces the slow calculation: 740 keyholes in 1.66 s, R² 0.998"])
    c = Callouts(880, Y0 + 30, 660, [
        ("(a) · (b) Detected openings", "Top and bottom openings found in the coaxial images (red circles), frame after frame"),
        ("(c) Reconstructed keyhole", "The beam (red) reflects off the walls (blue); every bounce absorbs another share of the energy"),
        ("What raises absorptance", "A more tilted front wall and a smaller — or closed — bottom opening: less of the beam escapes")])
    sc.append(image_scene(b, im, (40, Y0), 7.5, callouts=c))

    v = Video(MD + "7fd693efd0.mp4", (1010, 624), start=0, dur=53.3, speed=4.0, crop="crop=1378:858:31:161", overlay=SITE + "mon-live-labels.png")  # Korean row labels replaced in English
    b = chrome(tag, st, 2, "Reading the weld from absorptance", [
        "Time-averaged absorptance computed frame by frame and plotted along the bead (Al 5052)",
        "Upper row: two cameras (top + bottom) · lower row: one top camera — both catch the same changes of welding mode"])
    c = Callouts(1080, Y0 + 20, 480, [
        ("Mode 1 · stable", "The keyhole opens and closes again and again; absorptance swings between ~9 % (closed) and ~15 % → regular ripples"),
        ("Mode 2 · keyhole stays open", "Absorptance stops swinging, the keyhole is held open and the bead widens steadily"),
        ("Burn-through (red)", "An over-sized opening is detected and flagged — the one-camera model was trained on these defect images")],
        times=[1.0, 6.3, 9.9])
    sc.append(video_scene(b, v, (40, Y0), callouts=c, hold=1.6))

    v = Video(SITE + "mon-partial-live.mp4", (1060, 624), start=0, dur=62.9, speed=3.0, crop="crop=922:340:19:180")
    b = chrome(tag, st, 3, "Partial penetration: the hidden bottom", [
        "Al 1050 · 665 W · 11.2 mm/s — the keyhole ends inside the plate, so its depth is estimated from the melt-pool image (right)",
        "Opening (YOLOv7) + depth (CNN) form a two-channel keyhole image; a second CNN gives the absorptance — R² 0.997 vs. ray tracing"])
    c = Callouts(1140, Y0 + 10, 420, [
        ("Start-up · 9 → 43 %", "Absorptance climbs as the keyhole forms and penetration builds up"),
        ("Stable band 43–55 %", "A healthy keyhole keeps the averaged absorptance here (mean 49 %) and leaves regular ripples"),
        ("Drops to 9 %", "At 22.5 and 85 mm the keyhole collapses: melt is ejected, depth falls to zero and underfill forms — see the cross-section"),
        ("Relative change", "Other assumed keyhole shapes shift the curve but not its trend, so monitoring reads the changes")],
        gap=24, times=[0.8, 3.0, 5.6, 10.0])
    sc.append(video_scene(b, v, (40, Y0 + 90), callouts=c, hold=1.6))
    return sc


def demo_bead():
    tag = "BEAD GEOMETRY MONITORING"; st = ["Coaxial camera", "Top & bottom widths", "Width & depth"]
    sc = []
    im = image(SITE + "fig-ai-bead-sys.jpg", (800, 624))
    b = chrome(tag, st, 0, "A camera that sees through the melt", [
        "A small camera on the laser axis, with 532 nm LED light and a band-pass filter, films the aluminum melt pool",
        "Molten aluminum looks transparent here — the melt boundary under the surface shows, so one image holds the bead geometry"])
    c = Callouts(880, Y0 + 30, 660, [
        ("Two images in", "The current image plus the one 0.1 mm behind it: the recent past adds information and cancels noise"),
        ("VoVNet27-slim", "One CNN regressor outputs the top and bottom bead widths — 1.30 ms per image"),
        ("The hidden side", "The bottom bead cannot be seen from above — adding the second image clearly improves its prediction")])
    sc.append(image_scene(b, im, (40, Y0), 7.0, callouts=c))

    v = Video(SITE + "bead-top-bottom-live.mp4", (1010, 624), start=0, dur=127.0, speed=6.0, crop="crop=1384:1024:28:28")
    b = chrome(tag, st, 1, "Top and bottom bead widths, live", [
        "Al 1050 · 739 W · 8.2 mm/s — both widths predicted from top-side melt-pool images while welding (×6 speed)",
        "Upper: one-image model · lower: two-image model · gray / black: measured afterwards on the top and bottom beads"])
    c = Callouts(40 + v.w + 40, Y0 + 20, W - 80 - v.w - 40, [
        ("Top width · ~3 mm", "Seen directly from above — both models follow it closely"),
        ("Bottom width · hidden", "Full penetration begins only at ~9 mm; across this partial-to-full transition (8–15 mm) the two-image model follows the jump much better"),
        ("Why two images", "The image 0.1 mm earlier adds the pool's recent history and evens out errors from melt ejection, shadows and glare")],
        times=[0.8, 2.2, 4.5])
    sc.append(video_scene(b, v, (40, Y0), callouts=c, hold=1.4))

    v = Video(UP + "demo_top_bead_depth.mp4", (1520, 612), start=0, dur=46.4, speed=3.0)  # the source resets its curves in the last second
    b = chrome(tag, st, 2, "Width and penetration depth together", [
        "Every frame becomes a top bead width and a penetration depth while the weld is being made (×3 speed)",
        "Gray / black: measured afterwards on the bead and its longitudinal cross-section · blue / red: AI — no need to cut the weld"])
    sc.append(video_scene(b, v, (40, Y0 + 4), hold=1.4))
    return sc


def demo_keyhole():
    tag = "COAXIAL KEYHOLE OBSERVATION"; st = ["The problem", "Coaxial openings", "Uncoated vs. zinc-coated"]
    sc = []
    v = Video(MD + "a70e642fae.mp4", (1000, 624), start=0, dur=9, crop="crop=854:428:0:26")
    b = chrome(tag, st, 0, "Why look inside the keyhole", [
        "High-speed view of the melt pool and keyhole during laser welding",
        "The study: zero-gap lap welding of zinc-coated steel — zinc boils at 907 °C, far below steel's melting point"])
    c = Callouts(1080, Y0 + 30, 480, [
        ("Keyhole", "The vapor channel drilled by the beam; its shape decides where the energy goes"),
        ("Zinc vapor", "Trapped between the sheets, it has to escape through the keyhole — or it blows the melt out as spatter"),
        ("The catch", "From above or the side, the inside of the keyhole stays hidden — so we look down the laser axis")])
    sc.append(video_scene(b, v, (40, Y0 + 50), callouts=c, hold=0.8))

    v = Video(MD + "4b792ee510.avi", (1000, 624), start=0, dur=10, crop="crop=480:268:0:2")
    b = chrome(tag, st, 1, "Looking down the laser axis", [
        "Keyhole openings filmed coaxially at 5,000 frames per second, lit only by the keyhole's own glow",
        "Each tile is a different welding condition — the opening jumps around even in a stable weld"])
    c = Callouts(1080, Y0 + 30, 480, [
        ("Common frame", "The camera shares the beam path, so the beam center fixes one coordinate system for top and bottom images"),
        ("Erratic openings", "Size and position change from frame to frame — single images are misleading"),
        ("Averaged keyhole", "A semi-statistical frame analysis gives time-averaged openings, joined into a 3D keyhole")])
    sc.append(video_scene(b, v, (40, Y0 + 30), callouts=c, hold=0.8))

    im = image(SITE + "fig-weld-keyhole-3d.jpg", (960, 624))
    b = chrome(tag, st, 2, "Uncoated vs. zinc-coated keyholes", [
        "Time-averaged 3D keyholes for 1230–1830 W (rows) × 12.5–21.2 mm/s (columns) · red: laser beam",
        "Zinc vapor reshapes the keyhole — and where the beam lands on it decides the weld quality"])
    c = Callouts(1030, Y0 + 10, 530, [
        ("(a) DP590 · uncoated", "No zinc vapor, low internal pressure: the bottom opening tends to close to absorb enough energy and stays inside the beam; front wall 6–9°"),
        ("(b) GA DP590 · zinc-coated", "Zinc vapor keeps the bottom open; the front wall tilts 7–16° and the beam lands on it"),
        ("Good welds", "A beam on the front wall heats the zinc between the sheets directly — vapor pressure soars and the pool is torn apart. Keep the beam off the front wall")],
        gap=26)
    sc.append(image_scene(b, im, (40, Y0), 9.0, callouts=c))
    return sc


def demo_foil():
    tag = "ULTRA-THIN FOIL WELDING"; st = ["Setup", "Melt pool", "Beam size"]
    sc = []
    im = image(SITE + "fig-weld-foil-setup.jpg", (560, 624))
    b = chrome(tag, st, 0, "A 50 µm foil on a 1 mm sheet", [
        "AM 350 stainless foil, 50 µm thick, lap-welded onto SUS 304 with a 2 kW multi-mode fiber laser",
        "Any gap under the foil makes it melt through — a vacuum jig pulls foil and sheet into tight contact"])
    c = Callouts(660, Y0 + 30, 760, [
        ("(a) Specimen", "After welding it is laser-cut into an ASTM E8 tensile specimen to test the joint"),
        ("(b) Vacuum jig", "Suction holds the foil flat against the sheet along the whole weld line"),
        ("Test design", "Four beam diameters (200–1125 µm), each with 25 power–speed conditions chosen to give similar depths and welding modes")])
    sc.append(image_scene(b, im, (40, Y0), 7.0, callouts=c))

    v = Video(MD + "493558aa1a.mp4", (1000, 624), start=8, dur=12, crop="crop=854:428:0:26")
    b = chrome(tag, st, 1, "Melt pool on the foil", [
        "High-speed images at 5,000 fps under 532 nm LED light — brightness shows how flat the melt surface is",
        "Where the foil loses contact, the pool is suppressed, rolls to its edge and breaks up into droplets"])
    c = Callouts(1080, Y0 + 30, 480, [
        ("Bright, smooth pool", "Stable conduction-mode welding with the foil in good contact"),
        ("Darkening", "The surface bulges and the pool is being disrupted"),
        ("Droplets", "Surface tension pulls the melt into beads at the boundary; the weld fails until the pool re-forms")], dt=1.2)
    sc.append(video_scene(b, v, (40, Y0 + 50), callouts=c, hold=0.8))

    v = Video(MD + "2c19dcf937.mp4", (1000, 624), start=0, dur=12, crop="crop=854:428:0:26")
    b = chrome(tag, st, 2, "Beam size decides stability", [
        "25 power–speed conditions of one beam size, filmed side by side",
        "In a 50 µm foil the pool is 4–11 times wider than it is deep, so surface tension takes over as the beam grows"])
    c = Callouts(1080, Y0 + 30, 480, [
        ("Small beams", "Stable pools over a wide process window — the smaller, the better"),
        ("Large beams", "Thermocapillary flow drives the melt outward until it breaks into droplets: 625 µm fails at high energy, 1125 µm everywhere"),
        ("Strength", "Joint strength falls as penetration deepens — a shallow, stable weld is best")], dt=1.2)
    sc.append(video_scene(b, v, (40, Y0 + 50), callouts=c, hold=1.0))
    return sc


def demo_fsi():
    tag = "FLUID–STRUCTURE INTERACTION"; st = ["One equation", "Thermal residual stress"]
    sc = []
    v = Video(SITE + "sim-lid.mp4", (760, 624), start=0, dur=27, speed=2.0, crop="crop=832:632:0:82")
    b = chrome(tag, st, 0, "One equation for fluid and solid", [
        "Lid-driven cavity flow and the stress it induces in the surrounding solid, computed together (color: stress, Pa)",
        "Fluid and solid share one momentum equation written in velocity — no body-fitted mesh, no back-and-forth between two solvers"])
    c = Callouts(860, Y0 + 30, 700, [
        ("Smeared interface", "A level set blends the fluid and solid momentum equations over a few cells at the boundary, on a plain Cartesian grid"),
        ("Automatic coupling", "Stress stays continuous across the fluid–solid boundary without any interface iteration"),
        ("Validated", "Stresses match COMSOL Multiphysics (body-fitted mesh), velocities match benchmark cavity data, second-order convergence")], dt=1.2)
    sc.append(video_scene(b, v, (40, Y0 + 20), callouts=c, hold=0.8))

    v = Video(SITE + "sim-fsi.mp4", (1080, 624), start=0, dur=31.6, speed=2.5, crop="crop=1600:742:0:158")
    b = chrome(tag, st, 1, "Residual stress through melting and solidification", [
        "Laser heating of a carbon-steel sheet: temperature (top) and stress (bottom) through melting, solidification and cooling",
        "Liquid, mushy zone and solid form one continuum, so melt flow and phase change act on the stress directly"])
    c = Callouts(1160, Y0 + 20, 400, [
        ("Heating", "The hot zone softens and melts (≈ 0 stress); the cooler surroundings are pushed into compression; arrows: melt flow"),
        ("Cooling", "Plastic strain left from heating turns into tensile residual stress in the heated zone, compression around it"),
        ("Martensite · flow", "Martensite expands and relieves stress; ignoring melt flow makes the zone deeper and narrower — wrong stress")],
        times=[0.8, 4.5, 8.5])
    sc.append(video_scene(b, v, (40, Y0 + 60), callouts=c, hold=1.6))
    return sc


DEMOS = {"mon": demo_mon, "bead": demo_bead, "keyhole": demo_keyhole, "foil": demo_foil, "fsi": demo_fsi}

if __name__ == "__main__":
    name, mode = sys.argv[1], sys.argv[2]
    sc = DEMOS[name]()
    out = f"{OUT}/demo-{name}.mp4"
    if mode == "preview":
        starts = []; t = 0
        for i, (d, _) in enumerate(sc): starts.append(t); t += d - XF
        pts = [s + d - 0.8 for s, (d, _) in zip(starts, sc)]
        render(sc, out, preview=pts)
    else:
        print("total", round(render(sc, out), 1), "s")
