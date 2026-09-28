# Gemini Notion

Summarize a YouTube video with the Gemini API and save the summary as a new page in Notion.

## Features

- Passes a YouTube video link directly to Gemini, which fetches and summarizes the video
- Creates a new Notion page under a parent page (folder)
- Optional custom prompt template via `--prompt`

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- A Google AI (Gemini) API key
- A Notion integration token

## Installation

```bash
git clone https://github.com/yourusername/gemini-notion.git
cd gemini-notion

uv sync
```

## Configuration

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

```env
GEMINI_API_KEY=your_gemini_api_key
NOTION_TOKEN=your_notion_integration_token
NOTION_FOLDER_PAGE_ID=your_notion_folder_page_id
```

Optional variables:

| Variable | Description | Default |
| --- | --- | --- |
| `GEMINI_MODEL` | Gemini model to use | `gemini-3.6-flash` |
| `DEFAULT_EXTERNAL_URL` | URL used when no argument is passed | none |

### Getting your keys

- **Gemini API key:** create one at https://aistudio.google.com/apikey
- **Notion token:** create an integration at https://www.notion.so/my-integrations and give it access to the parent page.
- **Folder page ID:** the ID of the Notion page under which notes are created (the last part of the page URL).

## Usage

Summarize a YouTube video and save the result to Notion:

```bash
uv run python gemini_to_notion.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

With a custom title:

```bash
uv run python gemini_to_notion.py "https://www.youtube.com/watch?v=VIDEO_ID" --title "My note title"
```

With a custom prompt template (a txt file):

```bash
uv run python gemini_to_notion.py "https://www.youtube.com/watch?v=VIDEO_ID" --prompt prompt.txt
```

If no URL is passed, `DEFAULT_EXTERNAL_URL` from `.env` is used.

## How it works

1. **Summarize** — sends the prompt (default: `summarize pls <url>`) to Gemini with your YouTube link; Gemini fetches the video itself and returns a summary.
2. **Save** — creates a new Notion page under `NOTION_FOLDER_PAGE_ID`, splitting the summary into paragraph blocks.

## Project structure

```
.
├── gemini_to_notion.py   # main script
├── gemini-notion.sh      # convenience wrapper using uv run
├── pyproject.toml        # project metadata and dependencies
├── uv.lock               # locked dependency versions
└── .env                  # environment variables (not committed)
```

## License

MIT
