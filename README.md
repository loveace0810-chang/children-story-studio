# 兒童故事工坊

[English](README.en.md) · 繁體中文

把孩子的故事點子完善成完整故事，再製作繁體中文注音繪本與有聲影片的開放工具。這個儲存庫只包含**通用程式、工作流程與空白範本**；沒有任何使用者創作的故事、插畫、聲音或成品。

## 可以做什麼

1. 依照 [故事製作 skill](.agents/skills/story-workflow/SKILL.md)，以兒童故事作家和 5～7 歲聽眾的角度完善故事。
2. 用 `init` 建立空白的 24 頁繪本專案。完成每頁插畫與短句後，用附帶的注音字型輸出獨立內頁、封面、封底 PDF。
3. 自行準備配音音檔，依場景順序組成 MP4 影片與 SRT 字幕。

工具**不會自動生成插畫或配音**。字型可以在漢字右側顯示注音，但多音字和變調仍須人工校對。影片字幕以一個場景為一段，正式上架前應按聲音再細分和調整時間。

## 交給 AI agent 使用

下載後，讓 agent 以此資料夾為工作目錄。會讀取 `AGENTS.md` 的 agent（例如 Codex）可依其中指示載入 `.agents/skills/story-workflow/SKILL.md`。其他 agent 請直接給它這句話：

> 請先閱讀 `AGENTS.md`、`.agents/skills/story-workflow/SKILL.md` 和 `README.md`。幫我把孩子的故事點子完善成適合 5～7 歲的故事，先給我完整故事，再規劃 24 頁繪本與有聲影片。請保留孩子的核心情節與作者署名。使用 `story_studio.py` 建立我的專案；故事、圖片與聲音都放在 `projects/`，不要加入工具儲存庫。

接著貼上孩子的故事點子。agent 可以協助寫作、安排分頁、檢查注音與執行本機程式；能否**直接畫圖或合成語音**取決於該 agent 是否有相應工具及服務權限。沒有這些工具時，仍可先完成文本、分鏡與空白專案，再由使用者補上插畫和錄音。任何線上配音服務的傳送、費用與授權也需另行確認。

## 安裝

需要 Python 3.10 以上。先用 GitHub 的 **Code → Download ZIP** 下載並解壓，或使用 `git clone`。在專案資料夾開啟終端機：

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

以下範例用 `python` 表示剛安裝好套件的 Python；Windows 可換成 `.\.venv\Scripts\python.exe`，macOS / Linux 可換成 `.venv/bin/python`。

## 建立你的故事專案

```sh
python story_studio.py init projects/my-story
```

這會建立 `projects/my-story/project.json`、`images/` 和 `audio/`。`projects/` 已被 Git 忽略，避免意外上傳你的故事。請在 JSON 裡填入書名、作者、封面／封底、每頁的圖片與短句。預設為 24 頁；可改為其他 **8 的倍數**。每頁可以設定 `text_position` 為 `top` 或 `bottom`。圖片要自行準備，且不要把中文字與注音畫在圖片裡。

必要欄位示意（以下只是欄位格式，並非故事內容）：

```json
{
  "title": "書名",
  "author": "作者",
  "trim_mm": [150, 200],
  "bleed_mm": 3,
  "front_cover": {"image": "images/cover.png", "text": ["書名"], "text_position": "top"},
  "back_cover": {"image": "images/back_cover.png", "text": ["封底簡介"], "text_position": "top"},
  "pages": [
    {"image": "images/page_01.png", "text": ["第一頁短句。"], "text_position": "bottom"}
  ],
  "video_scenes": [
    {"image": "images/cover.png", "audio": "audio/scene_00.mp3", "text": "這一段實際說出的話。"}
  ]
}
```

上面只示範一頁；實際 `pages` 必須列出 8 的倍數頁數。影片場景數不限，`text` 用於字幕，應與音檔說出的內容一致。所有路徑都相對於 `project.json`，且必須位於該專案資料夾內。

## 輸出繪本

```sh
python story_studio.py check projects/my-story/project.json
python story_studio.py book projects/my-story/project.json
```

輸出會出現在 `projects/my-story/build/pdf/`：`interior.pdf`、`front_cover.pdf`、`back_cover.pdf`。內頁頁數需為 8 的倍數，封面與封底另算。預設成品尺寸為 150 × 200 mm，四邊出血 3 mm，可在 JSON 中調整。輸出有 PDF TrimBox 和 BleedBox。送印前請與印刷廠確認尺寸、裝訂、色彩與封面規格，並逐頁檢查注音、文字對比及裁切安全。

## 輸出有聲影片

在 `video_scenes` 依序填入每段圖片、MP3 音檔與實際旁白文字。聲音可由本人錄製，或透過你有權使用的配音服務取得；選擇中文語音時，建議先試聽自然的台灣華語聲線。再執行：

```sh
python story_studio.py video projects/my-story/project.json
```

影片和字幕會出現在 `projects/my-story/build/video/story.mp4` 與 `story.srt`。字幕目前按每段錄音長度產生一個時間區間；上傳平台前請聽一遍並校正。使用線上語音服務與發布成品時，請遵守該服務的條款及素材權利。

## 授權

本儲存庫的通用程式與說明採 [MIT 授權](LICENSE)。內附字型有其各自授權，詳見 [第三方聲明](THIRD_PARTY_NOTICES.md)。你自己製作的故事、圖片和聲音**不會因使用本工具而改變權利歸屬**。
