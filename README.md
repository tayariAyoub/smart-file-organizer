# Smart File Organizer

A safe command-line tool that organizes files into folders such as
`Documents`, `Images`, `Audio`, `Videos`, `Archives`, `Code`, and `Other`.

This project demonstrates practical Python development with filesystem
operations, command-line arguments, JSON history, error handling, and automated
tests.

## Features

- Preview every change with `--dry-run`
- Never overwrite an existing file
- Undo the latest organization run
- Ignore hidden files and the history file
- Work with only the Python standard library
- Include automated tests

## Usage

Preview changes:

```bash
python organizer.py "C:\Users\YourName\Downloads" --dry-run
```

Organize the folder:

```bash
python organizer.py "C:\Users\YourName\Downloads"
```

Undo the latest run:

```bash
python organizer.py "C:\Users\YourName\Downloads" --undo
```

## Run the tests

From the project folder:

```bash
python -m unittest discover -s tests -v
```

## Safety

Always use `--dry-run` first on important folders. The tool records its latest
successful move operation in `.organizer-history.json` so it can restore moved
files with `--undo`.

## Possible future improvements

- Custom categories from a configuration file
- Graphical interface
- Duplicate-file detection
- Multiple undo history entries

## Author

Ayoub Tayari  
Computer Engineering student at RWTH Aachen University
