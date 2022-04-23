from musthe import *
import piano_fingering
import svgwrite

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

ROOTS=[
    "C4",
    "C#4",
    "D4",
    "Eb4",
    "E4",
    "F4",
    "F#4",
    "G4",
    "Ab4",
    "A4",
    "Bb4",
    "B4",
]

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

    text_x = x_offset + (7 * octaves * WHITE_KEY_WIDTH) / 2.0
    text_y = y_offset + WHITE_KEY_HEIGHT
    scale_notes = list(map(lambda t: t[0], label_notes))
    text = draw_scale_notes(drawing, scale_notes, (text_x, text_y))
    group.add(text)
    return group

def main(path):
    scale_width = 14 * WHITE_KEY_WIDTH + 30
    scale_height = WHITE_KEY_HEIGHT + 30
    width=len(MODES) * scale_width
    height=len(ROOTS) * scale_height
    drawing = svgwrite.Drawing(path, profile="full", size=(width, height))
    drawing.embed_stylesheet(STYLE)
    for i, mode in enumerate(MODES):
        for j, root in enumerate(ROOTS):
            scale = Scale(root, mode)
            if root in SCALES and mode in SCALES[root]:
                right_fingers, left_fingers = SCALES[root][mode]
                labeled_notes=list(zip(scale, right_fingers, left_fingers))
                group = draw_keyboard(
                    drawing,
                    octaves=2,
                    label_notes=labeled_notes,
                    x_offset=i * scale_width,
                    y_offset=j * scale_height,
                )
                drawing.add(group)
    drawing.save()

if __name__ == "__main__":
    main("output.svg")
