from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parent
for name, count, length in [("crawl", 32, 1600), ("crawl_fast", 20, 800), ("stand_observe", 120, 6000), ("run", 32, 640)]:
    frames = []
    for i in range(count):
        image = Image.open(root / "animation_frames" / f"{name}_{i:03d}.png").convert("RGBA")
        background = Image.new("RGBA", image.size, (35, 39, 46, 255))
        frames.append(Image.alpha_composite(background, image).convert("RGB"))
    sheet = Image.new("RGB", (600 * 4, 600), (35, 39, 46))
    for j in range(4):
        sheet.paste(frames[j * count // 4], (j * 600, 0))
    palette = sheet.quantize(colors=255)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    durations = [round((i + 1) * length / count / 10) * 10 - round(i * length / count / 10) * 10 for i in range(count)]
    indexed[0].save(root / f"animation_{name}.gif", save_all=True, append_images=indexed[1:], duration=durations, loop=0, disposal=2, optimize=False)
    sheet.resize((1200, 300)).save(root / f"animation_{name}_contactsheet.png")
    with Image.open(root / f"animation_{name}.gif") as saved:
        duration = 0
        for i in range(saved.n_frames):
            saved.seek(i)
            duration += saved.info.get("duration", 0)
        print(f"{name}: {saved.n_frames} frames, {duration} ms")
