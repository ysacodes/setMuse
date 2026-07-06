"""
Generates static PNG showcase images of the ClosetMuse UI — non-functional
mockups so judges can see the intended look/feel and feature flow without a
built front-end. Uses the project's real color tokens (config.THEME) and the
Nunito / Dancing-Script (decorative "Lavonia-style" display) fonts bundled
in ui_mockups/assets/.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import THEME

ASSETS = os.path.join(os.path.dirname(__file__), "assets")
OUT = os.path.dirname(__file__)

CREAM = THEME.cream
TAN = THEME.tan
ESPRESSO = THEME.espresso
BLUSH = THEME.blush
WHITE = "#FFFFFF"

def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def font(name, size):
    return ImageFont.truetype(os.path.join(ASSETS, name), size)

F_DISPLAY = "DancingScript-Bold.ttf"
F_HEAVY = "Nunito-ExtraBold.ttf"
F_BOLD = "Nunito-Bold.ttf"
F_SEMI = "Nunito-SemiBold.ttf"
F_REG = "Nunito-Regular.ttf"


def rrect(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def soft_shadow(img, box, radius, blur=18, opacity=60, offset=(0, 8)):
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    x0, y0, x1, y1 = box
    sd.rounded_rectangle((x0 + offset[0], y0 + offset[1], x1 + offset[0], y1 + offset[1]),
                          radius=radius, fill=(0, 0, 0, opacity))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(shadow)


def chip(draw, xy, text, f, fg, bg, pad_x=14, pad_y=7):
    x, y = xy
    w = draw.textlength(text, font=f)
    h = f.size
    rrect(draw, (x, y, x + w + pad_x * 2, y + h + pad_y * 2), radius=(h + pad_y * 2) // 2, fill=bg)
    draw.text((x + pad_x, y + pad_y - 2), text, font=f, fill=fg)
    return x + w + pad_x * 2


def text_center(draw, cx, y, text, f, fill):
    w = draw.textlength(text, font=f)
    draw.text((cx - w / 2, y), text, font=f, fill=fill)
    return w


def garment_icon(draw, box, kind, color):
    """Simple flat-icon silhouettes so mockups don't need real photography."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    cx, cy = x0 + w / 2, y0 + h / 2
    c = hexrgb(color) if color.startswith("#") else color
    if kind == "dress":
        pts = [(cx, y0 + h*0.05), (cx - w*0.18, y0 + h*0.28), (cx - w*0.38, y1 - h*0.05),
               (cx + w*0.38, y1 - h*0.05), (cx + w*0.18, y0 + h*0.28)]
        draw.polygon(pts, fill=c)
        draw.ellipse((cx - w*0.09, y0, cx + w*0.09, y0 + h*0.14), fill=c)
    elif kind == "top":
        draw.polygon([(cx - w*0.32, y0 + h*0.18), (cx - w*0.14, y0), (cx + w*0.14, y0),
                      (cx + w*0.32, y0 + h*0.18), (cx + w*0.22, y0 + h*0.32), (cx + w*0.14, y0 + h*0.2),
                      (cx + w*0.14, y1), (cx - w*0.14, y1), (cx - w*0.14, y0 + h*0.2),
                      (cx - w*0.22, y0 + h*0.32)], fill=c)
    elif kind == "bottom":
        rrect(draw, (cx - w*0.28, y0, cx + w*0.28, y0 + h*0.15), radius=6, fill=c)
        draw.polygon([(cx - w*0.28, y0 + h*0.15), (cx + w*0.28, y0 + h*0.15),
                      (cx + w*0.06, y1), (cx - w*0.02, y1)], fill=c)
        draw.polygon([(cx - w*0.28, y0 + h*0.15), (cx + w*0.02, y0+h*0.15),
                      (cx - w*0.06, y1), (cx - w*0.28, y1)], fill=c)
    elif kind == "outerwear":
        draw.polygon([(cx - w*0.36, y0 + h*0.2), (cx - w*0.16, y0), (cx, y0 + h*0.1),
                      (cx + w*0.16, y0), (cx + w*0.36, y0 + h*0.2), (cx + w*0.28, y1),
                      (cx + w*0.12, y1), (cx + w*0.12, y0+h*0.45), (cx-w*0.12, y0+h*0.45),
                      (cx - w*0.12, y1), (cx - w*0.28, y1)], fill=c)
    elif kind == "shoes":
        draw.pieslice((cx - w*0.34, cy - h*0.1, cx + w*0.1, cy + h*0.3), 180, 360, fill=c)
        draw.rounded_rectangle((cx - w*0.34, cy, cx + w*0.3, cy + h*0.22), radius=8, fill=c)
    else:  # accessory / set
        draw.ellipse((cx - w*0.28, cy - h*0.28, cx + w*0.28, cy + h*0.28), outline=c, width=6)


def draw_phone_frame(img, x, y, w, h, radius=52):
    draw = ImageDraw.Draw(img)
    rrect(draw, (x, y, x + w, y + h), radius, fill=hexrgb(ESPRESSO))
    inset = 10
    rrect(draw, (x + inset, y + inset, x + w - inset, y + h - inset), radius - 6, fill=hexrgb(CREAM))
    # notch
    notch_w, notch_h = w * 0.32, 22
    rrect(draw, (x + w/2 - notch_w/2, y + inset, x + w/2 + notch_w/2, y + inset + notch_h), 12, fill=hexrgb(ESPRESSO))
    return (x + inset, y + inset + notch_h + 6, x + w - inset, y + h - inset)  # screen content box


def status_bar(draw, x0, y0, x1, fg):
    f = font(F_BOLD, 15)
    draw.text((x0 + 18, y0 + 6), "9:41", font=f, fill=fg)
    text_center(draw, (x0 + x1) / 2 + (x1-x0)/2 - 40, y0+6, "●●●", f, fg)


# ---------------------------------------------------------------- Screen 1
def make_closet_library():
    W, H = 1000, 1500
    img = Image.new("RGBA", (W, H), hexrgb(CREAM) + (255,))
    phone_w, phone_h = 900, 1400
    px, py = (W - phone_w)//2, (H-phone_h)//2
    soft_shadow(img, (px, py, px+phone_w, py+phone_h), 52, blur=30, opacity=70)
    sx0, sy0, sx1, sy1 = draw_phone_frame(img, px, py, phone_w, phone_h)
    draw = ImageDraw.Draw(img)
    status_bar(draw, sx0, sy0, sx1, hexrgb(ESPRESSO))

    top = sy0 + 40
    draw.text((sx0+34, top), "ClosetMuse", font=font(F_DISPLAY, 54), fill=hexrgb(ESPRESSO))
    draw.text((sx0+34, top+66), "Your Closet Library", font=font(F_SEMI, 22), fill=hexrgb(TAN))

    # search + upload row
    row_y = top + 118
    rrect(draw, (sx0+34, row_y, sx1-140, row_y+56), 28, fill=WHITE, outline=hexrgb(TAN), width=2)
    draw.text((sx0+58, row_y+14), "🔍  Search style, color, occasion…", font=font(F_REG, 20), fill=hexrgb(TAN))
    rrect(draw, (sx1-124, row_y, sx1-34, row_y+56), 28, fill=hexrgb(BLUSH))
    draw.text((sx1-108, row_y+14), "+ Add", font=font(F_BOLD, 20), fill=hexrgb(ESPRESSO))

    # filter chips
    chip_y = row_y + 74
    cx = sx0 + 34
    for label, active in [("All", True), ("Dresses", False), ("Tops", False), ("Outerwear", False), ("Shoes", False)]:
        bg = hexrgb(ESPRESSO) if active else WHITE
        fg = WHITE if active else hexrgb(ESPRESSO)
        cx = chip(draw, (cx, chip_y), label, font(F_SEMI, 16), fg, bg) + 10

    # garment grid
    demo_items = [
        ("dress", "#E07A6B", "Floral Wrap Dress", ["floral","bohemian"]),
        ("top", "#F4EFE3", "Ruffle Blouse", ["ruffles"]),
        ("outerwear", "#2E2A28", "Tailored Blazer", ["business"]),
        ("outerwear", "#3E6EA5", "Denim Jacket", ["streetwear"]),
        ("bottom", "#4B4B4E", "Tailored Trousers", ["minimalist"]),
        ("top", "#C9B7DE", "Knit Sweater", ["pastel"]),
        ("shoes", "#7A4B32", "Ankle Boots", ["vintage"]),
        ("dress", "#F3EFE0", "Linen Sundress", ["minimalist"]),
    ]
    grid_top = chip_y + 60
    cols, gap = 2, 24
    card_w = (sx1 - sx0 - 34*2 - gap) // cols
    card_h = 220
    for i, (kind, color, name, tags) in enumerate(demo_items):
        col, row = i % cols, i // cols
        cx0 = sx0 + 34 + col*(card_w+gap)
        cy0 = grid_top + row*(card_h+gap)
        rrect(draw, (cx0, cy0, cx0+card_w, cy0+card_h), 22, fill=WHITE)
        icon_box = (cx0+20, cy0+16, cx0+card_w-20, cy0+card_h-70)
        rrect(draw, icon_box, 16, fill=hexrgb(CREAM))
        garment_icon(draw, (icon_box[0]+20, icon_box[1]+14, icon_box[2]-20, icon_box[3]-14), kind, color)
        draw.text((cx0+18, cy0+card_h-58), name, font=font(F_BOLD, 17), fill=hexrgb(ESPRESSO))
        tx = cx0+18
        for t in tags:
            tx = chip(draw, (tx, cy0+card_h-30), t, font(F_SEMI, 12), hexrgb(ESPRESSO), hexrgb(BLUSH), pad_x=8, pad_y=3) + 6

    # bottom nav
    nav_y = sy1 - 90
    rrect(draw, (sx0, nav_y, sx1, sy1), 0, fill=WHITE)
    labels = ["👗 Closet", "✨ Today", "📊 Insights", "⚙️ Settings"]
    seg = (sx1-sx0)/len(labels)
    for i, lab in enumerate(labels):
        fg = hexrgb(ESPRESSO) if i == 0 else hexrgb(TAN)
        text_center(draw, sx0 + seg*i + seg/2, nav_y+28, lab, font(F_SEMI, 15), fg)

    img.convert("RGB").save(os.path.join(OUT, "01_closet_library.png"))
    print("saved 01_closet_library.png")


# ---------------------------------------------------------------- Screen 2
def make_outfit_generator():
    W, H = 1000, 1500
    img = Image.new("RGBA", (W, H), hexrgb(CREAM) + (255,))
    phone_w, phone_h = 900, 1400
    px, py = (W - phone_w)//2, (H-phone_h)//2
    soft_shadow(img, (px, py, px+phone_w, py+phone_h), 52, blur=30, opacity=70)
    sx0, sy0, sx1, sy1 = draw_phone_frame(img, px, py, phone_w, phone_h)
    draw = ImageDraw.Draw(img)
    status_bar(draw, sx0, sy0, sx1, hexrgb(ESPRESSO))

    top = sy0 + 40
    draw.text((sx0+34, top), "Today's Look", font=font(F_DISPLAY, 54), fill=hexrgb(ESPRESSO))
    draw.text((sx0+34, top+66), "Mon, Jul 6 · Hong Kong", font=font(F_SEMI, 20), fill=hexrgb(TAN))

    # context cards row: weather + calendar
    cardy = top + 116
    card_h = 110
    card_w = (sx1 - sx0 - 34*2 - 20)//2
    # weather card
    rrect(draw, (sx0+34, cardy, sx0+34+card_w, cardy+card_h), 22, fill=hexrgb(ESPRESSO))
    draw.text((sx0+54, cardy+16), "☀️  28°C", font=font(F_HEAVY, 26), fill=WHITE)
    draw.text((sx0+54, cardy+62), "Overcast · 60% rain", font=font(F_REG, 15), fill=hexrgb(CREAM))
    # calendar card
    cx0b = sx0+34+card_w+20
    rrect(draw, (cx0b, cardy, cx0b+card_w, cardy+card_h), 22, fill=WHITE, outline=hexrgb(TAN), width=2)
    draw.text((cx0b+20, cardy+16), "📅  Business", font=font(F_HEAVY, 22), fill=hexrgb(ESPRESSO))
    draw.text((cx0b+20, cardy+62), "Client Presentation 2pm", font=font(F_REG, 14), fill=hexrgb(TAN))

    # agent trace strip
    trace_y = cardy + card_h + 24
    rrect(draw, (sx0+34, trace_y, sx1-34, trace_y+44), 22, fill=hexrgb(BLUSH))
    draw.text((sx0+52, trace_y+11), "🤖 Weather Agent + Calendar Agent → Outfit Curator", font=font(F_SEMI, 15), fill=hexrgb(ESPRESSO))

    # hero outfit card
    hero_y = trace_y + 68
    hero_h = 560
    rrect(draw, (sx0+34, hero_y, sx1-34, hero_y+hero_h), 28, fill=WHITE)
    draw.text((sx0+58, hero_y+22), "Option 1 · Best Match", font=font(F_BOLD, 20), fill=hexrgb(ESPRESSO))
    icon_area = (sx0+58, hero_y+66, sx1-58, hero_y+hero_h-150)
    rrect(draw, icon_area, 20, fill=hexrgb(CREAM))
    pieces = [("dress", "#E07A6B"), ("outerwear", "#2E2A28"), ("shoes", "#7A4B32")]
    seg_w = (icon_area[2]-icon_area[0]) / len(pieces)
    for i, (kind, color) in enumerate(pieces):
        bx0 = icon_area[0] + i*seg_w
        garment_icon(draw, (bx0+20, icon_area[1]+20, bx0+seg_w-20, icon_area[3]-20), kind, color)
    rationale = "28°C, overcast, 60% rain + client presentation today → business-ready dress, a light layer, and boots that won't slip on wet pavement."
    # wrap rationale text
    import textwrap
    wrapped = textwrap.wrap(rationale, width=48)
    ry = hero_y + hero_h - 130
    for line in wrapped:
        draw.text((sx0+58, ry), line, font=font(F_REG, 16), fill=hexrgb(TAN))
        ry += 24

    # action buttons
    by = hero_y + hero_h + 20
    rrect(draw, (sx0+34, by, sx0+34+((sx1-sx0-68-16)//2), by+64), 32, fill=hexrgb(ESPRESSO))
    text_center(draw, sx0+34+((sx1-sx0-68-16)//4), by+18, "Wear this", font(F_BOLD, 20), WHITE)
    bx2 = sx0+34+((sx1-sx0-68-16)//2)+16
    rrect(draw, (bx2, by, sx1-34, by+64), 32, fill=WHITE, outline=hexrgb(ESPRESSO), width=2)
    text_center(draw, (bx2+sx1-34)/2, by+18, "See 2 more options", font(F_BOLD, 18), hexrgb(ESPRESSO))

    nav_y = sy1 - 90
    rrect(draw, (sx0, nav_y, sx1, sy1), 0, fill=WHITE)
    labels = ["👗 Closet", "✨ Today", "📊 Insights", "⚙️ Settings"]
    seg = (sx1-sx0)/len(labels)
    for i, lab in enumerate(labels):
        fg = hexrgb(ESPRESSO) if i == 1 else hexrgb(TAN)
        text_center(draw, sx0 + seg*i + seg/2, nav_y+28, lab, font(F_SEMI, 15), fg)

    img.convert("RGB").save(os.path.join(OUT, "02_outfit_generator.png"))
    print("saved 02_outfit_generator.png")


# ---------------------------------------------------------------- Screen 3: architecture
def make_architecture_diagram():
    W, H = 1400, 900
    img = Image.new("RGBA", (W, H), hexrgb(CREAM) + (255,))
    draw = ImageDraw.Draw(img)
    draw.text((60, 40), "ClosetMuse — Multi-Agent Pipeline", font=font(F_DISPLAY, 46), fill=hexrgb(ESPRESSO))
    draw.text((60, 100), "Google ADK  ·  MCP Server  ·  Agent Skills  ·  Security Guardrails", font=font(F_SEMI, 20), fill=hexrgb(TAN))

    def box(x, y, w, h, label, sub, fillc, fg=WHITE):
        rrect(draw, (x, y, x+w, y+h), 20, fill=fillc)
        text_center(draw, x+w/2, y+h/2-24, label, font(F_BOLD, 20), fg)
        if sub:
            text_center(draw, x+w/2, y+h/2+4, sub, font(F_REG, 14), fg)

    def arrow(x0, y0, x1, y1):
        draw.line((x0, y0, x1, y1), fill=hexrgb(ESPRESSO), width=4)
        angle = math.atan2(y1-y0, x1-x0)
        for a in (angle+2.6, angle-2.6):
            draw.line((x1, y1, x1 - 14*math.cos(a), y1 - 14*math.sin(a)), fill=hexrgb(ESPRESSO), width=4)

    # Root
    box(560, 170, 280, 80, "Root / Stylist Agent", "SequentialAgent (ADK)", hexrgb(ESPRESSO))
    # Parallel context box
    rrect(draw, (300, 300, 1100, 460), 26, outline=hexrgb(TAN), width=3, fill=None)
    text_center(draw, 700, 312, "ParallelAgent — context gathering", font(F_SEMI, 16), hexrgb(TAN))
    box(340, 350, 320, 90, "Weather Agent", "OpenWeatherMap tool", hexrgb(BLUSH), fg=hexrgb(ESPRESSO))
    box(740, 350, 320, 90, "Calendar Agent", "Google Calendar tool", hexrgb(BLUSH), fg=hexrgb(ESPRESSO))
    # Vision + curator
    box(160, 560, 300, 90, "Style Vision Agent", "Tags photos → closet DB", hexrgb(TAN), fg=hexrgb(ESPRESSO))
    box(560, 560, 300, 90, "Outfit Curator Agent", "outfit_curation.skill.md", hexrgb(ESPRESSO))
    box(960, 560, 300, 90, "Security Guardrails", "upload/PII/injection/allow-list", hexrgb(TAN), fg=hexrgb(ESPRESSO))
    # MCP row
    box(400, 730, 600, 90, "ClosetMuse MCP Server", "get_weather · get_calendar_events · list_wardrobe_items · record_outfit_feedback", "#3E6EA5")

    arrow(700, 250, 700, 300)
    arrow(500, 440, 500, 560)
    arrow(900, 440, 900, 560)
    arrow(310, 605, 560, 605)
    arrow(860, 605, 960, 605)
    arrow(700, 650, 700, 730)

    img.convert("RGB").save(os.path.join(OUT, "03_agent_architecture.png"))
    print("saved 03_agent_architecture.png")


# ---------------------------------------------------------------- Screen 4: card/thumbnail
def make_card_thumbnail():
    W, H = 1200, 630
    img = Image.new("RGBA", (W, H), hexrgb(CREAM) + (255,))
    draw = ImageDraw.Draw(img)
    # decorative blush blob
    draw.ellipse((820, -120, 1300, 360), fill=hexrgb(BLUSH))
    draw.ellipse((-150, 380, 350, 820), fill=hexrgb(TAN))

    draw.text((70, 170), "ClosetMuse", font=font(F_DISPLAY, 108), fill=hexrgb(ESPRESSO))
    draw.text((76, 300), "AI outfit planning from your own closet", font=font(F_SEMI, 30), fill=hexrgb(ESPRESSO))
    draw.text((76, 350), "Weather + calendar aware · multi-agent · built with Google ADK", font=font(F_REG, 20), fill="#5c4433")

    # mini phone graphic on the right
    phone_w, phone_h = 300, 460
    ppx, ppy = 860, 100
    soft_shadow(img, (ppx, ppy, ppx+phone_w, ppy+phone_h), 40, blur=20, opacity=60)
    sx0, sy0, sx1, sy1 = draw_phone_frame(img, ppx, ppy, phone_w, phone_h, radius=34)
    d2 = ImageDraw.Draw(img)
    d2.text((sx0+16, sy0+16), "ClosetMuse", font=font(F_DISPLAY, 26), fill=hexrgb(ESPRESSO))
    icon_area = (sx0+16, sy0+60, sx1-16, sy0+230)
    rrect(d2, icon_area, 14, fill=hexrgb(CREAM))
    garment_icon(d2, (icon_area[0]+16, icon_area[1]+10, icon_area[2]-16, icon_area[3]-10), "dress", "#E07A6B")
    d2.rounded_rectangle((sx0+16, sy0+244, sx1-16, sy0+280), 12, fill=hexrgb(ESPRESSO))
    d2.text((sx0+30, sy0+252), "Wear this", font=font(F_BOLD, 16), fill="#FFFFFF")

    img.convert("RGB").save(os.path.join(OUT, "00_card_thumbnail.png"))
    print("saved 00_card_thumbnail.png")


if __name__ == "__main__":
    make_card_thumbnail()
    make_closet_library()
    make_outfit_generator()
    make_architecture_diagram()
