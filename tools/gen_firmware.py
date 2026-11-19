#!/usr/bin/env python3
# מחולל קושחה: קורא design/themes.json + design/screens/*.json + design/VERSION
# וכותב firmware/generated/ui.yaml (LVGL + גופן + סקריפטים שמחברים מצב ממסר למסך).
# שימוש: python3 tools/gen_firmware.py [--theme navygrad]
import json, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
theme_name = sys.argv[sys.argv.index("--theme") + 1] if "--theme" in sys.argv else "navy"
ALL = json.load(open(f"{ROOT}/design/themes.json"))
TH = ALL[theme_name]
SCR = json.load(open(f"{ROOT}/design/screens/keys.json"))
VER = open(f"{ROOT}/design/VERSION").read().strip()

def hexc(c): return "0x" + c.lstrip("#").upper()
def colors(v):   # "#RRGGBB" או גרדיאנט CSS -> רשימת צבעים
    return re.findall(r"#[0-9A-Fa-f]{6}", v)
def vis(t): return t[::-1]   # עברית בסדר ויזואלי: אין תמיכת bidi ב-LVGL (כמו בקושחה של גיא)

W, H = SCR["size"]
n = len(SCR["keys"])
col_w = W // n
RT = ["navy", "black", "white"]            # ערכות שנבחרות בזמן ריצה (אחידות, בלי גרדיאנט)
HEB = {"navy": "כחול", "black": "שחור", "white": "לבן"}
def gold_of(T): return colors(ALL[T]["gold"])[len(colors(ALL[T]["gold"]))//2]
bg = colors(TH.get("bg", TH["ground"]))
out = [f"# נוצר אוטומטית ע\"י tools/gen_firmware.py (ערכה התחלתית: {theme_name}, גרסה {VER}). לא לערוך ידנית.",
       "font:",
       ('  - file: "fonts/Heebo.ttf"' if "--font-local" in sys.argv else '  - file: "gfonts://Heebo"'), "    id: f_name", "    size: 44", "    bpp: 4",
       '    glyphs: "אבגדהוזחטיכלמנסעפצקרשתךםןףץ0123456789 ."',
       "select:", "  - platform: template", "    id: theme_sel", '    name: "ערכת נושא"', f"    options: [{', '.join(RT)}]",
       f"    initial_option: {theme_name if theme_name in RT else 'navy'}", "    optimistic: true", "    restore_value: true",
       "    on_value:", "      - script.execute: ui_refresh",
       "lvgl:", "  displays: [lcd]", "  touchscreens: [touch]", "  rotation: 90", "  buffer_size: 50%",
       f"  bg_color: {hexc(bg[0])}", "  text_font: f_name", f"  text_color: {hexc(TH['ink'])}", "  pages:", "    - id: keys", "      widgets:",
       "        - obj:", "            id: bgroot", "            x: 0", "            y: 0", f"            width: {W}", f"            height: {H}",
       "            radius: 0", "            border_width: 0", "            pad_all: 0", f"            bg_color: {hexc(bg[0])}", "            clickable: false"]
for i, k in enumerate(SCR["keys"], 1):
    out += [
     "        - obj:", f"            id: key{i}", f"            x: {(n-i)*col_w}", "            y: 40",
     f"            width: {col_w}", f"            height: {H-112}", "            bg_opa: TRANSP", "            border_width: 0",
     "            radius: 0", "            pad_all: 0", "            widgets:",
     "              - label:", f"                  id: name{i}", f'                  text: "{vis(k["name"])}"', "                  align: CENTER", "                  y: -12",
     "              - obj:", f"                  id: bar{i}", "                  align: CENTER", "                  y: 36",
     "                  width: 140", "                  height: 6", "                  radius: 3", "                  border_width: 0",
     f"                  bg_color: {hexc(TH['track'])}",
     f"            on_click:", f"              - switch.toggle: relay{k['relay']}"]
# רצועת משיכה בראש המסך + פאנל ערכות נושא
out += ["        - obj:", "            id: handle", "            x: 0", "            y: 0", f"            width: {W}", "            height: 40",
        "            bg_opa: TRANSP", "            border_width: 0", "            radius: 0", "            pad_all: 0",
        "            on_click:", "              - lvgl.widget.show: panel",
        "            widgets:", "              - obj:", "                  id: grip", "                  align: CENTER", "                  width: 80", "                  height: 5",
        "                  radius: 3", "                  border_width: 0", f"                  bg_color: {hexc(TH['track'])}",
        "        - obj:", "            id: panel", "            hidden: true", "            x: 0", "            y: 0", f"            width: {W}", "            height: 230",
        "            radius: 0", "            border_width: 0", "            pad_all: 0", f"            bg_color: {hexc(TH['surface'])}",
        "            widgets:",
        "              - label:", "                  id: panel_title", f'                  text: "{vis("ערכת נושא")}"', "                  align: TOP_MID", "                  y: 14"]
for j, t in enumerate(RT):
    out += ["              - obj:", f"                  id: tbtn_{t}", "                  align: TOP_MID", f"                  x: {(1-j)*-240}", "                  y: 80",
            "                  width: 200", "                  height: 70", "                  radius: 12", "                  border_width: 2",
            f"                  bg_color: {hexc(ALL[t]['ground'])}", f"                  border_color: {hexc(gold_of(t))}",
            "                  on_click:", "                    - select.set:", "                        id: theme_sel", f"                        option: {t}",
            "                  widgets:", "                    - label:", f'                        text: "{vis(HEB[t])}"', f"                        text_color: {hexc(ALL[t]['ink'])}", "                        align: CENTER"]
out += ["              - obj:", "                  id: panel_close", "                  align: BOTTOM_MID", "                  y: -10", "                  width: 160", "                  height: 50",
        "                  radius: 12", "                  border_width: 0", f"                  bg_color: {hexc(TH['track'])}",
        "                  on_click:", "                    - lvgl.widget.hide: panel",
        "                  widgets:", "                    - label:", f'                        text: "{vis("סגור")}"', "                        align: CENTER"]
out += ["script:"]
for T in RT:
    C = ALL[T]; gd = hexc(gold_of(T))
    out += [f"  - id: ui_theme_{T}", "    then:"]
    def up(i_, **kw):
        r = ["      - lvgl.widget.update:", f"          id: {i_}"]
        r += [f"          {k}: {v}" for k, v in kw.items()]
        return r
    out += up("bgroot", bg_color=hexc(C["ground"])) + up("panel", bg_color=hexc(C["surface"]))
    out += up("panel_title", text_color=hexc(C["ink"])) + up("panel_close", bg_color=hexc(C["track"])) + up("grip", bg_color=hexc(C["track"]))
    for i, k in enumerate(SCR["keys"], 1):
        out += up(f"name{i}", text_color=hexc(C["ink"]))
        out += ["      - if:", "          condition:", f"            switch.is_on: relay{k['relay']}", "          then:"]
        out += ["      " + l for l in up(f"bar{i}", bg_color=gd)]
        out += ["          else:"] + ["      " + l for l in up(f"bar{i}", bg_color=hexc(C["track"]))]
out += ["  - id: ui_refresh", "    then:"]
for T in RT:
    out += ["      - if:", "          condition:", f"            lambda: 'return id(theme_sel).current_option() == \"{T}\";'", "          then:", f"            - script.execute: ui_theme_{T}"]
for i, k in enumerate(SCR["keys"], 1):
    for st in ("on", "off"):
        out += [f"  - id: ui_key{i}_{st}", "    then:", "      - script.execute: ui_refresh"]
os.makedirs(f"{ROOT}/firmware/generated", exist_ok=True)
open(f"{ROOT}/firmware/generated/ui.yaml", "w").write("\n".join(out) + "\n")
print("ok", theme_name, VER)
