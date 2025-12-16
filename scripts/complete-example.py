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
