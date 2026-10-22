---
name: story-workflow
description: Develop a child's rough story into a complete Traditional Chinese story, then adapt it into a Zhuyin picture book and narrated video using this toolkit.
---

# Children's story workflow

## Complete the story

Act as a children's story writer. Preserve the child's characters, main events, intended ending, and author credit. Fill gaps with clear cause and effect, concrete action, feelings, dialogue, and age-appropriate detail. Keep a complete prose version separate from page text and narration. Review it as a 5–7-year-old listener: check whether the sequence, time jumps, vocabulary, and ending make sense. This is an editorial perspective, not a claim of testing with a real child.

## Make the picture book

Act as the picture-book writer and illustrator. Divide the plot into page-sized beats, keeping the 5–7-year-old reader's understanding in mind. Plan the text placement before drawing. Make illustrations without generated Chinese lettering or Zhuyin, then typeset real Traditional Chinese text over the art. Use the bundled BpmfHuninn font for right-side Zhuyin, and inspect every rendered page for reading, tone, alignment, contrast, continuity, and trim safety. Check polyphonic readings and tone changes manually; font defaults are not always correct. Use 8-page multiples for interior pages, with separate front and back covers. The toolkit's `init` command creates a blank 24-page project.

Help produce the pictures too. First define a compact character and visual reference (appearance, clothes, palette, setting, and style) and map each page to one visible action and emotion. If an image-generation or drawing tool is available, create the cover, back cover, and page illustrations; keep recurring characters consistent and reserve safe areas for later text. Save them under the project's `images/` using the filenames in `project.json`. If no image tool is available, give the user page-by-page art briefs and prompts suitable for their chosen tool, then incorporate the resulting images. Do not stop after a generic prompt list when actual art can be made. Review compositions at picture-book size, especially hands, props, scene continuity, and important details near the gutter or trim.

Review the book as a young reader: do the pictures and short lines show what happened, why the character changed, and how the ending follows? Revise unclear pages before printing.

## Make the narrated video

Act as a video storyteller. Adapt the full story into natural spoken Traditional Chinese, with a direct opening that names the story and a gentle ending that helps children understand its point. Choose a natural Taiwan Mandarin voice, male or female, and audition a short sample when possible. Shape pace, pauses, and emphasis as though speaking to children in person. Review the finished audio and images as a 5–7-year-old listener: can the child follow the plot and stay engaged? Do not claim a real child has listened unless that happened.

Help the user complete the audio stage rather than merely asking for MP3 files. Offer a few voice candidates when a service makes them available, with the same short passage for comparison. Check accent, warmth, pace, clarity, emotional variation, and recording noise. Do not default to a voice or provider used in a previous project. Select among accessible text-to-speech tools based on Taiwan Mandarin quality, output rights, cost, and the user's preference. With authorization to send story text, guide or perform scene-by-scene generation: use one approved passage for audition, choose a voice and model, generate each scene, listen and revise delivery, then save the chosen MP3 files in scene order. ElevenLabs is one example, not a requirement. Only use model-specific performance tags when supported, and keep tags out of displayed subtitles. Consult the selected provider's current documentation because interfaces and models change.

The toolkit assembles supplied illustrations and audio; it does not generate voices or illustrations by itself. Place audio paths and matching spoken text in `video_scenes` in `project.json`, build the video, then listen through and correct subtitle timing. If the agent lacks image or voice generation tools, explain the exact inputs needed and guide the user through obtaining them. Check the provider's terms before sending story text to an online service or publishing generated audio. Never purchase a plan or publish externally without authorization.

See the repository README for the `project.json` format and build commands. Never include a user's private story, generated pictures, audio, or video in the toolkit repository without their explicit instruction.
