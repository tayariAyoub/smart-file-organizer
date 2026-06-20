"""Safely organize files into category folders."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


CATEGORIES = {
    "Documents": {".doc", ".docx", ".odt", ".pdf", ".ppt", ".pptx", ".txt", ".xls", ".xlsx"},
    "Images": {".bmp", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"},
    "Audio": {".aac", ".flac", ".m4a", ".mp3", ".ogg", ".wav"},
    "Videos": {".avi", ".mkv", ".mov", ".mp4", ".webm"},
    "Archives": {".7z", ".gz", ".rar", ".tar", ".zip"},
    "Code": {".c", ".cpp", ".css", ".h", ".hpp", ".html", ".java", ".js", ".json", ".py", ".ts"},
}

LOG_FILE = ".organizer-history.json"


def category_for(path: Path) -> str:
    """Return the category folder for a file."""
    extension = path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if extension in extensions:
            return category
    return "Other"


def unique_destination(destination: Path) -> Path:
    """Return a non-existing destination without overwriting another file."""
    if not destination.exists():
        return destination

    counter = 1
    while True:
        candidate = destination.with_name(
            f"{destination.stem}_{counter}{destination.suffix}"
        )
        if not candidate.exists():
            return candidate
        counter += 1


def files_to_organize(folder: Path) -> list[Path]:
    """Return regular, visible files in the selected folder."""
    return sorted(
        (
            item
            for item in folder.iterdir()
            if item.is_file() and item.name != LOG_FILE and not item.name.startswith(".")
        ),
        key=lambda item: item.name.lower(),
    )


def build_plan(folder: Path) -> list[tuple[Path, Path]]:
    """Build a move plan without changing the filesystem."""
    plan: list[tuple[Path, Path]] = []
    reserved: set[Path] = set()

    for source in files_to_organize(folder):
        target_dir = folder / category_for(source)
        target = target_dir / source.name

        while target.exists() or target in reserved:
            target = unique_destination(target)
            if target in reserved:
                target = target.with_name(
                    f"{target.stem}_copy{target.suffix}"
                )

        reserved.add(target)
        plan.append((source, target))

    return plan


def organize(folder: Path, dry_run: bool = False) -> list[dict[str, str]]:
    """Organize files and return move records."""
    folder = folder.expanduser().resolve()
    if not folder.is_dir():
        raise ValueError(f"Folder does not exist: {folder}")

    moves: list[dict[str, str]] = []
    for source, target in build_plan(folder):
        print(f"{'[PREVIEW] ' if dry_run else ''}{source.name} -> {target.parent.name}/{target.name}")
        if not dry_run:
            target.parent.mkdir(exist_ok=True)
            shutil.move(str(source), str(target))
            moves.append({"source": str(source), "destination": str(target)})

    if moves:
        history_path = folder / LOG_FILE
        history = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "moves": moves,
        }
        history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")

    return moves


def undo(folder: Path) -> int:
    """Undo the most recent organization run."""
    folder = folder.expanduser().resolve()
    history_path = folder / LOG_FILE
    if not history_path.exists():
        raise ValueError("No organizer history was found.")

    history = json.loads(history_path.read_text(encoding="utf-8"))
    restored = 0

    for move in reversed(history["moves"]):
        source = Path(move["source"])
        destination = Path(move["destination"])
        if destination.exists() and not source.exists():
            shutil.move(str(destination), str(source))
            restored += 1

    for child in folder.iterdir():
        if child.is_dir() and not any(child.iterdir()):
            child.rmdir()

    history_path.unlink()
    return restored


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Organize files by type without overwriting existing files."
    )
    parser.add_argument("folder", type=Path, help="Folder to organize")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without moving files",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="Undo the most recent organization run",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        if args.undo:
            count = undo(args.folder)
            print(f"Restored {count} file(s).")
        else:
            moves = organize(args.folder, dry_run=args.dry_run)
            if not moves and not args.dry_run:
                print("No files needed organizing.")
    except ValueError as error:
        raise SystemExit(f"Error: {error}") from error


if __name__ == "__main__":
    main()
