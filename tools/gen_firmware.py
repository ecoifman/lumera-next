#!/usr/bin/env python3
# מחולל קושחה: קורא design/themes.json + design/screens/keys.json + design/VERSION
# וכותב firmware/generated/ui.yaml (LVGL, גופנים, כיסויי תריסים, חיישני HA, סקריפטי ערכות נושא).
# שימוש: python3 tools/gen_firmware.py [--theme navy] [--font-local]
# סגנונות (style בכל ערכה): card (כרטיס מעוגל), ladder (סולם פסים), hud (מסגרות פינות).
import json, os, re, sys
import yaml

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
theme_name = sys.argv[sys.argv.index("--theme") + 1] if "--theme" in sys.argv else "navy"
ALL = json.load(open(f"{ROOT}/design/themes.json"))
SCR = json.load(open(f"{ROOT}/design/screens/keys.json"))
VER = open(f"{ROOT}/design/VERSION").read().strip()

RT = ["navy", "black", "white", "lunar", "hud", "ladder"]   # ערכות שנבחרות בזמן ריצה (צבעים אחידים, בלי גרדיאנט)
HEB = {"navy": "כחול", "black": "שחור", "white": "לבן", "lunar": "לונאר", "hud": "HUD", "ladder": "סולם"}
if theme_name not in RT:
    theme_name = "navy"


class Hex(int):
    pass


yaml.add_representer(Hex, lambda d, v: d.represent_scalar("tag:yaml.org,2002:int", f"0x{int(v):06X}"))


class Lam(str):
    pass


yaml.add_representer(Lam, lambda d, v: d.represent_scalar("!lambda", str(v), style="|"))


def hx(c):
    return Hex(int(c.lstrip("#"), 16))


def vis(t):
    """עברית בסדר ויזואלי: אין תמיכת bidi ב-LVGL. טקסט בלי עברית נשאר כמות שהוא."""
    return t[::-1] if re.search(r"[֐-׿]", t) else t


def vis2(name):
    """שם בשתי שורות לפי רווח; כל שורה הפוכה לחוד (סדר השורות נשמר)."""
    return "\n".join(vis(p) for p in name.split(" "))


def P(T):
    """פלטה מלאה של ערכה, עם ברירות מחדל לשדות שלא הוגדרו."""
    C = dict(ALL[T])
    C.setdefault("style", "card")
    C.setdefault("off_name", C["ink"])
    C.setdefault("off_border", C["hair"])
    return C


W, H = SCR["size"]
TILES = SCR["tiles"]
N = len(TILES)
MX, GAP, TOP = 14, 10, 56
CW = (W - 2 * MX - (N - 1) * GAP) // N       # 129
CH = 340
TABS = SCR["tabs"]
ACTIVE = SCR["active_tab"]
G0 = P(theme_name)

GL = "אבגדהוזחטיכלמנסעפצקרשתךםןףץ0123456789 .ONFHUD"
gfont = (lambda i, s: {"file": "fonts/Heebo.ttf", "id": i, "size": s, "bpp": 4, "glyphs": GL}) if "--font-local" in sys.argv \
    else (lambda i, s: {"file": "gfonts://Heebo@300", "id": i, "size": s, "bpp": 4, "glyphs": GL})


def tx(t):          # מיקום עמודה: אריח 0 הוא הימני ביותר (RTL)
    return MX + (N - 1 - t) * (CW + GAP)


def obj(i, x=None, y=None, w=None, h=None, **kw):
    o = {"id": i}
    if x is not None: o["x"] = x
    if y is not None: o["y"] = y
    if w is not None: o["width"] = w
    if h is not None: o["height"] = h
    base = {"radius": 0, "border_width": 0, "pad_all": 0, "bg_opa": "TRANSP"}
    base.update(kw)
    o.update(base)
    return {"obj": o}


def label(i, text, font=None, **kw):
    o = {"id": i, "text": text}
    if font: o["text_font"] = font
    o.update(kw)
    return {"label": o}


BR = {"tl": (["LEFT", "TOP"], "TOP_LEFT"), "tr": (["RIGHT", "TOP"], "TOP_RIGHT"),
      "bl": (["LEFT", "BOTTOM"], "BOTTOM_LEFT"), "br": (["RIGHT", "BOTTOM"], "BOTTOM_RIGHT")}


def brackets(pfx, color):
    return [obj(f"{pfx}_{c}", w=22, h=22, align=al, border_width=3, border_side=sd, border_color=hx(color), clickable=False)
            for c, (sd, al) in BR.items()]


widgets = [obj("bgroot", 0, 0, W, H, bg_opa="COVER", bg_color=hx(G0["ground"]), clickable=False)]
lights, shutters = [], []
for t, tl in enumerate(TILES):
    x = tx(t); k = t + 1
    if tl["type"] == "shutter":
        shutters.append((k, tl))
        zones = []
        for z, (zid, glyph, act) in enumerate([("u", "", "cover.open"), ("s", "", "cover.stop"), ("d", "", "cover.close")]):
            zones.append({"obj": {"id": f"z{k}{zid}", "x": 0, "y": z * 90, "width": CW, "height": 90, "radius": 0, "border_width": 0,
                                  "pad_all": 0, "bg_opa": "TRANSP", "on_press": [{"script.execute": f"ui_press_z{k}{zid}"}], "on_release": [{"script.execute": f"ui_tile{k}"}],
                                  "on_click": [{"script.execute": f"ui_tile{k}"}, {"homeassistant.action": {"action": f"cover.{act}", "data": {"entity_id": tl["entity"]}}}],
                                  "widgets": [label(f"g{k}{zid}", glyph, "montserrat_28", align="CENTER")]}})
        kids = zones + [obj(f"dv{k}_1", 14, 90, CW - 28, 1, bg_opa="COVER"), obj(f"dv{k}_2", 14, 180, CW - 28, 1, bg_opa="COVER"),
                        label(f"name{k}", vis2(tl["name"]), "f_tiny", align="BOTTOM_MID", y=-18, text_align="CENTER")] + brackets(f"sb{k}", G0["outline"])
        widgets.append({"obj": {"id": f"card{k}", "x": x, "y": TOP, "width": CW, "height": CH, "radius": 24, "border_width": 1,
                                "pad_all": 0, "bg_opa": "COVER", "widgets": kids}})
    else:
        lights.append((k, tl))
        kids = [label(f"name{k}", vis2(tl["name"]), "f_name", align="CENTER", y=-22, text_align="CENTER"),
                label(f"stat{k}", vis("כבוי"), "f_state", align="CENTER", y=38),
                obj(f"bar{k}", w=52, h=6, align="BOTTOM_MID", y=-22, radius=3, bg_opa="COVER")]
        kids += [obj(f"lb{k}_{b}", w=68, h=14, align="TOP_MID", y=22 + 22 * b, radius=7, bg_opa="COVER") for b in range(7)]
        kids += brackets(f"hb{k}", G0["outline"])
        kids += [label(f"hs{k}", "OFF", "f_state", align="TOP_MID", y=50)]
        widgets.append({"obj": {"id": f"card{k}", "x": x, "y": TOP, "width": CW, "height": CH, "radius": 24, "border_width": 1,
                                "pad_all": 0, "bg_opa": "COVER",
                                "on_press": [{"script.execute": f"ui_press_c{k}"}], "on_release": [{"script.execute": f"ui_tile{k}"}],
                                "on_click": [{"lambda": f"id(lon{k}) = !id(lon{k});"}, {"script.execute": f"ui_tile{k}"},
                                             {"homeassistant.action": {"action": "light.toggle", "data": {"entity_id": tl["entity"]}}}],
                                "widgets": kids}})

# כיתוב תחתון: קו, ארבע-חמש לשוניות, פס מסמן מתחת לפעילה
widgets.append(obj("tabline", MX, 408, W - 2 * MX, 1, bg_opa="COVER"))
for i, name in enumerate(TABS):
    cx = 100 + 165 * i
    widgets.append({"obj": {"id": f"tab{i}", "x": cx - 82, "y": 418, "width": 164, "height": 60, "radius": 0, "border_width": 0, "pad_all": 0,
                            "bg_opa": "TRANSP", "clickable": False,
                            "widgets": [label(f"tabl{i}", vis(name), "f_tab", align="CENTER")]}})
widgets.append(obj("tabind", 100 + 165 * TABS.index(ACTIVE) - 30, 406, 60, 4, radius=2, bg_opa="COVER"))

# רצועת משיכה בראש המסך + פאנל ערכות נושא
widgets.append({"obj": {"id": "handle", "x": 0, "y": 0, "width": W, "height": 40, "bg_opa": "TRANSP", "border_width": 0, "radius": 0, "pad_all": 0,
                        "on_click": [{"lvgl.widget.show": "panel"}],
                        "widgets": [obj("grip", w=80, h=5, align="CENTER", radius=3, bg_opa="COVER")]}})
pk = [label("panel_title", vis("ערכת נושא"), "f_name", align="TOP_MID", y=12)]
for j, T in enumerate(RT):
    row, colm = divmod(j, 3)
    pk.append({"obj": {"id": f"tbtn_{T}", "align": "TOP_MID", "x": (colm - 1) * 240, "y": 62 + row * 74, "width": 200, "height": 62, "radius": 12,
                       "border_width": 2, "bg_color": hx(ALL[T]["ground"]), "border_color": hx(ALL[T]["accent"]),
                       "on_click": [{"select.set": {"id": "theme_sel", "option": T}}],
                       "widgets": [label(f"tbl_{T}", vis(HEB[T]), "f_name", text_color=hx(ALL[T]["ink"]), align="CENTER")]}})
pk.append({"obj": {"id": "panel_close", "align": "BOTTOM_MID", "y": -10, "width": 160, "height": 46, "radius": 12, "border_width": 0,
                   "on_click": [{"lvgl.widget.hide": "panel"}],
                   "widgets": [label("panel_close_l", vis("סגור"), "f_state", align="CENTER")]}})
widgets.append({"obj": {"id": "panel", "hidden": True, "x": 0, "y": 0, "width": W, "height": 262, "radius": 0, "border_width": 0, "pad_all": 0,
                        "bg_color": hx(G0["surface"]), "widgets": pk}})


# ---- סקריפטים: צביעה לפי ערכה ----
def U(i, **kw):
    return {"lvgl.widget.update": {"id": i, **kw}}


def SHOW(i): return {"lvgl.widget.show": i}
def HIDE(i): return {"lvgl.widget.hide": i}


TA = {}


def theme_script(T):
    C = P(T); S = C["style"]; hud = S == "hud"; lad = S == "ladder"
    A = []
    A += [U("bgroot", bg_color=hx(C["ground"])), U("panel", bg_color=hx(C["surface"])), U("panel_title", text_color=hx(C["ink"])),
          U("panel_close", bg_color=hx(C["track"])), U("panel_close_l", text_color=hx(C["ink"])), U("grip", bg_color=hx(C["track"])),
          U("tabline", bg_color=hx(C["hair"])), U("tabind", bg_color=hx(C["accent"]))]
    for i, name in enumerate(TABS):
        A.append(U(f"tabl{i}", text_color=hx(C["accent"] if name == ACTIVE else C["muted"])))
    rad = 0 if hud else 24
    TA[T] = {}
    for k, tl in shutters:
        _s = len(A)
        A += [U(f"card{k}", bg_color=hx(C["ground"] if hud else C["surface"]), bg_opa="TRANSP" if hud else "COVER", radius=rad,
                border_width=0 if hud else 1, border_color=hx(C["hair"])),
              U(f"name{k}", text_color=hx(C["muted"])), U(f"dv{k}_1", bg_color=hx(C["hair"])), U(f"dv{k}_2", bg_color=hx(C["hair"]))]
        A += [U(f"g{k}{z}", text_color=hx(C["ink"])) for z in "usd"]
        A += [(HIDE if hud else SHOW)(f"dv{k}_{n}") for n in (1, 2)]
        A += [(SHOW if hud else HIDE)(f"sb{k}_{c}") for c in BR] + [U(f"sb{k}_{c}", border_color=hx(C["outline"])) for c in BR]
        TA[T][k] = A[_s:]
    for k, tl in lights:
        _s = len(A)
        A += [(HIDE if (hud or lad) else SHOW)(f"bar{k}")]
        A += [(SHOW if lad else HIDE)(f"lb{k}_{b}") for b in range(7)]
        A += [(SHOW if hud else HIDE)(f"hb{k}_{c}") for c in BR] + [(SHOW if hud else HIDE)(f"hs{k}")]
        A += [U(f"name{k}", y=0 if hud else (42 if lad else -22)), U(f"stat{k}", y=80 if hud else (120 if lad else 38))]
        on, off = [], []
        # דולק
        if hud:
            on += [U(f"card{k}", bg_color=hx(C["on_fill"]), bg_opa="COVER", radius=0, border_width=0)]
            on += [U(f"hb{k}_{c}", border_color=hx(C["on_border"])) for c in BR]
            on += [U(f"hs{k}", text_color=hx(C["accent"])), {"lvgl.label.update": {"id": f"hs{k}", "text": "ON"}}]
            off += [U(f"card{k}", bg_color=hx(C["ground"]), bg_opa="TRANSP", radius=0, border_width=0)]
            off += [U(f"hb{k}_{c}", border_color=hx(C["off_border"])) for c in BR]
            off += [U(f"hs{k}", text_color=hx(C["muted"])), {"lvgl.label.update": {"id": f"hs{k}", "text": "OFF"}}]
        else:
            if lad:
                on += [U(f"card{k}", bg_color=hx(C["surface"]), bg_opa="COVER", radius=24, border_width=1, border_color=hx(C["hair"]))]
                on += [U(f"lb{k}_{b}", bg_color=hx(C["accent"] if b >= 2 else C["track"])) for b in range(7)]
                off += [U(f"card{k}", bg_color=hx(C["surface"]), bg_opa="COVER", radius=24, border_width=1, border_color=hx(C["hair"]))]
                off += [U(f"lb{k}_{b}", bg_color=hx(C["track"])) for b in range(7)]
            else:
                on += [U(f"card{k}", bg_color=hx(C["on_fill"]), bg_opa="COVER", radius=24, border_width=2, border_color=hx(C["on_border"])),
                       U(f"bar{k}", bg_color=hx(C["on_bar"]))]
                off += [U(f"card{k}", bg_color=hx(C["surface"]), bg_opa="COVER", radius=24, border_width=1, border_color=hx(C["hair"])),
                        U(f"bar{k}", bg_color=hx(C["track"]))]
        on += [U(f"name{k}", text_color=hx(C["on_name"])), U(f"stat{k}", text_color=hx(C["on_sub"])),
               {"lvgl.label.update": {"id": f"stat{k}", "text": vis("דולק")}}]
        off += [U(f"name{k}", text_color=hx(C["off_name"] if hud else C["ink"])), U(f"stat{k}", text_color=hx(C["muted"])),
                {"lvgl.label.update": {"id": f"stat{k}", "text": vis("כבוי")}}]
        A.append({"if": {"condition": {"lambda": f"return id(lon{k});"}, "then": on, "else": off}})
        TA[T][k] = A[_s:]
    return {"id": f"ui_theme_{T}", "then": A}


scripts = [theme_script(T) for T in RT]
scripts.append({"id": "ui_refresh", "then": [
    {"if": {"condition": {"lambda": f'return id(theme_sel).current_option() == "{T}";'}, "then": [{"script.execute": f"ui_theme_{T}"}]}} for T in RT]})

for k, tl in lights + shutters:   # רענון של אריח בודד (לחיצה / שינוי מצב מ-HA), בלי לצייר מחדש את כל המסך
    scripts.append({"id": f"ui_tile{k}", "then": [
        {"if": {"condition": {"lambda": f'return id(theme_sel).current_option() == "{T}";'}, "then": TA[T][k]}} for T in RT]})


def press_script(sid, fn):
    return {"id": sid, "then": [{"if": {"condition": {"lambda": f'return id(theme_sel).current_option() == "{T}";'}, "then": fn(P(T))}} for T in RT]}


for k, tl in lights:
    scripts.append(press_script(f"ui_press_c{k}", lambda C, k=k: [U(f"card{k}", border_width=4, border_color=hx(C["accent"]), bg_opa="COVER")]))
for k, tl in shutters:
    for zid in "usd":
        g = {"u": "u", "s": "s", "d": "d"}[zid]
        scripts.append(press_script(f"ui_press_z{k}{zid}", lambda C, k=k, g=g: [U(f"g{k}{g}", text_color=hx(C["accent"]))]))

doc = {
    "font": [gfont("f_name", 22), gfont("f_state", 18), gfont("f_tab", 20), gfont("f_tiny", 16)],
    "esphome": {"on_boot": {"priority": -100, "then": [{"script.execute": "ui_refresh"}]}},
    "select": [{"platform": "template", "id": "theme_sel", "name": "ערכת נושא", "options": RT, "initial_option": theme_name,
                "optimistic": True, "restore_value": True, "on_value": [{"script.execute": "ui_refresh"}]}],
    "globals": [{"id": f"lon{k}", "type": "bool", "initial_value": "false"} for k, tl in lights],
    "binary_sensor": [{"platform": "homeassistant", "id": f"lstate{k}", "entity_id": tl["entity"], "internal": True,
                       "on_state": [{"lambda": f"id(lon{k}) = x;"}, {"script.execute": f"ui_tile{k}"}]} for k, tl in lights],
    "lvgl": {"displays": ["lcd"], "touchscreens": ["touch"], "rotation": 90, "buffer_size": "50%",
             "bg_color": hx(G0["ground"]), "text_font": "f_name", "text_color": hx(G0["ink"]),
             "pages": [{"id": "keys", "widgets": widgets}]},
    "script": scripts,
}
os.makedirs(f"{ROOT}/firmware/generated", exist_ok=True)
head = f"# נוצר אוטומטית ע\"י tools/gen_firmware.py (ערכה התחלתית: {theme_name}, גרסה {VER}). לא לערוך ידנית.\n"
open(f"{ROOT}/firmware/generated/ui.yaml", "w").write(head + yaml.dump(doc, allow_unicode=True, sort_keys=False, width=1000))
print("ok", theme_name, VER)
