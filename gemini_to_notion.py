import os
import sys
import re
import argparse
from dotenv import load_dotenv

from google import genai
from notion_client import Client

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_FOLDER_PAGE_ID = os.getenv("NOTION_FOLDER_PAGE_ID")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


def process_with_gemini(youtube_url: str, prompt_template: str | None = None) -> tuple[str, str]:
    """
    Summarize the YouTube video using the Gemini Interactions API.
    Passes the YouTube URL in the structured input payload format.
    """
    client = genai.Client(api_key=GEMINI_API_KEY)

    system_instruction = (
        "You are an expert video summarizer. "
        "On the very first line of your output, extract and provide the exact official title of the YouTube video "
        "prefixed with 'TITLE: '. "
        "Following that, provide a structured and comprehensive summary using Markdown headers (#, ##, ###), bullet points, and paragraphs."
    )

    if not prompt_template:
        prompt_text = "Please summarize the video."
    else:
        prompt_text = prompt_template.format(url=youtube_url)

    full_instruction = f"{system_instruction}\n\n{prompt_text}"

    # Interactions API structure passing text and video objects explicitly
    interaction = client.interactions.create(
        model=GEMINI_MODEL,
        input=[
            {"type": "text", "text": full_instruction},
            {
                "type": "video",
                "uri": youtube_url
            }
        ]
    )

    output_text = interaction.output_text or ""
    lines = output_text.splitlines()

    extracted_title = "Auto note from YouTube video"
    markdown_body = output_text

    # Extract title prefix if present on the first line
    if lines and lines[0].startswith("TITLE:"):
        extracted_title = lines[0].replace("TITLE:", "").strip()
        markdown_body = "\n".join(lines[1:]).strip()

    return extracted_title, markdown_body


def markdown_to_notion_blocks(md_text: str) -> list[dict]:
    """Convert clean Markdown into official Notion API Block objects."""
    blocks = []
    lines = md_text.splitlines()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Format rich text (handles basic **bold** syntax)
        rich_text = []
        parts = re.split(r'(\*\*.*?\*\*)', stripped)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                rich_text.append({
                    "type": "text",
                    "text": {"content": part[2:-2]},
                    "annotations": {"bold": True}
                })
            elif part:
                rich_text.append({
                    "type": "text",
                    "text": {"content": part}
                })

        # Heading 1
        if stripped.startswith("# "):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {"rich_text": [{"type": "text", "text": {"content": stripped[2:].strip()}}]}
            })
        # Heading 2
        elif stripped.startswith("## "):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": stripped[3:].strip()}}]}
            })
        # Heading 3 (and fallback for H4)
        elif stripped.startswith("### ") or stripped.startswith("#### "):
            content = re.sub(r"^#{3,4}\s*", "", stripped)
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": [{"type": "text", "text": {"content": content}}]}
            })
        # Bullet Points
        elif stripped.startswith("- ") or stripped.startswith("* "):
            content = stripped[2:].strip()
            bullet_rich_text = []
            bullet_parts = re.split(r'(\*\*.*?\*\*)', content)
            for part in bullet_parts:
                if part.startswith('**') and part.endswith('**'):
                    bullet_rich_text.append({
                        "type": "text",
                        "text": {"content": part[2:-2]},
                        "annotations": {"bold": True}
                    })
                elif part:
                    bullet_rich_text.append({
                        "type": "text",
                        "text": {"content": part}
                    })

            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": bullet_rich_text}
            })
        # Numbered Lists
        elif re.match(r"^\d+\.\s", stripped):
            content = re.sub(r"^\d+\.\s", "", stripped)
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": [{"type": "text", "text": {"content": content}}]}
            })
        # Default Paragraph
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": rich_text}
            })

    return blocks


def create_notion_page(title: str, markdown_content: str) -> dict:
    """Create a page in Notion using official Notion REST API blocks."""
    notion = Client(auth=NOTION_TOKEN)

    blocks = markdown_to_notion_blocks(markdown_content)

    # Notion API allows up to 100 blocks during initial page creation
    initial_blocks = blocks[:100]

    new_page = notion.pages.create(
        parent={"type": "page_id", "page_id": NOTION_FOLDER_PAGE_ID},
        properties={
            "title": [
                {
                    "type": "text",
                    "text": {"content": title}
                }
            ]
        },
        children=initial_blocks
    )

    # Append remaining blocks if total blocks > 100
    if len(blocks) > 100:
        page_id = new_page["id"]
        for i in range(100, len(blocks), 100):
            chunk = blocks[i:i + 100]
            notion.blocks.children.append(block_id=page_id, children=chunk)

    return new_page


def main():
    parser = argparse.ArgumentParser(
        description="Summarize a YouTube video with Gemini Interactions API → Notion."
    )
    parser.add_argument(
        "url",
        nargs="?",
        default=os.getenv("DEFAULT_EXTERNAL_URL"),
        help="YouTube video URL to summarize."
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Custom note title in Notion."
    )
    parser.add_argument(
        "--prompt",
        default=None,
        help="Path to a .txt file containing a custom prompt template for Gemini."
    )
    args = parser.parse_args()

    if not GEMINI_API_KEY or not NOTION_TOKEN or not NOTION_FOLDER_PAGE_ID:
        print("Error: Missing required environment variables in .env", file=sys.stderr)
        sys.exit(1)

    if not args.url:
        print("Error: No YouTube URL provided.", file=sys.stderr)
        sys.exit(1)

    prompt_template = None
    if args.prompt:
        with open(args.prompt, "r", encoding="utf-8") as f:
            prompt_template = f.read()

    print("Generating summary and title using Gemini Interactions API...")
    generated_title, processed_text = process_with_gemini(args.url, prompt_template)

    final_title = args.title if args.title else generated_title

    print(f"Title: {final_title}")
    print("Uploading formatted note to Notion...")
    notion_data = create_notion_page(final_title, processed_text)

    print("Note created successfully in Notion!")
    print("Note URL:", notion_data.get("url"))


if __name__ == "__main__":
    main()
