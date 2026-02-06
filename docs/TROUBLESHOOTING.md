# Troubleshooting Engineering Decision Logger

This document provides solutions for common issues encountered while using EDL.

## 1. 'edl' command not found

If you receive a "command not found" error after installation:

**Solution:**
- Ensure you installed the package in editable mode: `pip install -e .`
- Check if your Python scripts directory is in your system's PATH.
- Try running the tool using: `python -m src.cli`

## 2. Git Integration Errors

If EDL fails to capture a Git commit hash:

**Solution:**
- Ensure you are running the command inside a Git repository.
- Make sure you have at least one commit in your repository.
- Verify that `git` is installed and accessible from your terminal.

## 3. Database Errors

If you encounter issues with the SQLite database (e.g., locked database or corruption):

**Solution:**
- Ensure no other process is holding a lock on `edl.db`.
- If the database is corrupted, you can delete `edl.db` and start fresh (Warning: this will delete all recorded decisions).
- The Markdown files in `docs/ADR/` are your source of truth and will remain even if the database is deleted.

## 4. Hook Installation Fails

If `edl install-hooks` fails:

**Solution:**
- Check if the `.git/hooks` directory exists in your project.
- Ensure you have write permissions to the `.git/hooks` directory.
