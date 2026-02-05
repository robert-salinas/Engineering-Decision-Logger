# EDL Architecture

This document describes the high-level architecture of the Engineering Decision Logger (EDL).

## Components

### CLI (`src/cli.py`)
The entry point of the application. Built with **Typer**. It handles user input and displays results using **Rich**.

### Decision Manager (`src/logger/manager.py`)
The core logic of the application. It coordinates:
- Storing decisions in a **SQLite** database using **SQLModel**.
- Generating ADR files in Markdown format.
- Searching and listing decisions.

### ADR Formatter (`src/adr_formatter/formatter.py`)
Handles the transformation of decision data into Markdown files using **Jinja2** templates.

### Git Integration (`src/git_integration/git_manager.py`)
Provides tools to interact with the Git repository, such as:
- Retrieving the current commit hash.
- Installing git hooks to automate decision checks.

## Data Flow

1. User runs `edl log`.
2. CLI prompts for decision details.
3. `GitManager` captures the current commit hash.
4. `DecisionManager` saves the data to `edl.db`.
5. `ADRFormatter` generates a `.md` file in `docs/ADR/`.
6. User commits the new ADR file.
