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