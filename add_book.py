#!/usr/bin/env python3
"""Scaffold a new puzzle book: create folder, generate HTML from JSON, and make QR code."""

import argparse
import json
import os
import sys

from generate_qr import generate_qr

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "templates", "book-template.html")
GITHUB_USERNAME = "carverprints"


def build_grid_html(grid, highlights=None):
    """Build an HTML table for a word search grid.

    Args:
        grid: 2D list of letters.
        highlights: optional set of (row, col) tuples for highlighted (solution) cells.
    """
    highlights = highlights or set()
    rows = []
    for r, row in enumerate(grid):
        cells = []
        for c, letter in enumerate(row):
            cls = ' class="hl"' if (r, c) in highlights else ""
            cells.append(f"<td{cls}>{letter.upper()}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return "<table class=\"grid\">" + "".join(rows) + "</table>"


def build_page(book_name, puzzles):
    """Build the full HTML page from the template and puzzle data."""
    with open(TEMPLATE_PATH, "r") as f:
        template = f.read()

    # Navigation links
    nav_links = "".join(
        f'<a href="#puzzle-{i+1}">{i+1}</a>' for i in range(len(puzzles))
    )

    # Puzzle sections
    sections = []
    for i, puzzle in enumerate(puzzles):
        num = i + 1
        title = puzzle.get("title", f"Puzzle {num}")

        # Build grid
        grid_html = ""
        if "grid" in puzzle:
            hl = set()
            for coord in puzzle.get("highlights", []):
                hl.add((coord[0], coord[1]))
            grid_html = (
                '<div class="grid-container">'
                + build_grid_html(puzzle["grid"], hl)
                + "</div>"
            )

        # Word list
        words_html = ""
        if "words" in puzzle:
            word_str = ", ".join(puzzle["words"])
            words_html = f'<div class="word-list"><strong>Words:</strong> {word_str}</div>'

        section = (
            f'<div class="puzzle-section" id="puzzle-{num}">'
            f"<h2>{title}</h2>"
            f"{grid_html}"
            f"{words_html}"
            f'<a class="back-top" href="#top">Back to top</a>'
            f"</div>"
        )
        sections.append(section)

    html = template.replace("{{BOOK_NAME}}", book_name)
    html = html.replace("{{NAV_LINKS}}", nav_links)
    html = html.replace("{{PUZZLE_SECTIONS}}", "\n\n    ".join(sections))
    return html


def create_placeholder_json(book_id, book_name, num_puzzles):
    """Create a sample JSON file showing the expected format."""
    sample = {
        "book_name": book_name,
        "puzzles": [],
    }
    for i in range(num_puzzles):
        sample["puzzles"].append({
            "title": f"Puzzle {i + 1}",
            "grid": [
                ["A", "B", "C", "D", "E"],
                ["F", "G", "H", "I", "J"],
                ["K", "L", "M", "N", "O"],
                ["P", "Q", "R", "S", "T"],
                ["U", "V", "W", "X", "Y"],
            ],
            "highlights": [[0, 0], [1, 1], [2, 2], [3, 3], [4, 4]],
            "words": ["SAMPLE", "WORDS"],
        })
    path = os.path.join(SCRIPT_DIR, book_id, f"{book_id}.json")
    with open(path, "w") as f:
        json.dump(sample, f, indent=2)
    return path


def main():
    parser = argparse.ArgumentParser(description="Add a new puzzle book.")
    parser.add_argument("book_id", help="Folder name for the book (e.g. book1)")
    parser.add_argument("--name", required=True, help="Display name of the book")
    parser.add_argument("--json", dest="json_file", help="Path to solutions JSON file (optional — if omitted, creates a placeholder)")
    parser.add_argument("--puzzles", type=int, default=10, help="Number of puzzles (used only when creating placeholder JSON, default 10)")
    args = parser.parse_args()

    book_dir = os.path.join(SCRIPT_DIR, args.book_id)
    images_dir = os.path.join(book_dir, "images")

    # Create directories
    os.makedirs(images_dir, exist_ok=True)
    print(f"Created: {book_dir}/")
    print(f"Created: {images_dir}/")

    # Load or create JSON
    if args.json_file:
        with open(args.json_file, "r") as f:
            data = json.load(f)
    else:
        json_path = create_placeholder_json(args.book_id, args.name, args.puzzles)
        print(f"Created placeholder JSON: {json_path}")
        with open(json_path, "r") as f:
            data = json.load(f)

    # Build and write HTML
    book_name = data.get("book_name", args.name)
    puzzles = data.get("puzzles", [])
    html = build_page(book_name, puzzles)

    html_path = os.path.join(book_dir, "index.html")
    with open(html_path, "w") as f:
        f.write(html)
    print(f"Created: {html_path}")

    # Generate QR code
    qr_path = generate_qr(args.book_id)

    # Print next steps
    url = f"https://{GITHUB_USERNAME}.github.io/puzzle-solutions/{args.book_id}/"
    print()
    print("=" * 60)
    print("  NEXT STEPS")
    print("=" * 60)
    if not args.json_file:
        print(f"""
1. Edit the JSON file with your real puzzle data:
   {os.path.join(book_dir, args.book_id + '.json')}

   JSON format:
   {{
     "book_name": "Your Book Title",
     "puzzles": [
       {{
         "title": "Puzzle 1",
         "grid": [["A","B","C"], ["D","E","F"], ["G","H","I"]],
         "highlights": [[0,0], [1,1], [2,2]],
         "words": ["WORD1", "WORD2"]
       }}
     ]
   }}

2. Re-run this script with your completed JSON:
   python3 add_book.py {args.book_id} --name "{args.name}" --json {os.path.join(book_dir, args.book_id + '.json')}
""")
    else:
        print(f"""
1. Review the generated page:
   {html_path}
""")
    print(f"""3. Update index.html to add a link to this book.

4. Commit and push:
   cd {SCRIPT_DIR}
   git add .
   git commit -m "Add {book_name} solutions"
   git push

5. Your solutions will be live at:
   {url}

6. Use this QR code in your KDP book layout:
   {qr_path}
""")


if __name__ == "__main__":
    main()
