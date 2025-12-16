# Pysion - Python API for DaVinci Resolve Fusion

## Overview

**Pysion** is a Python framework for programmatically creating Blackmagic DaVinci Resolve Fusion compositions using Python code. Instead of manually creating node trees in Fusion's GUI, you write Python code to define compositions, tools, inputs, animations, and connections. The framework outputs Lua-like `.setting` files that can be pasted directly into Fusion's node-based compositor.

### Key Information

| Property | Value |
|----------|-------|
| **Author** | Bruno Reis |
| **Version** | 0.1.2 |
| **License** | MIT |
| **Python** | >= 3.10 |
| **Repository** | https://github.com/brunocbreis/pysion |

---

## Installation

```bash
# Basic installation
pip install git+https://github.com/brunocbreis/pysion

# With clipboard support (for comp.copy())
pip install "pysion[copy] @ git+https://github.com/brunocbreis/pysion"
```

---

## Quick Start

```python
from pysion import Composition, Tool, RGBA
from pysion.animation import Curve

# 1. Create a composition
comp = Composition()

# 2. Add tools
bg = Tool.background("BG1", RGBA(1, 0.4, 0.1), resolution="auto")
comp.add_tools(bg)
text = comp.add_text("Title", "Hello World", color=RGBA(1, 1, 1))

# 3. Connect tools with a merge
merge = comp.add_merge("Merge1", bg, text)

# 4. Animate the title position
title_pos = comp.animate_position(text, default_curve_x=Curve.ease_in())
title_pos[0] = (-0.5, 0.5)    # Start position at frame 0
title_pos[24] = (0.5, 0.5)    # End position at frame 24

# 5. Output
print(comp)                    # Print Lua code to console
comp.copy()                    # Copy to clipboard (requires pyperclip)
```

---

## Directory Structure

```
pysion/
├── pysion/                    # Main package
│   ├── __init__.py           # Package exports
│   ├── composition.py        # Composition class (main container)
│   ├── tool.py               # Tool class (Fusion nodes)
│   ├── input.py              # Input and Polyline classes
│   ├── macro.py              # Macro and InstanceInput/Output classes
│   ├── flow.py               # Flow positioning utilities
│   ├── color.py              # RGBA and TileColor classes
│   ├── user_control.py       # UserControl class
│   ├── modifiers.py          # Modifier and XYPathModifier classes
│   ├── named_table.py        # Lua table generation
│   ├── animation/            # Animation subpackage
│   │   ├── spline.py         # BezierSpline class
│   │   ├── curve.py          # Curve class (animation curves)
│   │   └── keyframe.py       # Keyframe class
│   └── values/               # Value types and converters
│       ├── converters.py     # String/tuple/list converters
│       ├── fu_id.py          # FuID class (Fusion IDs)
│       ├── tool_id.py        # ToolID namespace (tool identifiers)
│       └── user_controls.py  # DType and InputControl namespaces
├── tests/                     # Test suite
│   ├── test_composition.py
│   ├── test_tool.py
│   ├── test_input.py
│   ├── test_macro.py
│   ├── test_curve.py
│   └── expected_results/     # Expected test outputs
├── examples/                  # Example scripts
│   └── simple_title/
│       ├── simple_title.py
│       └── simple_title_media_out.py
├── setup.py                   # Setup configuration
├── setup.cfg                  # Package metadata
├── pyproject.toml            # Build system config
└── README.md                 # Official documentation
```

---

## Core Concepts

### Composition

The `Composition` class is the main container that holds all tools, modifiers, and generates the final output.

```python
from pysion import Composition

comp = Composition()

# Add tools
comp.add_tool(id="Background", name="BG1", position=(0, 0))
text = comp.add_text("MyTitle", "Hello", font="Arial", color=RGBA(1,1,1))
merge = comp.add_merge("Merge1", background=bg, foreground=text)

# Connect tools
comp.connect(tool_out=text, tool_in=merge)

# Output methods
print(comp)              # Print to console
comp.copy()              # Copy to clipboard
comp.save("name", "./")  # Save to .setting file
```

**Key Methods:**
| Method | Description |
|--------|-------------|
| `add_tool(id, name, position)` | Add a generic Fusion tool |
| `add_tools(*tools)` | Add multiple tools at once |
| `add_text(name, text, font, color, ...)` | Create a Text+ node |
| `add_merge(name, bg, fg, position)` | Create a Merge node |
| `connect(tool_out, tool_in)` | Connect two tools |
| `animate(tool, input, ...)` | Animate a numeric input |
| `animate_position(tool, input, ...)` | Animate a position input |
| `publish(tool, input, value)` | Publish an input value |
| `to_macro(name, type)` | Convert composition to macro |
| `render()` | Generate Fusion-compatible code |
| `copy()` | Copy output to clipboard |
| `save(file_name, folder)` | Save to .setting file |

---

### Tool

The `Tool` class represents individual Fusion nodes (Background, Blur, Transform, Text+, etc.).

```python
from pysion import Tool, RGBA

# Generic tool creation
blur = Tool(id="Blur", name="Blur1", position=(1, 0))

# Factory methods for common tools
bg = Tool.background("BG1", colors=RGBA(1, 0.5, 0), resolution="auto")
text = Tool.text("Title1", text="Hello", font="Arial", color=RGBA(1,1,1))
mask = Tool.mask("EllipseMask1", type="Ellipse")
merge = Tool.merge("Merge1", bg=bg, fg=text, position=(2, 0))

# Add inputs
bg.add_input(Input("Width", 1920))
bg.add_inputs(Width=1920, Height=1080)
bg.add_color_input(RGBA(1, 0, 0))

# Add mask
tool.add_mask(mask_tool)

# Create instances
instance = tool.add_instance("MyInstance", position=(3, 0))
```

**Factory Methods:**
| Method | Description |
|--------|-------------|
| `Tool.background(name, colors, resolution, position)` | Create Background node |
| `Tool.text(name, text, font, color, resolution, position)` | Create Text+ node |
| `Tool.merge(name, bg, fg, position)` | Create Merge node |
| `Tool.mask(name, type, position)` | Create mask tools (Rectangle, Ellipse, etc.) |

---

### Input

The `Input` class represents tool inputs with static values, expressions, or connections.

```python
from pysion import Input, Polyline

# Basic inputs
width_input = Input("Width", 1920)
expr_input = Input("Size", expression="time * 10", value=0)
connected_input = Input("Background", source_operator="BG1", source="Output")

# Mask input (convenience factory)
mask_input = Input.mask(source_op="EllipseMask1", source="Mask")

# Polyline (for path/shape inputs)
polyline = Polyline(points=[(0.1, 0.2), (0.5, 0.8), (0.9, 0.2)])
polyline_with_expr = Polyline.with_expression(
    points=[(0.1, 0.2), (0.5, 0.8)],
    x_expression="Point.X + 0.1",
    y_expression="Point.Y"
)
```

---

### Animation

The animation system uses `BezierSpline`, `Keyframe`, and `Curve` classes.

```python
from pysion.animation import BezierSpline, Curve, Keyframe

# Create a spline for animation
spline = BezierSpline("Opacity", default_curve=Curve.ease_in_and_out())

# Add keyframes using subscript notation
spline[0] = 0.0     # Value at frame 0
spline[24] = 1.0    # Value at frame 24
spline[48] = 0.0    # Value at frame 48

# Or add multiple keyframes at once
spline.add_keyframes([(0, 0.0), (24, 1.0), (48, 0.0)], curve=Curve.linear())

# Animation via Composition
comp = Composition()
text = comp.add_text("Title", "Hello")

# Animate a single value
opacity_spline = comp.animate(text, "Opacity")
opacity_spline[0] = 0.0
opacity_spline[24] = 1.0

# Animate position (creates XYPathModifier)
position = comp.animate_position(text, default_curve_x=Curve.ease_out())
position[0] = (0.3, 0.5)    # (x, y) at frame 0
position[24] = (0.7, 0.5)   # (x, y) at frame 24
```

**Available Curves:**
| Curve | Description |
|-------|-------------|
| `Curve.linear()` | Linear interpolation |
| `Curve.ease_in(strength)` | Ease in (slow start) |
| `Curve.ease_out(strength)` | Ease out (slow end) |
| `Curve.ease_in_and_out(strength)` | S-curve |
| `Curve.decelerate_in(strength)` | Deceleration curve |
| `Curve.decelerate_out(strength)` | Deceleration curve |
| `Curve.flat()` | No interpolation (hold) |

---

### Macro

The `Macro` class groups tools into reusable macros or groups.

```python
from pysion import Macro, Tool, RGBA

# Create a macro
macro = Macro("MyEffect", type="macro")  # or type="group"

# Add tools to macro
bg = Tool.background("BG", RGBA(1, 0, 0))
blur = Tool(id="Blur", name="Blur1")
macro.add_tools(bg, blur)

# Expose inputs as macro controls
macro.add_input(tool=blur, input_name="Blur", pretty_name="Blur Amount")
macro.add_color_input(tool=bg, name="Background Color")

# Expose output
macro.add_output(tool=blur)

# Convert composition to macro
comp = Composition()
# ... add tools to comp ...
my_macro = comp.to_macro("MyMacro", type="macro")
```

---

### Color

The `RGBA` class represents colors with values from 0.0 to 1.0.

```python
from pysion import RGBA
from pysion.color import TileColor

# Create colors
red = RGBA(1, 0, 0)                    # Red, opaque
semi_transparent_blue = RGBA(0, 0, 1, 0.5)  # Blue, 50% alpha
premultiplied = RGBA(1, 1, 1, 0.5, premultiply=True)

# Tile colors for tool nodes
from pysion.color import TileColor
TileColor.orange
TileColor.blue
TileColor.purple
# ... and more
```

---

### User Controls

Create custom controls for tools and macros.

```python
from pysion import UserControl
from pysion.values.user_controls import DType, InputControl

# Create a slider control
slider = UserControl(
    pretty_name="Blur Amount",
    input_control=InputControl.slider,
    data_type=DType.number,
    default=5.0,
    min_scale=0.0,
    max_scale=100.0
)

# Add to tool
tool.add_user_control(
    name="BlurAmount",
    pretty_name="Blur Amount",
    control=InputControl.slider,
    dtype=DType.number,
    page="Controls"
)
```

---

## Values Module

### ToolID

Pre-defined tool identifiers:

```python
from pysion.values.tool_id import ToolID

ToolID.background      # "Background"
ToolID.text            # "TextPlus"
ToolID.merge           # "Merge"
ToolID.blur            # "Blur"
ToolID.transform       # "Transform"
ToolID.media_in        # "MediaIn"
ToolID.media_out       # "MediaOut"
ToolID.color_corrector # "ColorCorrector"
ToolID.s_rectangle     # "sRectangle"
ToolID.s_ellipse       # "sEllipse"
# ... and more
```

### FuID

Fusion IDs for filters, blend modes, etc.:

```python
from pysion.values.fu_id import FuID

# Filter types
FuID.fast_gaussian()   # Fast Gaussian blur
FuID.gaussian()        # Gaussian blur
FuID.multi_box()       # Multi-box blur

# Blend modes
FuID.merge()           # Normal/merge
FuID.add()             # Additive
FuID.multiply()        # Multiply
FuID.screen()          # Screen
```

---

## Complete Example

Here's a complete example creating an animated title card:

```python
from pysion import Composition, Tool, RGBA
from pysion.animation import Curve
from pysion.values.tool_id import ToolID

# Create composition
comp = Composition()

# Create background
bg = Tool.background(
    name="Background",
    top_left=RGBA(0.1, 0.1, 0.2),  # Dark blue
    top_right=RGBA(0.1, 0.1, 0.2),
    bottom_left=RGBA(0.1, 0.1, 0.2),
    bottom_right=RGBA(0.1, 0.1, 0.2),
    resolution="auto"
)
comp.add_tools(bg)

# Create text
text = comp.add_text(
    name="TitleText",
    text="My Amazing Title",
    font_face="Open Sans",
    font_style="Bold",
    color=RGBA(1, 1, 1)
)

# Create merge
merge = comp.add_merge("FinalMerge", bg, text)

# Add MediaOut for DaVinci Resolve
media_out = Tool(id=ToolID.media_out, name="MediaOut1", position=(3, 0))
media_out.add_source_input("Input", merge.name, "Output")
comp.add_tools(media_out)

# Animate text position (slide in from left)
position = comp.animate_position(
    text,
    input_name="Center",
    default_curve_x=Curve.ease_out(0.5),
    default_curve_y=Curve.flat()
)
position[0] = (-0.5, 0.5)   # Start off-screen left
position[30] = (0.5, 0.5)   # End at center

# Animate text opacity (fade in)
opacity = comp.animate(text, "Opacity")
opacity[0] = 0.0
opacity[20] = 1.0

# Output
print(comp.render())

# Copy to clipboard (paste into Fusion)
comp.copy()
```

---

## Workflow

1. **Write Python code** defining your composition
2. **Run the script** to generate Fusion code
3. **Copy to clipboard** with `comp.copy()` or save with `comp.save()`
4. **Paste into Fusion** (Ctrl/Cmd+V in the Flow view)
5. **Edit as needed** in Fusion's GUI

---

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pysion

# Run specific test file
pytest tests/test_composition.py
```

---

## Dependencies

### Runtime
- Python >= 3.10 (uses pattern matching, type hints)
- No required external packages (pure Python)

### Optional
- `pyperclip` - For clipboard support (`comp.copy()`)

### Development
- `pytest` - Testing
- `pytest-cov` - Coverage
- `flake8` - Linting

---

## Related Projects

- **FuPlot** (https://github.com/brunocbreis/FuPlot): Data visualization tool that uses Pysion to generate charts as editable Fusion node trees.

---

## Current Limitations

- Still work-in-progress, expect syntax changes
- Not all Fusion tool types have dedicated factory methods
- Limited documentation/docstrings
- Macros inside macros may have issues

---

## API Reference Summary

### Main Classes

| Class | Import | Purpose |
|-------|--------|---------|
| `Composition` | `from pysion import Composition` | Main container for compositions |
| `Tool` | `from pysion import Tool` | Fusion nodes/tools |
| `Input` | `from pysion import Input` | Tool inputs |
| `Polyline` | `from pysion import Polyline` | Path/shape points |
| `Macro` | `from pysion import Macro` | Tool grouping |
| `RGBA` | `from pysion import RGBA` | Color values |
| `UserControl` | `from pysion import UserControl` | Custom controls |

### Animation Classes

| Class | Import | Purpose |
|-------|--------|---------|
| `BezierSpline` | `from pysion.animation import BezierSpline` | Animated values |
| `Curve` | `from pysion.animation import Curve` | Animation curves |
| `Keyframe` | `from pysion.animation import Keyframe` | Individual keyframes |

### Value Classes

| Class | Import | Purpose |
|-------|--------|---------|
| `ToolID` | `from pysion.values.tool_id import ToolID` | Tool identifiers |
| `FuID` | `from pysion.values.fu_id import FuID` | Fusion IDs |
| `DType` | `from pysion.values.user_controls import DType` | Data types |
| `InputControl` | `from pysion.values.user_controls import InputControl` | Control types |
| `TileColor` | `from pysion.color import TileColor` | Tile colors |

### Utility Functions

| Function | Import | Purpose |
|----------|--------|---------|
| `fusion_coords` | `from pysion import fusion_coords` | Convert to Fusion grid coordinates |
