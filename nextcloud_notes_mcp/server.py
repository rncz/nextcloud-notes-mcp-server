from typing import Any
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from webdav3.client import Client
from typing import List, Dict
import httpx
import posixpath
import tempfile
import os
import re

mcp = FastMCP("notes-mcp")

load_dotenv()

webdav_hostname = os.getenv("webdav_hostname")
webdav_username = os.getenv("webdav_username")
webdav_password = os.getenv("webdav_password")

options = {
    'webdav_hostname': f"{webdav_hostname}{webdav_username}",
    'webdav_login':    webdav_username,
    'webdav_password': webdav_password
}

client = Client(options)

def _ensure_remote_dir(path: str):
    """Ensure that a remote directory exists in Nextcloud."""
    try:
        client.mkdir(path)
    except Exception:
        # Folder probably already exists → ignore
        pass


@mcp.tool()
def check_webdav_login() -> str:
    """
    Check if WebDAV login is successful.
    Returns a message indicating success or failure.
    """
    try:
        if client.check():  # returns True if login works
            return "✅ WebDAV login successful!"
        else:
            return "❌ WebDAV login failed!"
    except Exception as e:
        return f"❌ WebDAV login failed: {e}"

@mcp.tool()
def ensure_notes_folder_exists() -> str:
    """
    Ensure that the /Notes folder exists in Nextcloud.
    Creates it if it doesn't exist.
    """
    _ensure_remote_dir("/Notes")
    return "/Notes folder exists or created successfully."

@mcp.tool()
def list_uncategorized_notes() -> List[str]:
    """
    List all Markdown (.md) files directly inside /Notes (not in subfolders).
    """
    items = client.list("/Notes")
    return [f for f in items if f.endswith('.md')]

@mcp.tool()
def list_categories() -> List[str]:
    """
    List all categories (directories) inside /Notes.
    """
    items = client.list("/Notes")
    # Keep only directories (exclude .md files)
    return [f for f in items if not f.endswith('.md')]

@mcp.tool()
def list_notes_of_a_category(category_name: str) -> List[str]:
    """
    List all notes in a given category inside /Notes.

    Args:
        category_name: The subfolder name inside /Notes

    Returns:
        List of note filenames (.md) in that category.
    """
    notes_path = f"/Notes/{category_name}"
    try:
        items = client.list(notes_path)
    except Exception as e:
        return [f"Error: {str(e)}"]

    # Keep only Markdown files
    return [f for f in items if f.endswith('.md')]

@mcp.tool()
def read_note(filename: str, category: str | None = None) -> str:
    """
    Read a Markdown (.md) file.

    Args:
        filename: Name of the note file, e.g., "note1.md"
        category: Optional category folder. If None, read from /Notes root.

    Returns:
        Content of the note as a string.
    """
    full_path = f"/Notes/{category}/{filename}" if category else f"/Notes/{filename}"
    tmp_path = os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()) + ".tmp")

    client.download_sync(remote_path=full_path, local_path=tmp_path)
    with open(tmp_path, "r", encoding="utf-8") as f:
        content = f.read()
    os.remove(tmp_path)
    return content

@mcp.tool()
def edit_note(filename: str, new_content: str, category: str | None = None) -> str:
    """
    Edit a Markdown (.md) file, updating its content. Always overwrites the old file.
    """
    full_path = f"/Notes/{category}/{filename}" if category else f"/Notes/{filename}"
    tmp_path = os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()) + ".tmp")

    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    # Remove existing file if it exists
    if client.check(remote_path=full_path):
        client.clean(remote_path=full_path)

    # Upload new content
    client.upload_sync(remote_path=full_path, local_path=tmp_path)
    os.remove(tmp_path)

    return f"Note updated successfully: {full_path}"


@mcp.tool()
def create_note(filename: str, content: str, category: str | None = None) -> str:
    """
    Create a new Markdown (.md) note.

    - If category is None → stored in /Notes/<filename>
    - If category is provided → stored in /Notes/<category>/<filename>
    """
    # Determine full paths
    if category:
        full_dir = f"/Notes/{category}"
        full_path = f"{full_dir}/{filename}"
        _ensure_remote_dir(full_dir)
    else:
        full_path = f"/Notes/{filename}"

    tmp_path = os.path.join(tempfile.gettempdir(), next(tempfile._get_candidate_names()) + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(content)

    client.upload_sync(remote_path=full_path, local_path=tmp_path)
    os.remove(tmp_path)
    return f"Note created successfully: {full_path}"

@mcp.tool()
def delete_note(filename: str, category: str | None = None) -> str:
    """
    Delete a note file inside Notes.
    """
    full_path = f"Notes/{category}/{filename}" if category else f"Notes/{filename}"
    try:
        client.clean(full_path)
    except Exception as e:
        return f"Failed to delete note: {str(e)}"
    return f"Note deleted successfully: {full_path}"

@mcp.tool()
def rename_note(filename: str, new_filename: str, category: str | None = None) -> str:
    """
    Rename a Markdown (.md) note inside Notes or a category.
    Overwrites the target if it already exists.
    """
    source_path = f"Notes/{category}/{filename}" if category else f"Notes/{filename}"
    target_path = f"Notes/{category}/{new_filename}" if category else f"Notes/{new_filename}"

    try:
        client.move(source_path, target_path, overwrite=True)
    except Exception as e:
        return f"Failed to rename note: {str(e)}"

    return f"Note renamed successfully: {source_path} → {target_path}"

@mcp.tool()
def create_category(category_name: str) -> str:
    """
    Create a new category inside Notes by creating a subdirectory.
    """
    full_path = f"Notes/{category_name}"
    _ensure_remote_dir(full_path)
    return f"Category created successfully: {full_path}"

@mcp.tool()
def edit_category(old_name: str, new_name: str) -> str:
    """
    Rename an existing category inside Notes.

    Args:
        old_name: Current name of the category.
        new_name: New name for the category.
    """
    old_path = f"Notes/{old_name}"
    new_path = f"Notes/{new_name}"
    try:
        client.move(old_path, new_path)
    except Exception as e:
        return f"Failed to rename category: {str(e)}"
    return f"Category renamed successfully: {old_path} → {new_path}"

@mcp.tool()
def delete_category(category_name: str) -> str:
    """
    Delete a category folder inside Notes.
    """
    full_path = f"Notes/{category_name}"
    try:
        client.clean(full_path)  # works for folders too
    except Exception as e:
        return f"Failed to delete category: {str(e)}"
    return f"Category deleted successfully: {full_path}"


# --- Main entry ---
def main():
    mcp.run()

if __name__ == "__main__":
    main()