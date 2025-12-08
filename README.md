# Nextcloud Notes MCP Server

The unofficial **Nextcloud Notes MCP Server** is a MCP server for the Nextcloud Notes app that lets a **Large Language Model (LLM)** do the heavy lifting for your notes.

Simply tell the LLM what to do with your notes — organize, summarize, rewrite, or perform any custom task — and it will execute your instructions automatically.

## Features

* 💻 **Fully Local Possible** – Run the MCP Server and LLM models entirely on your own PC; no cloud needed.
* 🤖 **LLM-Powered Note Management** – Automate tasks like summarization, categorization, rewriting, or translations.
* 🌐 **Nextcloud Integration via WebDAV** – Access your notes directly through Nextcloud using the WebDAV protocol.
* ⚡ **Boost Productivity** – Save time by letting the LLM handle repetitive or complex note tasks.

Sure! Here is an updated version of the **Installation** section that clearly separates **macOS/Linux** and **Windows** steps.

You can copy-paste this into your README:

## Installation

### 🐧 macOS / Linux

1. **Download the repository**:

   ```bash
   git clone https://github.com/rncz/nextcloud-notes-mcp-server.git
   ```

2. **Configure environment**:

   ```bash
   cd nextcloud-notes-mcp-server
   cp env_sample .env
   ```

   *Open `.env` and enter your Nextcloud WebDAV URL, username, and password.*

3. **Set up the Python environment and install the package**:

   ```bash
   uv venv
   uv tool install -e .
   ```

4. **Add MCP server to your LLM software** (example for LM Studio):

   ```json
   {
     "mcpServers": {
       "nextcloud-notes-mcp": {
         "command": "uvx",
         "args": ["nextcloud-notes-mcp"]
       }
     }
   }
   ```

5. **Test your setup** — Use a model with tool calling enabled and ask it to access your notes.

### 🪟 Windows (PowerShell)

1. **Download the repository**:

   ```powershell
   git clone https://github.com/rncz/nextcloud-notes-mcp-server.git
   ```

2. **Configure environment**:

   ```powershell
   cd nextcloud-notes-mcp-server
   copy env_sample .env
   ```

   *Edit `.env` in your text editor and enter your WebDAV URL, username, and password.*

3. **Set up the Python environment and install the package**:

   ```powershell
   uv venv
   uv tool install -e .
   ```

4. **Add MCP server to your LLM software** (example for LM Studio):

   ```json
   {
     "mcpServers": {
       "nextcloud-notes-mcp": {
         "command": "uvx",
         "args": ["nextcloud-notes-mcp"]
       }
     }
   }
   ```

5. **Test your setup** — Ask the LLM to check WebDAV login.

### 🗂️ Nextcloud WebDAV Notes Tools (12 tools)

| Tool                         | Description                                                                                |
| ---------------------------- | ------------------------------------------------------------------------------------------ |
| `check_webdav_login`         | Check if WebDAV authentication works and return a success/failure message                  |
| `ensure_notes_folder_exists` | Ensure the `/Notes` folder exists; create it if missing                                    |
| `list_uncategorized_notes`   | List `.md` notes directly inside `/Notes`, excluding subfolders                            |
| `list_categories`            | List all category folders inside `/Notes` (directories only)                               |
| `list_notes_of_a_category`   | List `.md` notes inside a given category folder                                            |
| `read_note`                  | Read the full content of a note from `/Notes` or a category folder                         |
| `edit_note`                  | Replace an existing note’s full content with new text                                      |
| `create_note`                | Create a new Markdown note in `/Notes` or a category folder (auto-create folder if needed) |
| `delete_note`                | Delete a note from `/Notes` or a category folder                                           |
| `rename_note`                | Rename a note within `/Notes` or inside a category                                         |
| `create_category`            | Create a new category folder inside `/Notes`                                               |
| `edit_category`              | Rename an existing category inside `/Notes`                                                |
| `delete_category`            | Delete a category and all notes inside it                                                  |
