## Setup Steps in Termux

1. **Update Termux packages:**
   ```bash
   pkg update && pkg upgrade
   ```

2. **Install Python and required tools:**
   ```bash
   pkg install python git
   ```

3. **Clone the repository:**
   ```bash
   git clone https://github.com/slidingsoul/gemini-notion.git
   cd gemini-notion
   ```

4. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Configure environment variables:**
   Create a `.env` file with your credentials:
   ```bash
   cat > .env << EOF
   GEMINI_API_KEY=your_gemini_api_key
   NOTION_TOKEN=your_notion_integration_token
   NOTION_FOLDER_PAGE_ID=your_notion_folder_page_id
   EOF
   ```

7. **Run the script:**
   ```bash
   python gemini_to_notion.py "https://www.youtube.com/watch?v=VIDEO_ID"
   ```

## ⚠️ Important Considerations

- **Python 3.10+**: Termux typically installs a recent Python version, which should work.
- **Network access**: Make sure you have internet connectivity for API calls to Gemini and Notion.
- **File storage**: All files will be stored in your Termux home directory (usually `/data/data/com.termux/files/home`).
- **Persistence**: Keep Termux running while the script executes, or use `nohup` for background execution.

The dependencies (`requests`, `google-genai`, `python-dotenv`, `notion_client`) are all pure Python packages with no native compilation requirements, so they should install smoothly in Termux.
