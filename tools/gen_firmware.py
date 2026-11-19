#!/usr/bin/env python3
# מחולל קושחה: קורא design/themes.json + design/screens/*.json + design/VERSION
# וכותב firmware/generated/ui.yaml (LVGL + גופן + סקריפטים שמחברים מצב ממסר למסך).
# שימוש: python3 tools/gen_firmware.py [--theme navygrad]
import json, os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
theme_name = sys.argv[sys.argv.index("--theme") + 1] if "--theme" in sys.argv else "navygrad"
TH = json.load(open(f"{ROOT}/design/themes.json"))[theme_name]
SCR = json.load(open(f"{ROOT}/design/screens/keys.json"))
VER = open(f"{ROOT}/design/VERSION").read().strip()

def hexc(c): return "0x" + c.lstrip("#").upper()
def colors(v):   # "#RRGGBB" או גרדיאנט CSS -> רשימת צבעים
    return re.findall(r"#[0-9A-Fa-f]{6}", v)
def vis(t): return t[::-1]   # עברית בסדר ויזואלי: אין תמיכת bidi ב-LVGL (כמו בקושחה של גיא)

W, H = SCR["size"]
n = len(SCR["keys"])
col_w = W // n
bg = colors(TH.get("bg", TH["ground"]))
gold = colors(TH["gold"])
out = [f"# נוצר אוטומטית ע\"י tools/gen_firmware.py (ערכה: {theme_name}, גרסה {VER}). לא לערוך ידנית.",
       "font:",
       '  - file: "fonts/Heebo.ttf"', "    id: f_name", "    size: 32",
       '    glyphs: "אבגדהוזחטיכלמנסעפצקרשתךםןףץ0123456789 ."',
       "lvgl:", "  displays: [lcd]", "  touchscreens: [touch]", "  rotation: 90",
       f"  bg_color: {hexc(bg[0])}"]
if len(bg) > 1:
    out += [f"  bg_grad_color: {hexc(bg[-1])}", "  bg_grad_dir: VER"]
out += ["  text_font: f_name", f"  text_color: {hexc(TH['ink'])}", "  pages:", "    - id: keys", "      widgets:"]
for i, k in enumerate(SCR["keys"], 1):
    out += [
     "        - obj:", f"            id: key{i}", f"            x: {(i-1)*col_w}", "            y: 0",
     f"            width: {col_w}", f"            height: {H-72}", "            bg_opa: TRANSP", "            border_width: 0",
     "            radius: 0", "            pad_all: 0", "            widgets:",
     "              - label:", f'                  text: "{vis(k["name"])}"', "                  align: CENTER", "                  y: -12",
     "              - obj:", f"                  id: bar{i}", "                  align: CENTER", "                  y: 36",
     "                  width: 140", "                  height: 6", "                  radius: 3", "                  border_width: 0",
     f"                  bg_color: {hexc(TH['track'])}",
     f"            on_click:", f"              - switch.toggle: relay{k['relay']}"]
out += ["script:"]
for i, k in enumerate(SCR["keys"], 1):
    for st, c in (("on", gold[len(gold)//2]), ("off", TH["track"])):
        out += [f"  - id: ui_key{i}_{st}", "    then:", "      - lvgl.widget.update:", f"          id: bar{i}", f"          bg_color: {hexc(c)}"]
os.makedirs(f"{ROOT}/firmware/generated", exist_ok=True)
open(f"{ROOT}/firmware/generated/ui.yaml", "w").write("\n".join(out) + "\n")
print("ok", theme_name, VER)
