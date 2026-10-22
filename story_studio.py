"""Turn a user-supplied story project into print PDFs and a narrated video."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import wave
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, RectangleObject
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
FONT = ROOT / "assets" / "fonts" / "BpmfHuninn-Regular.ttf"
pdfmetrics.registerFont(TTFont("BpmfHuninn", str(FONT)))


def load_project(path: Path) -> tuple[Path, dict]:
    path = path.resolve()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("project.json must contain a JSON object")
    return path.parent, data


def init_project(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "images").mkdir(exist_ok=True)
    (folder / "audio").mkdir(exist_ok=True)
    manifest = folder / "project.json"
    if manifest.exists():
        raise FileExistsError(manifest)
    data = {
        "title": "請填入書名",
        "author": "請填入作者",
        "trim_mm": [150, 200],
        "bleed_mm": 3,
        "front_cover": {"image": "images/cover.png", "text": ["請填入書名"], "text_position": "top"},
        "back_cover": {"image": "images/back_cover.png", "text": ["請填入封底簡介"], "text_position": "top"},
        "pages": [
            {"image": f"images/page_{i:02}.png", "text": [], "text_position": "bottom"}
            for i in range(1, 25)
        ],
        "video_scenes": [],
    }
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Created {manifest}")


def inside_project(base: Path, relative: str) -> Path:
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError(f"Path escapes project folder: {relative}")
    return path


def validate(base: Path, data: dict, *, mode: str) -> None:
    if not data.get("title") or not data.get("author"):
        raise ValueError("title and author are required")
    pages = data.get("pages")
    if not isinstance(pages, list) or not pages or len(pages) % 8:
        raise ValueError("Interior pages must be a nonzero multiple of 8")
    for label, entry in [("front_cover", data.get("front_cover")),
                         ("back_cover", data.get("back_cover")),
                         *((f"page {i}", p) for i, p in enumerate(pages, 1))]:
        if not isinstance(entry, dict) or not isinstance(entry.get("image"), str):
            raise ValueError(f"{label}: image is required")
        if not isinstance(entry.get("text", []), list):
            raise ValueError(f"{label}: text must be a list of lines")
        if entry.get("text_position", "bottom") not in ("top", "bottom"):
            raise ValueError(f"{label}: text_position must be top or bottom")
        if mode == "book" and not inside_project(base, entry["image"]).is_file():
            raise FileNotFoundError(f"{label}: {entry['image']}")
    scenes = data.get("video_scenes", [])
    if not isinstance(scenes, list):
        raise ValueError("video_scenes must be a list")
    if mode == "video":
        if not scenes:
            raise ValueError("Add video_scenes before building a video")
        for i, scene in enumerate(scenes):
            if not isinstance(scene, dict) or not all(isinstance(scene.get(k), str) for k in ("image", "audio", "text")):
                raise ValueError(f"video scene {i}: image, audio, and text are required")
            for key in ("image", "audio"):
                if not inside_project(base, scene[key]).is_file():
                    raise FileNotFoundError(f"video scene {i}: {scene[key]}")


def draw_image(c: canvas.Canvas, path: Path, width: float, height: float) -> None:
    with Image.open(path) as image:
        iw, ih = image.size
    scale = max(width / iw, height / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(str(path), (width - dw) / 2, (height - dh) / 2, dw, dh, mask="auto")


def draw_lines(c: canvas.Canvas, lines: list[str], position: str, width: float,
               height: float, bleed: float) -> None:
    for i, line in enumerate(lines):
        if not isinstance(line, str):
            raise ValueError("Every text line must be a string")
        size = 22.0
        while size >= 12 and pdfmetrics.stringWidth(line, "BpmfHuninn", size) > width - 28 * mm:
            size -= 0.5
        if size < 12:
            raise ValueError(f"Text line is too long: {line}")
        x = (width - pdfmetrics.stringWidth(line, "BpmfHuninn", size)) / 2
        y = height - bleed - (22 + i * 13) * mm if position == "top" else bleed + (20 + (len(lines) - 1 - i) * 13) * mm
        if y < bleed + 10 * mm or y > height - bleed - 10 * mm:
            raise ValueError("Too many text lines for a page")
        c.setFont("BpmfHuninn", size)
        for dx, dy in [(-1.4, 0), (1.4, 0), (0, -1.4), (0, 1.4)]:
            c.setFillColor(HexColor("#FFFDF6"))
            c.drawString(x + dx, y + dy, line)
        c.setFillColor(HexColor("#292929"))
        c.drawString(x, y, line)


def set_boxes(path: Path, trim_w: float, trim_h: float, bleed: float) -> None:
    reader = PdfReader(path)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    for page in writer.pages:
        page[NameObject("/TrimBox")] = RectangleObject([bleed, bleed, bleed + trim_w, bleed + trim_h])
        page[NameObject("/BleedBox")] = RectangleObject([0, 0, trim_w + 2 * bleed, trim_h + 2 * bleed])
    temp = path.with_suffix(".boxed.pdf")
    with temp.open("wb") as stream:
        writer.write(stream)
    temp.replace(path)


def build_pdf(base: Path, data: dict, out: Path) -> None:
    validate(base, data, mode="book")
    trim_w, trim_h = (float(v) * mm for v in data.get("trim_mm", [150, 200]))
    bleed = float(data.get("bleed_mm", 3)) * mm
    width, height = trim_w + 2 * bleed, trim_h + 2 * bleed
    out.mkdir(parents=True, exist_ok=True)
    for name, entries in [("interior", data["pages"]), ("front_cover", [data["front_cover"]]),
                          ("back_cover", [data["back_cover"]])]:
        target = out / f"{name}.pdf"
        pdf = canvas.Canvas(str(target), pagesize=(width, height), pageCompression=1)
        pdf.setTitle(f"{data['title']} — {name}")
        pdf.setAuthor(data["author"])
        for entry in entries:
            draw_image(pdf, inside_project(base, entry["image"]), width, height)
            draw_lines(pdf, entry.get("text", []), entry.get("text_position", "bottom"), width, height, bleed)
            pdf.showPage()
        pdf.save()
        set_boxes(target, trim_w, trim_h, bleed)
        print(target)


def stamp(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    seconds, millis = divmod(millis, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"


def build_video(base: Path, data: dict, out: Path) -> None:
    validate(base, data, mode="video")
    import imageio_ffmpeg

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    out.mkdir(parents=True, exist_ok=True)
    segments = out / "segments"
    segments.mkdir(exist_ok=True)
    concat_lines, cues = [], []
    elapsed = 0.0
    for i, scene in enumerate(data["video_scenes"]):
        audio = inside_project(base, scene["audio"])
        picture = inside_project(base, scene["image"])
        wav = segments / f"scene_{i:02}.wav"
        clip = segments / f"scene_{i:02}.mp4"
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(audio),
                        "-ar", "44100", "-ac", "1", str(wav)], check=True)
        with wave.open(str(wav), "rb") as stream:
            spoken = stream.getnframes() / stream.getframerate()
        duration = math.ceil((spoken + 0.8) * 24) / 24
        subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-loop", "1",
                        "-framerate", "24", "-i", str(picture), "-i", str(wav),
                        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                        "-af", "apad", "-t", f"{duration:.3f}", "-r", "24",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                        "-c:a", "aac", "-b:a", "160k", str(clip)], check=True)
        concat_lines.append(f"file '{clip.as_posix()}'")
        cues.append(f"{i + 1}\n{stamp(elapsed)} --> {stamp(elapsed + spoken)}\n{scene['text']}\n")
        elapsed += duration
    concat = segments / "concat.txt"
    concat.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
    video = out / "story.mp4"
    subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat",
                    "-safe", "0", "-i", str(concat), "-c", "copy", str(video)], check=True)
    (out / "story.srt").write_text("\n".join(cues), encoding="utf-8-sig")
    print(video)
    print(out / "story.srt")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a Traditional Chinese picture book and narrated video")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="Create a blank project with 24 interior pages")
    init.add_argument("folder", type=Path)
    for command in ("check", "book", "video"):
        command_parser = sub.add_parser(command)
        command_parser.add_argument("project", type=Path, help="Path to project.json")
        if command != "check":
            command_parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.command == "init":
        init_project(args.folder)
        return
    base, data = load_project(args.project)
    if args.command == "check":
        validate(base, data, mode="structure")
        print(f"Structure OK: {len(data['pages'])} interior pages, {len(data.get('video_scenes', []))} video scenes")
    elif args.command == "book":
        build_pdf(base, data, args.out or base / "build" / "pdf")
    else:
        build_video(base, data, args.out or base / "build" / "video")


if __name__ == "__main__":
    main()
