# Children's Story Studio

English · [繁體中文](README.md)

An open toolkit for developing a child's story idea into a complete story, then producing a Traditional Chinese picture book with Zhuyin and a narrated video. This repository contains **generic code, workflow guidance, and a blank project template only**. It does not include anyone's finished story, illustrations, audio, or video.

## What it does

1. Use the [story workflow skill](.agents/skills/story-workflow/SKILL.md) to develop the draft from a children's writer's perspective and review it as a 5–7-year-old listener.
2. Use `init` to create a blank 24-page book project. Add your own images and short text, then build separate interior, front-cover, and back-cover PDFs with the bundled Zhuyin font.
3. Supply your own narration recordings to assemble an MP4 video and SRT subtitles.

The toolkit **does not generate illustrations or voices**. The font places Zhuyin beside Chinese characters, but polyphonic readings and tone changes still need manual review. Video captions have one cue per scene; refine their timing before publication.

## Use it with an AI agent

Download the repository and open this folder as the agent's workspace. Agents that read `AGENTS.md` (such as Codex) can follow its pointer to `.agents/skills/story-workflow/SKILL.md`. For other agents, give this instruction explicitly:

> First read `AGENTS.md`, `.agents/skills/story-workflow/SKILL.md`, and `README.en.md`. Help me develop a child's story idea into a complete story for ages 5–7, then plan a 24-page picture book and narrated video. Preserve the child's core plot and author credit. Use `story_studio.py` to create my project. Keep my story, images, and audio under `projects/`; do not add them to the toolkit repository.

Then provide the child's story idea. The agent can help write, plan pages, review Zhuyin, and run the local scripts. Whether it can **make illustrations or synthesize speech directly** depends on the agent's available tools and service access. Without those tools, it can still prepare the story, storyboard, and blank project for you to complete with artwork and recordings. Confirm any online voice provider's data transfer, cost, and license separately.

## Install

Use Python 3.10 or newer. Download and extract the repository from GitHub with **Code → Download ZIP**, or use `git clone`. Open a terminal in the extracted folder.

**Windows PowerShell**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**macOS / Linux**

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

In the following commands, `python` means the environment where you installed the packages. Use `.\.venv\Scripts\python.exe` on Windows or `.venv/bin/python` on macOS/Linux if needed.

## Start your own project

```sh
python story_studio.py init projects/my-story
```

This creates `projects/my-story/project.json` plus `images/` and `audio/`. The `projects/` directory is Git-ignored so your work is not uploaded by accident. Fill in the title, author, cover and back cover, and each page's image and short text. The template starts with 24 pages; you can use any **multiple of eight**. Set `text_position` to `top` or `bottom` for each page. Prepare your own artwork without baked-in Chinese text or Zhuyin.

The required field shape is shown below. This is a schema example, not a finished story:

```json
{
  "title": "Book title",
  "author": "Author",
  "trim_mm": [150, 200],
  "bleed_mm": 3,
  "front_cover": {"image": "images/cover.png", "text": ["Book title"], "text_position": "top"},
  "back_cover": {"image": "images/back_cover.png", "text": ["Back-cover synopsis"], "text_position": "top"},
  "pages": [
    {"image": "images/page_01.png", "text": ["A short page line."], "text_position": "bottom"}
  ],
  "video_scenes": [
    {"image": "images/cover.png", "audio": "audio/scene_00.mp3", "text": "Words spoken in this recording."}
  ]
}
```

Only one page is shown above. Your actual `pages` array must contain a multiple of eight pages. Video scenes can have any count. Each scene's `text` becomes its subtitle and should match its recording. Paths are relative to `project.json` and must stay inside that project folder.

## Build the book

```sh
python story_studio.py check projects/my-story/project.json
python story_studio.py book projects/my-story/project.json
```

The output is `projects/my-story/build/pdf/interior.pdf`, `front_cover.pdf`, and `back_cover.pdf`. Interior pages must be a multiple of eight; covers are separate. The default trim is 150 × 200 mm with 3 mm bleed on every edge, configurable in JSON. PDFs contain TrimBox and BleedBox. Confirm page size, binding, color, and cover requirements with your printer, and inspect every page for Zhuyin accuracy, legibility, and trim safety.

## Build a narrated video

Fill `video_scenes` with each image, MP3 recording, and the words actually spoken. You can record your own voice or use a voice service whose terms permit your intended use. For Mandarin narration, audition natural Taiwan Mandarin voices first. Then run:

```sh
python story_studio.py video projects/my-story/project.json
```

The output is `projects/my-story/build/video/story.mp4` and `story.srt`. Each recording currently yields one subtitle cue. Listen through and refine the timing before uploading. Follow the voice provider's terms and confirm rights to your story, artwork, and sound.

## License

The generic code and documentation in this repository use the [MIT License](LICENSE). The bundled font has separate terms listed in [Third-party notices](THIRD_PARTY_NOTICES.md). This toolkit does not change ownership of stories, images, or audio that you create with it.
