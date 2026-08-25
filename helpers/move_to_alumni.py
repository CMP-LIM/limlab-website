#!/usr/bin/env python3
"""
move_to_alumni.py

Moves a person from the "Lab Members" list to the "Lim Lab Alumni" list in
src/people.jade: removes their li.member entry from Lab Members, and adds
a new li.alum entry at the very TOP of the Alumni list (the alumni list is
ordered most-recent-departure-first, so new entries always go at the top).

USAGE
-----
    # interactive (prompts section by section):
    python move_to_alumni.py --slug hernanrubinstein

    # fully non-interactive:
    python move_to_alumni.py --slug hernanrubinstein \\
        --position "Graduate Student" --years "2016-2026" \\
        --credentials PhD \\
        --subsequently "Postdoctoral Fellow, MIT" \\
        --website-url "https://example.com" --website-label "Example Lab Website"

    # also delete their old bio page (src/people/hernanrubinstein.jade),
    # since alumni entries don't link to a page:
    python move_to_alumni.py --slug hernanrubinstein --delete-page

By default this assumes it is being run from the repo root. Use
--repo-root to point at the repo if you're running it from elsewhere.

--slug is the part of their old URL, e.g. for people/hernanrubinstein.html
the slug is "hernanrubinstein". If you don't already have --credentials on
hand, this is also a good moment to add PhD/MD initials, since Lab Members
and Alumni both show them the same way ("Hernan Rubinstein, PhD").
"""

import argparse
import re
import sys
from pathlib import Path


def read_line(label, required=False):
    while True:
        value = input(f"{label}: ").strip()
        if value or not required:
            return value
        print("  (required, please enter a value)")


def find_member_entry(text, slug):
    """
    Find the li.member entry for this slug anywhere in the Lab Members
    section. Returns a dict with start/end offsets and the display name,
    or None if not found.
    """
    marker = "h3.header Lab Members"
    section_start = text.find(marker)
    if section_start == -1:
        raise ValueError(f'Could not find "{marker}" in the file')

    next_header = text.find("h3.header", section_start + len(marker))
    hr_marker = text.find("<hr>", section_start)
    candidates = [x for x in (next_header, hr_marker) if x != -1]
    section_end = min(candidates) if candidates else len(text)

    pattern = re.compile(
        r'(?P<indent>[ \t]*)li\.member[ \t]*\n'
        r'(?P=indent)\t+a\(href="people/' + re.escape(slug) + r'\.html"\)[ \t]*(?P<name>[^\n]*)\n?',
    )
    m = pattern.search(text, section_start, section_end)
    if not m:
        return None
    return {"start": m.start(), "end": m.end(), "name": m.group("name").strip()}


def remove_member_entry(text, entry):
    return text[: entry["start"]] + text[entry["end"] :]


def insert_alumni_entry(text, entry_lines):
    """
    Insert a new li.alum block as the first entry in the Alumni list
    (right after the '.col.s12' line that opens it).
    """
    marker = "h3.header Lim Lab Alumni"
    idx = text.find(marker)
    if idx == -1:
        raise ValueError(f'Could not find "{marker}" in the file')

    anchor = ".col.s12\n\n"
    anchor_idx = text.find(anchor, idx)
    if anchor_idx == -1:
        # fall back: anchor without the trailing blank line
        anchor = ".col.s12\n"
        anchor_idx = text.find(anchor, idx)
        if anchor_idx == -1:
            raise ValueError('Could not find the alumni ".col.s12" list opening')

    insert_at = anchor_idx + len(anchor)
    body = "".join(f"\t\t\t\t\t\t\t\t{line}\n" for line in entry_lines)
    entry_block = f"\t\t\t\t\t\t\tli.alum\n{body}\n"

    return text[:insert_at] + entry_block + text[insert_at:]


def main():
    parser = argparse.ArgumentParser(
        description="Move a person from Lab Members to Lim Lab Alumni in src/people.jade.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--slug",
        required=True,
        help='Their page slug, e.g. "hernanrubinstein" for people/hernanrubinstein.html',
    )
    parser.add_argument("--position", help='e.g. "Graduate Student", "Postdoc"')
    parser.add_argument("--years", help='e.g. "2016-2026" or a single year like "2015"')
    parser.add_argument(
        "--credentials",
        help='Title initials to show, e.g. "PhD" or "MD, PhD" (leave unset to keep whatever was already listed)',
    )
    parser.add_argument("--subsequently", help='What they did next, e.g. "Postdoctoral Fellow, MIT"')
    parser.add_argument("--website-url", help="Optional URL for a personal/lab website link")
    parser.add_argument("--website-label", help='Link text for --website-url, e.g. "Rubinstein Lab Website"')
    parser.add_argument(
        "--delete-page",
        action="store_true",
        help="Also delete their old src/people/<slug>.jade bio page (alumni entries don't link to a page)",
    )
    parser.add_argument("--repo-root", default=".", help="Path to the repo root (default: current directory)")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    people_jade_path = repo_root / "src" / "people.jade"
    if not people_jade_path.exists():
        sys.exit(f"Error: {people_jade_path} not found.")

    text = people_jade_path.read_text()

    entry = find_member_entry(text, args.slug)
    if entry is None:
        sys.exit(
            f'Error: no Lab Members entry found for slug "{args.slug}" '
            f"(looked for people/{args.slug}.html). Check the slug and try again."
        )

    existing_name = entry["name"]  # e.g. "Hernan Rubinstein" or "Hernan Rubinstein, PhD"
    if args.credentials:
        base_name = existing_name.split(",")[0].strip()
        display_name = f"{base_name}, {args.credentials}"
    else:
        display_name = existing_name

    position = args.position
    years = args.years
    subsequently = args.subsequently
    website_url = args.website_url
    website_label = args.website_label

    interactive = not (position and years)
    if interactive:
        print(f"Moving {existing_name} to Alumni. Press Enter to skip any optional field.\n")
        if not position:
            position = read_line("Position/role (e.g. Graduate Student)", required=True)
        if not years:
            years = read_line('Years (e.g. "2016-2026" or "2015")', required=True)
        if subsequently is None:
            subsequently = read_line("Subsequently (what they did next, blank to skip)")
        if website_url is None:
            website_url = read_line("Website URL (blank to skip)")
            if website_url:
                website_label = read_line("Website link text")

    entry_lines = [f"h3.name {display_name}", f"p {position} ({years})"]
    if subsequently:
        entry_lines.append(f"p Subsequently: {subsequently}")
    if website_url:
        label = website_label or website_url
        entry_lines.append("p")
        entry_lines.append(f'\ta(href="{website_url}") {label}')

    text = remove_member_entry(text, entry)
    text = insert_alumni_entry(text, entry_lines)
    people_jade_path.write_text(text)

    print(f"\nMoved {display_name} from Lab Members to Alumni (added at the top of the list).")

    if args.delete_page:
        page_path = repo_root / "src" / "people" / f"{args.slug}.jade"
        if page_path.exists():
            page_path.unlink()
            print(f"Deleted {page_path}")
        else:
            print(f"Note: {page_path} did not exist, nothing to delete.")

    print(
        "\nNext steps:\n"
        "  1. Review the Alumni entry in src/people.jade for formatting.\n"
        "  2. conda activate limlab-website && grunt   # build dest/\n"
        "  3. git add, commit, and open a PR."
    )


if __name__ == "__main__":
    main()