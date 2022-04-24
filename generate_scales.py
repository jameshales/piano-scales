from musthe import *
from yattag import Doc, indent
import piano_fingering
import svgwrite
import os
import urllib.parse

# Piano key dimensions taken from: <https://upload.wikimedia.org/wikipedia/commons/1/15/PianoKeyboard.svg>
# See also: <http://www.mathpages.com/home/kmath043.htm>
WHITE_KEY_WIDTH=23
WHITE_KEY_HEIGHT=120
WHITE_KEY_INDICES={number: Letter.letters_idx[letter] for letter, number in Letter.letters_number.items()}

BLACK_KEY_WIDTH=13
BLACK_KEY_HEIGHT=80
BLACK_KEY_NUMBER_OFFSETS={1: 43.0 / 3.0, 3: 125 / 3.0, 6: 82.25, 8: 108.25, 10: 134.75}

STYLE="""
.key {
    stroke-width: 1.5px;
}

.white.key .box {
    fill: white;
    stroke: black;
}

.white.key .label {
    fill: black;
    font-size: 15px;
}

.black.key .box {
    fill: black;
    stroke: black;
}

.black.key .label {
    fill: white;
    font-size: 15px;
}

.key.selected .box {
    fill: #FEC47F;
}

.label {
    font-family: "Helvetica", "Nimbus Sans", sans-serif;
    font-weight: bold;
    text-anchor: middle;
}

.key .label.lower {
    fill: black;
    dominant-baseline: text-before-edge;
}

.key .label.upper {
    fill: white;
    dominant-baseline: text-after-edge;
}

text.notes {
    font-family: "Helvetica", "Nimbus Sans", sans-serif;
    font-size: 15px;
    font-weight: bold;
    text-anchor: middle;
    dominant-baseline: text-before-edge;
    transform: translate(0, 5px);
}
"""

MODES=[
    "major",
    "natural_minor",
    "harmonic_minor",
    "melodic_minor",
]

ROOTS=list(map(lambda n: n.scientific_notation(), Note.all()))

ROOT_ENHARMONIC_EQUIVALENTS={
    "A#4": "Bb4",
    "B#4": "C4",
    "Cb4": "B4",
    "D#4": "Eb4",
    "Db4": "C#4",
    "G#4": "Ab4",
    "Gb4": "F#4",
}

# Piano fingering taken from chart at: <http://robertkelleyphd.com/home/teaching/keyboard/keyboard-scale-fingering-chart/>
SCALES={
    "C4": {
        "major": (
            [1,2,3,1,2,3,4,1],
            [1,4,3,2,1,3,2,1]
        ),
        "natural_minor": (
            [1,2,3,1,2,3,4,1],
            [2,1,3,2,1,4,3,2]
        ),
        "harmonic_minor": (
            [1,2,3,1,2,3,4,1],
            [2,1,3,2,1,4,3,2]
        ),
        "melodic_minor": (
            [1,2,3,1,2,3,4,1],
            [2,1,4,3,2,1,3,2]
        )
    },
    "A4": {
        "major": (
            [1,2,3,1,2,3,4,1],
            [2,1,3,2,1,4,3,2]
        ),
        "natural_minor": (
            [1,2,3,1,2,3,4,1],
            [1,4,3,2,1,3,2,1]
        ),
        "harmonic_minor": (
            [1,2,3,1,2,3,4,1],
            [3,2,1,3,2,1,4,3]
        ),
        "melodic_minor": (
            [1,2,3,1,2,3,4,1],
            [2,1,3,2,1,4,3,2]
        )
    },
    "G4": {
        "major": (
            [1,2,3,1,2,3,4,1],
            [3,2,1,3,2,1,4,3]
        ),
        "natural_minor": (
            [2,3,4,1,2,3,1,2],
            [2,1,3,2,1,4,3,2]
        ),
        "harmonic_minor": (
            [1,2,3,1,2,3,4,1],
            [2,1,3,2,1,4,3,2]
        ),
        "melodic_minor": (
            [1,2,3,1,2,3,4,1],
            [2,1,4,3,2,1,3,2]
        )
    },
    "D4": {
        "major": (
            [1,2,3,1,2,3,4,1],
            [2,1,4,3,2,1,3,2]
        ),
        "natural_minor": (
            [2,3,1,2,3,4,1,2],
            [2,1,3,2,1,4,3,2]
        ),
        "harmonic_minor": (
            [1,2,3,1,2,3,4,1],
            [2,1,3,2,1,4,3,2]
        ),
        "melodic_minor": (
            [1,2,3,1,2,3,4,1],
            [3,2,1,3,2,1,4,3]
        )
    },
    "E4": {
        "major": (
            [1,2,3,1,2,3,4,1],
            [1,4,3,2,1,3,2,1]
        ),
        "natural_minor": (
            [3,4,1,2,3,1,2,3],
            [1,4,3,2,1,3,2,1]
        ),
        "harmonic_minor": (
            [1,2,3,1,2,3,4,1],
            [1,4,3,2,1,3,2,1]
        ),
        "melodic_minor": (
            [1,2,3,1,2,3,4,1],
            [1,4,3,2,1,3,2,1]
        )
    },
    "B4": {
        "major": (
            [1,2,3,1,2,3,4,1],
            [1,3,2,1,4,3,2,1]
        ),
        "natural_minor": (
            [3,4,1,2,3,1,2,3],
            [1,3,2,1,4,3,2,1]
        ),
        "harmonic_minor": (
            [1,2,3,1,2,3,4,1],
            [1,3,2,1,4,3,2,1]
        ),
        "melodic_minor": (
            [1,2,3,1,2,3,4,1],
            [1,3,2,1,4,3,2,1]
        )
    },
    "F#4": {
        "major": (
            [2,3,4,1,2,3,1,2],
            [4,3,2,1,3,2,1,4]
        ),
        "natural_minor": (
            [3,4,1,2,3,1,2,3],
            [4,3,2,1,3,2,1,4]
        ),
        "harmonic_minor": (
            [3,4,1,2,3,1,2,3],
            [4,3,2,1,3,2,1,4]
        ),
        "melodic_minor": (
            [2,3,1,2,3,4,1,2],
            [4,3,2,1,3,2,1,4]
        )
    },
    "C#4": {
        "major": (
            [2,3,1,2,3,4,1,2],
            [3,2,1,4,3,2,1,3]
        ),
        "natural_minor": (
            [3,4,1,2,3,1,2,3],
            [3,2,1,4,3,2,1,3]
        ),
        "harmonic_minor": (
            [3,4,1,2,3,1,2,3],
            [3,2,1,4,3,2,1,3]
        ),
        "melodic_minor": (
            [2,3,1,2,3,4,1,2],
            [3,2,1,4,3,2,1,3]
        )
    },
    "Ab4": {
        "major": (
            [3,4,1,2,3,1,2,3],
            [3,2,1,4,3,2,1,3]
        ),
        "natural_minor": (
            [3,4,1,2,3,1,2,3],
            [3,2,1,3,2,1,4,3]
        ),
        "harmonic_minor": (
            [3,4,1,2,3,1,2,3],
            [3,2,1,4,3,2,1,3]
        ),
        "melodic_minor": (
            [3,4,1,2,3,1,2,3],
            [3,2,1,4,3,2,1,3]
        )
    },
    "Eb4": {
        "major": (
            [3,1,2,3,4,1,2,3],
            [3,2,1,4,3,2,1,3]
        ),
        "natural_minor": (
            [3,1,2,3,4,1,2,3],
            [2,1,4,3,2,1,3,2]
        ),
        "harmonic_minor": (
            [3,1,2,3,4,1,2,3],
            [2,1,4,3,2,1,3,2]
        ),
        "melodic_minor": (
            [3,1,2,3,4,1,2,3],
            [2,1,4,3,2,1,3,2]
        )
    },
    "Bb4": {
        "major": (
            [4,1,2,3,1,2,3,4],
            [3,2,1,4,3,2,1,3]
        ),
        "natural_minor": (
            [4,1,2,3,1,2,3,4],
            [2,1,3,2,1,4,3,2]
        ),
        "harmonic_minor": (
            [4,1,2,3,1,2,3,4],
            [2,1,3,2,1,4,3,2]
        ),
        "melodic_minor": (
            [4,1,2,3,1,2,3,4],
            [2,1,4,3,2,1,3,2]
        )
    },
    "F4": {
        "major": (
            [1,2,3,4,1,2,3,1],
            [3,2,1,4,3,2,1,3]
        ),
        "natural_minor": (
            [1,2,3,4,1,2,3,1],
            [2,1,3,2,1,4,3,2]
        ),
        "harmonic_minor": (
            [1,2,3,4,1,2,3,1],
            [2,1,3,2,1,4,3,2]
        ),
        "melodic_minor": (
            [1,2,3,4,1,2,3,1],
            [2,1,4,3,2,1,3,2]
        )
    }
}

def scale_fingering(scale):
    notes = list(map(lambda n: n.midi_note(), scale[:8]))
    right = piano_fingering.computeFingering(notes, "right")
    right = list(map(lambda n: n["fingers"][0], piano_fingering.computeFingering(notes, "right")))
    left = list(map(lambda n: n["fingers"][0], piano_fingering.computeFingering(notes, "left")))
    return (scale, right, left)

# Is a note on a white key or a black key?
def is_white_key(note):
    return (note.number % 12) in Letter.letters_number.values()

# Print the note with Unicode flat and sharp symbols
def pretty_print_note(note):
    return str(note).replace("b", "♭").replace("#", "♯")

def pretty_print_mode(mode):
    modes = {
        "major": "Major",
        "natural_minor": "Minor",
        "harmonic_minor": "Harmonic Minor",
        "melodic_minor": "Melodic Minor"
    }
    return modes[mode]

def pretty_print_scale(scale):
    return f"{pretty_print_note(scale.root)} {pretty_print_mode(scale.name)}"

def slug_accidental(accidental):
    if len(accidental) == 0:
        return "natural"
    elif accidental[0] == "b":
        return "-".join(len(accidental) * ["flat"])
    elif accidental[0] == "#":
        return "-".join(len(accidental) * ["sharp"])

def slug_note(note):
    return f"{note.letter.name.lower()}-{slug_accidental(note.accidental)}-{note.octave}"

def slug_mode(mode):
    modes = {
        "major": "major",
        "natural_minor": "minor",
        "harmonic_minor": "harmonic-minor",
        "melodic_minor": "melodic-minor"
    }
    return modes[mode]

def slug_scale(scale):
    return f"{slug_note(scale.root)}-{slug_mode(scale.name)}"

# Draw the key corresponding to a note
def draw_key(
    drawing,
    note,
    label_upper=None,
    label_lower=None,
    selected=False,
    x_offset=0,
    y_offset=0,
):
    selected_class = " selected" if selected else ""
    if is_white_key(note):
        # Draw a white key
        x = (7 * (note.number // 12) + WHITE_KEY_INDICES[note.number % 12]) * WHITE_KEY_WIDTH + x_offset
        y = y_offset
        group = drawing.g(class_="white key" + selected_class)
        group.add(
            drawing.rect(
                insert=(x, y),
                size=(WHITE_KEY_WIDTH, WHITE_KEY_HEIGHT),
                class_="box"
            )
        )
        if label_lower is not None:
            group.add(
                drawing.text(
                    str(label_lower),
                    insert=(
                        x + WHITE_KEY_WIDTH / 2.0,
                        y + BLACK_KEY_HEIGHT + (WHITE_KEY_HEIGHT - BLACK_KEY_HEIGHT) / 2.0
                    ),
                    class_="label lower",
                )
            )
        if label_upper is not None:
            group.add(
                drawing.text(
                    str(label_upper),
                    insert=(
                        x + WHITE_KEY_WIDTH / 2.0,
                        y + BLACK_KEY_HEIGHT + (WHITE_KEY_HEIGHT - BLACK_KEY_HEIGHT) / 2.0
                    ),
                    class_="label upper",
                )
            )
        return group
    else:
        # Draw a black key
        x = 7 * (note.number // 12) * WHITE_KEY_WIDTH + BLACK_KEY_NUMBER_OFFSETS[note.number % 12] + x_offset
        y = y_offset
        group = drawing.g(class_="black key" + selected_class)
        group.add(
            drawing.rect(
                insert=(x, y),
                size=(BLACK_KEY_WIDTH, BLACK_KEY_HEIGHT),
                class_="box"
            )
        )
        if label_lower is not None:
            group.add(
                drawing.text(
                    str(label_lower),
                    insert=(
                        x + BLACK_KEY_WIDTH / 2.0,
                        y + BLACK_KEY_HEIGHT / 2.0
                    ),
                    class_="label lower"
                )
            )
        if label_upper is not None:
            group.add(
                drawing.text(
                    str(label_upper),
                    insert=(
                        x + BLACK_KEY_WIDTH / 2.0,
                        y + BLACK_KEY_HEIGHT / 2.0
                    ),
                    class_="label upper"
                )
            )
        return group

def draw_scale_notes(drawing, notes, insert):
    text = drawing.text(
        "",
        insert=insert,
        class_="notes"
    )
    if len(notes) > 0:
        text.add(drawing.tspan(pretty_print_note(notes[0]), class_="note"))
    for note in notes[1:]:
        text.add(drawing.tspan(" • ", class_="separator"))
        text.add(drawing.tspan(pretty_print_note(note), class_="note"))
    return text

def draw_keyboard(
    drawing,
    octaves,
    label_notes=list(),
    x_offset=0,
    y_offset=0,
):
    group = drawing.g(class_="scale")

    # Create a canonical list of notes corresponding to keys
    notes = list(
        reversed(
            {
                note.number: note
                for note in reversed(list(Note.all(min_octave=4, max_octave=octaves+4-1)))
            }.values()
        )
    )
    min_note = min(notes, key=lambda n: n.number)
    min_key = (min_note.number // 12) * 7

    # Map of note number to label notes
    label_notes_numbers = {
        note.number: (note, label_upper, label_lower)
        for (note, label_upper, label_lower) in label_notes
    }

    # Group white and black keys separately so black keys are on top
    white_key_group = group.add(drawing.g())
    black_key_group = group.add(drawing.g())

    for note in notes:
        # Is this note one of the labeled notes?
        (labeled_note, label_upper, label_lower) = label_notes_numbers.get(note.number, (note, None, None))

        selected = note.number in label_notes_numbers

        key = draw_key(
            drawing,
            note=labeled_note,
            label_lower=label_lower,
            label_upper=label_upper,
            selected=selected,
            x_offset=x_offset - min_key * WHITE_KEY_WIDTH,
            y_offset=y_offset,
        )

        # Add to the correct group
        key_group = white_key_group if is_white_key(note) else black_key_group
        key_group.add(key)

    # text_x = x_offset + (7 * octaves * WHITE_KEY_WIDTH) / 2.0
    # text_y = y_offset + WHITE_KEY_HEIGHT
    # scale_notes = list(map(lambda t: t[0], label_notes))
    # text = draw_scale_notes(drawing, scale_notes, (text_x, text_y))
    # group.add(text)
    return group

def main(base_path):
    doc, tag, text, line = Doc().ttl()
    doc.asis("<!DOCTYPE html>")
    width = 14 * WHITE_KEY_WIDTH
    height = WHITE_KEY_HEIGHT
    with tag("html"):
        with tag("head"):
            with tag("title"):
                text("Piano Scales")
            doc.stag(
                "link", 
                rel="stylesheet",
                href="style.css"
            )
            doc.stag(
                "link", 
                rel="stylesheet",
                href="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/css/bootstrap.min.css",
                integrity="sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu",
                crossorigin="anonymous"
            )
            doc.stag(
                "meta",
                name="viewport",
                content="width=device-width, initial-scale=1"
            )
            with tag(
                "script",
                src="https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js",
                integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=",
                crossorigin="anonymous"
            ):
                pass
            with tag(
                "script",
                src="https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/dist/js/bootstrap.min.js",
                integrity="sha384-aJ21OjlMXNL5UyIl/XNwTMqvzeRMZH2w8c5cRVpzpU8Y5bApTppSuUkhZXN0VxHd",
                crossorigin="anonymous"
            ):
                pass
        with tag("body"):
            with tag("div", klass="container"):
                with tag("header"):
                    with tag("h1"):
                        text("Piano Scales")
                with tag("nav"):
                    with tag("ul", klass="nav nav-pills"):
                        for mode in MODES:
                            with tag("li", klass="dropdown", role="presentation"):
                                with tag(
                                    "a",
                                    ("data-target", "#"),
                                    ("data-toggle", "dropdown"),
                                    ("aria-haspopup", "true"),
                                    ("aria-expanded", "false"),
                                    klass="dropdown-toggle",
                                    role="button",
                                ):
                                    text(pretty_print_mode(mode))
                                    text(" ")
                                    with tag("span", klass="caret"):
                                        pass
                                with tag("ul", klass="dropdown-menu"):
                                    for root in ROOTS:
                                        scale = Scale(root, mode)
                                        with tag("li"):
                                            with tag("a", href=f"#{slug_scale(scale)}"):
                                                text(pretty_print_scale(scale))
                for i, mode in enumerate(MODES):
                    with tag("section", id=slug_mode(mode)):
                        with tag("h2"):
                            text(pretty_print_mode(mode))
                        mode_path = os.path.join(base_path, mode)
                        os.makedirs(mode_path, exist_ok=True)
                        for j, root in enumerate(ROOTS):
                            path = os.path.join(mode_path, f"{root}.svg")
                            drawing = svgwrite.Drawing(path, profile="full", size=(width, height))
                            drawing.embed_stylesheet(STYLE)
                            if root in SCALES and mode in SCALES[root]:
                                scale = Scale(root, mode)
                                notes = scale[:8]
                                with tag("section", klass="scale", id=slug_scale(scale)):
                                    with tag("h3"):
                                        text(pretty_print_scale(scale))
                                    with tag("div", klass="contents"):
                                        doc.stag("img", klass="keyboard", src=urllib.parse.quote(path))
                                        with tag("div", klass="notes"):
                                            with tag("div"):
                                                if len(notes) > 0:
                                                    with tag("span", klass="note"):
                                                        text(pretty_print_note(notes[0]))
                                                for note in notes[1:]:
                                                    with tag("span", klass="separator"):
                                                        text(" • ")
                                                    with tag("span", klass="note"):
                                                        text(pretty_print_note(note))
                                equivalent = ROOT_ENHARMONIC_EQUIVALENTS.get(root, root)
                                right_fingers, left_fingers = SCALES[equivalent][mode]
                                labeled_notes=list(zip(notes, right_fingers, left_fingers))
                                group = draw_keyboard(
                                    drawing,
                                    octaves=2,
                                    label_notes=labeled_notes,
                                )
                                drawing.add(group)
                            drawing.save()
    with open("output.html", "w") as f:
        f.write(indent(doc.getvalue()))

if __name__ == "__main__":
    main("output")
