"""Generate learning system workflow diagram for README."""
from PIL import Image, ImageDraw, ImageFont
import math

SCALE = 2
TARGET_W, TARGET_H = 1200, 680

def s(val):
    return int(val * SCALE)

# Colors (GitHub dark theme)
BG = (13, 17, 23)
CARD_BG = (22, 27, 34)
BORDER = (48, 54, 61)
TEXT = (201, 209, 217)
TEXT_DIM = (110, 118, 129)
BLUE = (88, 166, 255)
GREEN = (126, 231, 135)
PURPLE = (210, 168, 255)
ORANGE = (240, 136, 62)
WHITE = (240, 246, 252)
TEAL = (63, 185, 180)
PINK = (219, 97, 162)

# Fonts
FONT_BODY = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", s(18))
FONT_BOLD = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", s(20))
FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", s(32))
FONT_SUBTITLE = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", s(16))
FONT_SMALL = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", s(14))
FONT_LABEL = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", s(14))

img = Image.new("RGB", (s(TARGET_W), s(TARGET_H)), BG)
draw = ImageDraw.Draw(img)

def make_node(x, y, w, h):
    return {
        "rect": (s(x), s(y), s(x + w), s(y + h)),
        "top": (s(x + w / 2), s(y)),
        "bottom": (s(x + w / 2), s(y + h)),
        "left": (s(x), s(y + h / 2)),
        "right": (s(x + w), s(y + h / 2)),
        "center": (s(x + w / 2), s(y + h / 2)),
    }

def draw_arrow(start, end, color, width=2, head_size=10):
    w = s(width)
    hs = s(head_size)
    draw.line([start, end], fill=color, width=w)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    x, y = end
    for da in [2.5, -2.5]:
        ax = x - hs * math.cos(angle + da)
        ay = y - hs * math.sin(angle + da)
        draw.line([(x, y), (int(ax), int(ay))], fill=color, width=w)

# Title
draw.text((s(TARGET_W / 2), s(30)), "QDD Learning System", font=FONT_TITLE, fill=WHITE, anchor="mt")
draw.text((s(TARGET_W / 2), s(65)), "6-Step First-Principles Learning Workflow", font=FONT_SUBTITLE, fill=TEXT_DIM, anchor="mt")

# Step definitions
steps = [
    ("1. DIAGNOSE", "Map knowledge\ngaps", ORANGE, "~15 min"),
    ("2. LEARN", "Interactive\nlesson", BLUE, "~35 min"),
    ("3. DISTILL", "Write reference\ncard", TEAL, "~15 min"),
    ("4. PRACTICE", "Applied problems\n& judgment", PURPLE, "~50 min"),
    ("5. GRADE", "Review &\nre-teach gaps", GREEN, "~15 min"),
    ("6. DRILL", "Interview\nsimulation", PINK, "~10 min"),
]

# Layout: 6 boxes in a row
box_w = 155
box_h = 100
start_y = 120
num = len(steps)
spacing = (TARGET_W - num * box_w) / (num + 1)

nodes = []
for i, (title, desc, color, time) in enumerate(steps):
    x = spacing + i * (box_w + spacing)
    node = make_node(x, start_y, box_w, box_h)
    nodes.append(node)

# Draw arrows between nodes
for i in range(len(nodes) - 1):
    draw_arrow(nodes[i]["right"], nodes[i + 1]["left"], BORDER, width=2, head_size=8)

# Draw step boxes
for i, (title, desc, color, time) in enumerate(steps):
    node = nodes[i]
    # Glow effect
    for offset in [6, 3]:
        glow_rect = (node["rect"][0] - s(offset), node["rect"][1] - s(offset),
                     node["rect"][2] + s(offset), node["rect"][3] + s(offset))
        glow_color = tuple(c // 6 for c in color)
        draw.rounded_rectangle(glow_rect, radius=s(12), fill=glow_color)

    draw.rounded_rectangle(node["rect"], radius=s(10), fill=CARD_BG, outline=color, width=s(2))

    # Step number badge
    badge_x = node["rect"][0] + s(10)
    badge_y = node["rect"][1] + s(8)
    draw.rounded_rectangle((badge_x, badge_y, badge_x + s(20), badge_y + s(16)),
                          radius=s(8), fill=color)
    draw.text((badge_x + s(10), badge_y + s(8)), str(i + 1), font=FONT_LABEL, fill=BG, anchor="mm")

    # Title
    draw.text((node["center"][0], node["rect"][1] + s(30)), title.split(". ")[1],
              font=FONT_BOLD, fill=color, anchor="mt")

    # Description
    lines = desc.split("\n")
    for j, line in enumerate(lines):
        draw.text((node["center"][0], node["rect"][1] + s(55 + j * 18)),
                  line, font=FONT_SMALL, fill=TEXT_DIM, anchor="mt")

    # Time estimate
    draw.text((node["center"][0], node["rect"][3] - s(8)),
              time, font=FONT_SMALL, fill=TEXT_DIM, anchor="mb")

# Teaching method section
method_y = 260
draw.text((s(TARGET_W / 2), s(method_y)), "Teaching Method (Step 2)", font=FONT_BOLD, fill=WHITE, anchor="mt")

method_steps = [
    ("ANCHOR", "Connect to something\nphysical you've touched", ORANGE),
    ("TRACE", "Walk cause-effect chain\nlink by link", BLUE),
    ("NUMBERS", "Prove with your\nhardware values", TEAL),
    ("PREDICT", "What-if scenarios to\ntest understanding", PURPLE),
]

method_box_w = 240
method_box_h = 75
method_spacing = (TARGET_W - len(method_steps) * method_box_w) / (len(method_steps) + 1)
method_start_y = method_y + 35

method_nodes = []
for i, (title, desc, color) in enumerate(method_steps):
    x = method_spacing + i * (method_box_w + method_spacing)
    node = make_node(x, method_start_y, method_box_w, method_box_h)
    method_nodes.append((node, title, desc, color))

# Arrows between method nodes
for i in range(len(method_nodes) - 1):
    draw_arrow(method_nodes[i][0]["right"], method_nodes[i + 1][0]["left"], BORDER, width=2, head_size=8)

# Draw method boxes
for node, title, desc, color in method_nodes:
    draw.rounded_rectangle(node["rect"], radius=s(8), fill=CARD_BG, outline=color, width=s(1))
    draw.text((node["center"][0], node["rect"][1] + s(15)), title, font=FONT_BOLD, fill=color, anchor="mt")
    lines = desc.split("\n")
    for j, line in enumerate(lines):
        draw.text((node["center"][0], node["rect"][1] + s(38 + j * 17)),
                  line, font=FONT_SMALL, fill=TEXT_DIM, anchor="mt")

# Gamification section
gam_y = 420
draw.text((s(TARGET_W / 2), s(gam_y)), "Gamification", font=FONT_BOLD, fill=WHITE, anchor="mt")

# Three gamification columns
gam_items = [
    ("Dashboard", "Progress bars, streak counter,\nnext mission, time estimates", BLUE,
     "Opens on /learn"),
    ("Unlocks", "Real-world milestones gated\nby knowledge acquisition", GREEN,
     "Resume, test campaign, LinkedIn..."),
    ("Streaks", "Consecutive days with study\nactivity logged", ORANGE,
     "Evening nudge if no activity"),
]

gam_box_w = 340
gam_box_h = 110
gam_spacing = (TARGET_W - len(gam_items) * gam_box_w) / (len(gam_items) + 1)
gam_start_y = gam_y + 35

for i, (title, desc, color, detail) in enumerate(gam_items):
    x = gam_spacing + i * (gam_box_w + gam_spacing)
    node = make_node(x, gam_start_y, gam_box_w, gam_box_h)
    draw.rounded_rectangle(node["rect"], radius=s(8), fill=CARD_BG, outline=color, width=s(1))
    draw.text((node["center"][0], node["rect"][1] + s(18)), title, font=FONT_BOLD, fill=color, anchor="mt")
    lines = desc.split("\n")
    for j, line in enumerate(lines):
        draw.text((node["center"][0], node["rect"][1] + s(42 + j * 17)),
                  line, font=FONT_SMALL, fill=TEXT_DIM, anchor="mt")
    draw.text((node["center"][0], node["rect"][3] - s(12)),
              detail, font=FONT_SMALL, fill=TEXT_DIM, anchor="mb")

# Footer
draw.text((s(TARGET_W / 2), s(TARGET_H - 20)),
          "Built for Tesla Optimus interview prep  |  13 topics  |  ~2 hrs per topic  |  4-week program",
          font=FONT_SMALL, fill=TEXT_DIM, anchor="mb")

# Downscale and save
final = img.resize((TARGET_W, TARGET_H), Image.Resampling.LANCZOS)
final.save("testing/learn/learning-system-diagram.png", quality=95)
print(f"Saved diagram: {TARGET_W}x{TARGET_H}")
