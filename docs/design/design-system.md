# TRACE design system

The rules every TRACE screen follows. Each phase extends this document; it never starts a new look. Terms follow [GLOSSARY.md](../../GLOSSARY.md).

Screens drawn with these rules: [mockups/screens.html](mockups/screens.html). Open it in a browser.

## Principles

1. **One window, everything in a fixed place.** The parts of the window keep their order and position on every screen and in every phase.
2. **The chrome is black and white.** Colour means data or state. It is never decoration, and there is no accent colour.
3. **One system, two themes.** The Timing screen (dark) and the Run sheet (light) share layout, type, spacing and rules. Only the colour tokens differ.
4. **Square and ruled.** No rounded corners, no shadows, no gradients. Structure comes from 1 px rules.
5. **Figures line up.** Tabular figures everywhere. Times read `m:ss.mmm`.
6. **Readable by everyone.** Text meets WCAG 2.2 AA. Channel colours are tested for colour-vision deficiency. A colour is never the only cue: every trace has a named legend row.
7. **Units and signs.** Display units follow the trade (ADR 0002). Signs follow ISO 8855 and are stated in the label (ADR 0003).

## Window

Top to bottom, at the default 1440 × 900. Minimum window 1280 × 720.

| Part | Height | Holds |
|---|---|---|
| Menu bar | 26 px | File, Edit, View, Layout, Add, Data, Component, Tools, Help, in that order |
| Toolbar | 36 px | Labelled buttons, each showing its hot key; a search box for any Channel or command |
| Current lap line | 31 px | A title block: Main, Lap, Time, Outing, Session, Course, Vehicle, Logged; the Overlay lap at the right |
| Lap strip | 17 px | The Outing as a strip of laps, each cell as wide as its lap time, with the time in it |
| Workbook and worksheet tabs | 28 px | Workbook selector; worksheet tabs numbered 1 to 0 |
| Worksheet | rest | Left rail 26 px (Data, Channels, Reports, Layouts); Data and Channels pane 276 px; components; tool rail 28 px |
| Status bar | 24 px | Cursor distance and time, Lap, Sector, zoom, x axis, units, key set, version |

Rules for the window:

- The Data and Channels pane is open and pinned by default.
- Every toolbar button is also a menu command.
- A view that arrives in a later phase is shown greyed in its final place, never hidden, so the layout does not move when it ships.
- On macOS the menus move to the system menu bar and Ctrl becomes Cmd. Nothing else changes between Windows, macOS and Linux.

## Themes

Both themes use the same token names. Dark is the default.

| Token | Timing screen (dark) | Run sheet (light) | Use |
|---|---|---|---|
| `ground` | `#000000` | `#E4E7E9` | Window, menu bar |
| `ground-2` | `#0D0D0D` | `#EDEFF1` | Toolbar, tab row, pane and component headers, status bar |
| `pane` | `#050505` | `#F7F8F9` | Side panes, title block, dialogs |
| `plot` | `#000000` | `#FFFFFF` | Plot and table background |
| `row-main` | `#1B1B1B` | `#E2E6EA` | Row of the Main lap or the selected Log |
| `rule` | `#2B2B2B` | `#B4BAC0` | Hairlines between rows |
| `rule-2` | `#4A4844` | `#7C838A` | Control borders, title-block dividers |
| `frame` | `#77746D` | `#14171A` | Lines that frame a region; button borders |
| `line` | `#F2F0EA` | `#14171A` | The line under the tab row |
| `grid` | `#1E1E1E` | `#E4E8EB` | Plot grid |
| `grid-zero` | `#5A5852` | `#8F969D` | Zero line of a plot |
| `plot-edge` | none | `#B4BAC0` | Outline of each plot |
| `ink` | `#F2F0EA` | `#14171A` | Text; also the cursor |
| `ink-2` | `#C6C3BB` | `#3C4249` | Secondary text |
| `ink-3` | `#928F87` | `#5B6168` | Labels, units, axis figures |
| `ink-4` | `#6A6762` | `#7C838A` | Controls not available yet |
| `inverse` | `#F2F0EA` with `#000000` text | `#14171A` with `#FFFFFF` text | Selection: active tab, Main lap, pressed button, primary button, cursor label |
| `time` | `#FFE600` | `#14171A` | A lap or Sector time with no improvement |
| `improved` | `#39D353` text | `#FFFFFF` on `#16803A` | An improved time |
| `best` | `#FF4DFF` text | `#FFFFFF` on `#8A1FB5` | The best time |
| `overlay` | `#8E8B84` | `#7D848B` | Traces of the Overlay lap |
| `danger` | `#FF6B5E` | `#C62B1A` | Delete |

Selection is always the inverse block. The current row is `row-main` with a 3 px `ink` bar at its left edge.

## Type

**Titillium Web**, weights 400, 600 and 700, bundled with the application so it works offline. It is under the SIL Open Font License 1.1, which is compatible with GPL-3.0-or-later. Its figures are tabular by default.

| Role | Size | Weight | Notes |
|---|---|---|---|
| Body, controls, menus | 12.5 px | 400, menus 600 | |
| Figures in tables and legends | 12 px | 400, cursor values 700 | Tabular |
| Label | 10.5 px | 600 | Capitals, letter-spacing 0.09 em |
| Title-block label | 8.5 px | 600 | Capitals, letter-spacing 0.1 em |
| Worksheet tab | 11.5 px | 600 | Capitals |
| Main lap time | 15 px | 700 | |
| Axis figures, key caps | 9.5 px | 400 | |
| Dialog heading | 15 px | 700 | |

## Shape and space

- Corner radius 0 everywhere.
- Rules are 1 px in three strengths: `rule`, `rule-2`, `frame`.
- Padding steps: 2, 4, 6, 8, 10, 12 px.
- Row heights: lap table 21 px, Sector table 22 px, Channel list 20 px, library 30 px.
- Controls: toolbar button 26 px, field and segmented control 24 px, dialog button 28 px.
- Keyboard focus: a 2 px `ink` outline, 1 px outside the control.

## Timing colours

| Meaning | Rule |
|---|---|
| **Best** | The best lap time, or the best time in a Sector, of the Outing |
| **Improved** | Quicker than every earlier Lap of the Outing when it was set, and later beaten |
| **No improvement** | Any other time |

- On the dark theme the colour is in the figure. On the light theme the cell is filled.
- The Out-lap and the In-lap are not Laps: they are shown in italics, hatched in the lap strip, and never coloured.
- A Deleted lap is struck through and is not eligible for Best or Improved.

## Channel colours

A Channel keeps its colour everywhere in the application.

| Channel | Dark | Light |
|---|---|---|
| Speed | `ink` | `ink` |
| Throttle | `#12A87E` | `#0B8F6C` |
| Brake pressure | `#F0503C` | `#D23B1E` |
| Steering angle | `#3D8DF5` | `#1668C9` |
| Engine speed | `#C08A00` | `#A86F00` |
| Gear, lateral acceleration | `ink-2` | `ink-2` |

- With an Overlay lap, the Main lap keeps the Channel colours and the Overlay lap is drawn thinner in `overlay`.
- A phase that needs more Channel colours adds them here and runs the checks below.

## Components

- **Title block.** Boxed fields, label above value, divided by `rule-2`. The Main tag is an inverse block.
- **Lap strip.** Ruled cells, lap number left, time right. Main lap inverse; best Lap a 3 px bar in `best`; Overlay lap outlined.
- **Tabs.** Capitals, numbered key cap, active tab inverse, `line` beneath the row.
- **Pane.** Header in `ground-2` with a capital label. The Data pane shows Log, Outing, then the lap table: marker, Lap, note, Time, Gap.
- **Time/Distance graph.** Tiled groups. Each group has a 16 px header band (colour swatch, Channel name, unit and position, cursor value, then minimum, maximum and average at the right) so the legend never covers a trace. Sector strip above; distance axis below. Turn numbers join the strip when corner detection arrives in a later phase. Traces 1.6 px. The cursor is a 1 px `ink` line with its distance on the axis.
- **Tables.** Capital column heads in `ink-3`, hairline rows, figures right-aligned.
- **Details list.** Label in `ink-3`, value in `ink`. Shows where the numbers come from: Source, Adapter, name in the file, recorded unit, stored unit, shown unit, sample rate, and what a derived Channel is derived from.
- **Buttons.** Default: `frame` border. Primary: inverse. Delete: `danger`.
- **Dialog.** `frame` border, inverse title bar with a capital label (a `danger` bar for Delete), heading, body, buttons at the bottom right.
- **Message bar.** One line with a 4 px `ink` bar at the left and one action.
- **Key cap.** A 9.5 px outlined label beside a control, showing its hot key.

## Wording

- Use the glossary's terms with its capitals: Log, Outing, Lap, Out-lap, In-lap, Deleted lap, Sector, Channel, Control line, Venue, Course, Vehicle, Session, Source, Adapter.
- Units: km/h, bar, °C, %, g, rpm. Thousands are separated by a thin space: `3 908 m`.
- A Channel's position on the Vehicle is written after its name: "Brake pressure, front", "Wheel speed FL".
- When a file did not supply something, say "Not in the file". Never leave the cell empty.
- A message says what happened, what TRACE did about it, and what the user can do next.

## Hot keys

The keys live in one named key set, shown in the status bar, so another set can be added later.

| Key | Action | Phase |
|---|---|---|
| Ctrl+O | Open Log (the library) | 1 |
| F8 | Data pane | 1 |
| C | Channels pane | 1 |
| N / P | Next or previous Lap | 1 |
| Ctrl+F | Select the fastest Lap | 1 |
| F9 | Time or distance on the x axis | 1 |
| Left / Right | Move the cursor (Ctrl for fast) | 1 |
| Up / Down | Zoom in or out | 1 |
| F2 | Zoom full out | 1 |
| W | Zoom to one Lap | 1 |
| Shift+Left / Right | Pan | 1 |
| F4 | Overlays on or off | later |
| F3 | Variance on or off | later |
| G | Overlapped or tiled groups | later |
| 0 to 9 | Select that worksheet | later |
| F11 / F12 | Previous or next worksheet | later |

## Screens in phase 1

| Screen | Tickets |
|---|---|
| Window, themes and shared parts | #17, #18, #19 |
| Library | #8 |
| Log and Channel plot | #9, #10, #11, #20, #21, #22 |
| Control lines | #12 |
| Dialogs and messages | #8, #9, #12 |
| Hot keys | #23 |

## Checks made

These are the values the automated checks (#24) hold the interface to.

- Text contrast, dark: `ink` 18.4:1, `ink-2` 11.0:1, `ink-3` 6.0:1, `time` 16.6:1, `improved` 10.6:1, `best` 7.8:1, `danger` 7.3:1.
- Text contrast, light: `ink` 14.5:1, `ink-2` 8.2:1, `ink-3` 5.0:1, white on `improved` 5.0:1, white on `best` 7.1:1, `danger` 5.3:1.
- `ink-4` is at least 3:1 in both themes. It marks controls that cannot be used yet, which WCAG exempts from the text minimum.
- Channel colours: worst neighbouring pair under simulated red-green colour-vision deficiency ΔE 9.6 (dark) and 10.2 (light), against a target of 8, and at least 3:1 against the plot.
