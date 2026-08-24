#!/usr/bin/env python3
"""
make_bio_page.py

Generates a new Lim Lab website person page (src/people/<slug>.jade) from
an existing portrait image and a plain-text bio file, following the same
structure as src/people/membertemplate.jade.

USAGE
-----
    python make_bio_page.py --image src/people/portraits/jane_doe.jpg --bio jane_bio.txt

    # or, with no --bio file, you'll be walked through the bio section by
    # section (First/Last/Email/Position, then Research, Education, Awards,
    # and Publications). Each section just takes whatever text you paste or
    # type -- press Enter on a blank line to move to the next section, or
    # to skip it. This is the easiest option when people's bios don't all
    # follow the same format.
    python make_bio_page.py --image src/people/portraits/jane_doe.jpg

    # also add the person to the "Lab Members" list on src/people.jade:
    python make_bio_page.py --image src/people/portraits/jane_doe.jpg --bio jane_bio.txt --add-to-listing

By default this assumes it is being run from the repo root (so
src/people/ and src/people.jade resolve correctly). Use --repo-root to
point at the repo if you're running it from elsewhere.

BIO FILE FORMAT
----------------
A simple "Label: value" text file. Multi-entry fields (Education, Awards,
Publications) take one entry per line, indented with at least one space
or a leading "-". Example:

    First: Jane
    Last: Doe
    Email: jane.doe
    Position: Graduate Student
    Research: Engineering synthetic signaling circuits in mammalian cells.
    Education:
      - 2022-Present | Ph.D., Biophysics | University of California, San Francisco
      - 2018-2022 | B.A., Molecular and Cell Biology | University of California, Berkeley
    Awards:
      - 2023 NSF Graduate Research Fellowship
    Publications:
      - Doe, J., et al. "A great paper." Nature. (2024).

All fields are optional except First and Last. Missing sections are left
blank in the generated page (matching the empty placeholders already used
by pages like alessandromigliara.jade).
"""

import argparse
import re
import sys
from pathlib import Path


MULTI_FIELDS = {"education", "awards", "publications"}
SINGLE_FIELDS = {"first", "last", "email", "position", "research"}
ALL_FIELDS = MULTI_FIELDS | SINGLE_FIELDS


def parse_bio_file(text):
    """Parse the simple 'Label: value' / indented-list bio format."""
    data = {k: [] for k in MULTI_FIELDS}
    data.update({k: "" for k in SINGLE_FIELDS})

    current_multi = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue

        # Indented / bulleted line -> belongs to the current multi-field
        if raw_line[:1] in (" ", "\t") or line.strip().startswith("-"):
            if current_multi:
                item = line.strip().lstrip("-").strip()
                if item:
                    data[current_multi].append(item)
            continue

        # "Label: value" or "Label:" (start of a multi-entry section)
        match = re.match(r"^([A-Za-z ]+):\s*(.*)$", line)
        if not match:
            continue
        label = match.group(1).strip().lower()
        value = match.group(2).strip()

        if label not in ALL_FIELDS:
            continue

        if label in MULTI_FIELDS:
            current_multi = label
            if value:
                data[label].append(value)
        else:
            current_multi = None
            data[label] = value

    return data


def read_line(label, required=False):
    """Read a single short line (name, email, position, etc.)."""
    while True:
        value = input(f"{label}: ").strip()
        if value or not required:
            return value
        print("  (required, please enter a value)")


def read_paragraph(label, hint="paste as many lines as you like, then leave a blank line to finish"):
    """Read free-form multi-line text (e.g. a pasted research blurb) until a blank line."""
    print(f"\n{label} ({hint}):")
    lines = []
    while True:
        line = input("  ")
        if line.strip() == "" and lines:
            break
        if line.strip() == "" and not lines:
            # allow skipping the whole section by hitting Enter immediately
            break
        lines.append(line.rstrip())
    return " ".join(lines).strip()


def read_list(label, hint="one entry per line, blank line to finish"):
    """Read a list of freeform entries (education lines, awards, publications)."""
    print(f"\n{label} ({hint}):")
    items = []
    while True:
        line = input("  - ").strip()
        if not line:
            break
        items.append(line)
    return items


def prompt_for_bio():
    """
    Interactive, section-by-section bio entry.

    People's bios rarely arrive in the same format, so every section here
    just takes whatever text you paste or type in and stops on a blank
    line -- no required delimiters or structure beyond that. Skip any
    section by hitting Enter immediately.
    """
    print("Enter this person's bio section by section. Press Enter on an")
    print("empty line to move to the next section (or to skip a section).\n")

    data = {}
    data["first"] = read_line("First name", required=True)
    data["last"] = read_line("Last name", required=True)
    data["email"] = read_line("Email handle (before @ucsf.edu, blank to skip)")
    data["position"] = read_line("Position (e.g. Graduate Student, blank to skip)")

    data["research"] = read_paragraph(
        "Research interests",
        hint="paste the bio text as given, in whatever format -- blank line to finish",
    )

    data["education"] = read_list(
        "Education",
        hint='one entry per line, e.g. "2022-Present | Ph.D., Biophysics | UCSF" '
        "-- but plain lines work too, blank line to finish",
    )

    data["awards"] = read_list("Awards", hint="one per line, blank line to finish")

    data["publications"] = read_list(
        "Publications", hint="one citation per line, blank line to finish"
    )

    return data


def slugify(first, last):
    slug = re.sub(r"[^a-z0-9]", "", f"{first}{last}".lower())
    if not slug:
        raise ValueError("Could not build a page slug from the first/last name.")
    return slug


def parse_education_entry(entry):
    """Split a 'years | degree | institution' entry into its parts."""
    parts = [p.strip() for p in entry.split("|")]
    while len(parts) < 3:
        parts.append("")
    return parts[0], parts[1], parts[2]


def render_jade(data, portrait_rel_path):
    first = data.get("first", "").strip()
    last = data.get("last", "").strip()
    email = data.get("email", "").strip()
    position = data.get("position", "").strip()
    research = data.get("research", "").strip()
    education = data.get("education", [])
    awards = data.get("awards", [])
    publications = data.get("publications", [])

    lines = []
    lines.append("html")
    lines.append("\thead")
    lines.append("\t\ttitle")
    lines.append("\t\tinclude ../components/people_head.jade")
    lines.append("\tbody")
    lines.append("\t\tinclude ../components/header.jade")
    lines.append("\t\t#title.container")
    lines.append("\t\t\th1.row.s12")
    lines.append(f"\t\t\t\tspan.part2 {first} | ")
    lines.append(f"\t\t\t\tspan.part1 {last}")
    lines.append("\t\t#basics.container")
    lines.append("\t\t\t.row")
    lines.append("\t\t\t\t.col.s8")
    if email:
        lines.append(
            f'\t\t\t\t\t|   <p>{email} <img src="images/at.gif" class="at"> ucsf.edu</p>'
        )
    else:
        lines.append('\t\t\t\t\t|   <p></p>')
    lines.append(f"\t\t\t\t\t|   <p><em>{position}</em></p>")
    lines.append("\t\t\t\t.col.s4")
    lines.append(f'\t\t\t\t\timg.responsive-img.z-depth-1(src="{portrait_rel_path}")')
    lines.append("")
    lines.append("\t\t\t#education")
    lines.append("\t\t\t\th3 Education")
    lines.append("")
    for entry in education:
        years, degree, institution = parse_education_entry(entry)
        lines.append(f"\t\t\t\tp {years}")
        lines.append(f"\t\t\t\t.degrees {degree}")
        lines.append(f"\t\t\t\t.degrees {institution}")
        lines.append("")

    lines.append("\t\t\t\th3 Research Interests")
    lines.append(f"\t\t\t\tp {research}")
    lines.append("")
    lines.append("\t\t\t\th3 Awards")
    if awards:
        for award in awards:
            lines.append(f"\t\t\t\tp {award}")
    else:
        lines.append("\t\t\t\tp ")
    lines.append("")
    lines.append("\t\t\t\th3 Publications")
    if publications:
        for pub in publications:
            lines.append(f"\t\t\t\tp {pub}")
    else:
        lines.append("\t\t\t\tp ")
    lines.append("\t\t\t\t ")
    lines.append("\t\tinclude ../components/footer.jade")

    return "\n".join(lines) + "\n"


def insert_into_listing(people_jade_path, first, last, slug):
    """Insert a new <li> entry as the first item in the Lab Members list."""
    text = people_jade_path.read_text()
    marker = "h3.header Lab Members"
    idx = text.find(marker)
    if idx == -1:
        raise ValueError(f'Could not find "{marker}" in {people_jade_path}')

    ul_idx = text.find("ul", idx)
    if ul_idx == -1:
        raise ValueError(f'Could not find the member "ul" list after "{marker}"')

    line_end = text.find("\n", ul_idx)
    if line_end == -1:
        raise ValueError("Unexpected end of file while inserting listing entry")

    entry = (
        f'\n\t\t\t\t\t\t.col.s12.m4\n'
        f'\t\t\t\t\t\t\tli.member\n'
        f'\t\t\t\t\t\t\t\ta(href="people/{slug}.html") {first} {last}'
    )

    new_text = text[: line_end + 1] + entry + "\n" + text[line_end + 1 :]
    people_jade_path.write_text(new_text)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a new Lim Lab website person page from a portrait image and a bio.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--image",
        required=True,
        help="Path to the portrait image, already placed somewhere inside src/people/ (e.g. src/people/images/ or src/people/portraits/)",
    )
    parser.add_argument(
        "--bio",
        help="Path to a bio text file (see format in --help). If omitted, prompts interactively.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Path to the repo root (default: current directory)",
    )
    parser.add_argument(
        "--add-to-listing",
        action="store_true",
        help="Also insert a <li> entry for this person into src/people.jade's Lab Members list",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the output .jade file if it already exists",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    people_dir = repo_root / "src" / "people"

    image_path = Path(args.image).resolve()
    if not image_path.exists():
        sys.exit(f"Error: image not found at {image_path}")
    try:
        portrait_rel = image_path.relative_to(people_dir)
    except ValueError:
        sys.exit(
            f"Error: --image must live inside {people_dir}\n"
            f"(got {image_path}). Move/copy the portrait there first "
            f"(e.g. into src/people/images/ or src/people/portraits/)."
        )

    if args.bio:
        bio_path = Path(args.bio)
        if not bio_path.exists():
            sys.exit(f"Error: bio file not found at {bio_path}")
        data = parse_bio_file(bio_path.read_text())
    else:
        data = prompt_for_bio()

    first, last = data.get("first", "").strip(), data.get("last", "").strip()
    if not first or not last:
        sys.exit("Error: First and Last name are required.")

    slug = slugify(first, last)
    output_path = people_dir / f"{slug}.jade"
    if output_path.exists() and not args.force:
        sys.exit(f"Error: {output_path} already exists. Use --force to overwrite.")

    portrait_rel_path = portrait_rel.as_posix()
    jade_content = render_jade(data, portrait_rel_path)

    people_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(jade_content)
    print(f"Wrote {output_path}")

    if args.add_to_listing:
        people_jade_path = repo_root / "src" / "people.jade"
        if not people_jade_path.exists():
            print(f"Warning: {people_jade_path} not found, skipping listing update.")
        else:
            insert_into_listing(people_jade_path, first, last, slug)
            print(f"Added {first} {last} to the Lab Members list in {people_jade_path}")
    else:
        print(
            f'\nTo list this page, add the following inside src/people.jade '
            f'(under "Lab Members"):\n'
            f'\t\t\t\t\t.col.s12.m4\n'
            f'\t\t\t\t\t\tli.member\n'
            f'\t\t\t\t\t\t\ta(href="people/{slug}.html") {first} {last}'
        )

    print(
        "\nNext steps:\n"
        "  1. Review the generated .jade file for anything that needs manual tweaking.\n"
        "  2. conda activate limlab-website && grunt   # build dest/\n"
        "  3. git add, commit, and open a PR."
    )


if __name__ == "__main__":
    main()