# Generates the Lumera Panel mockup artboards (854x480) from the package tokens.
# Usage: python3 gen_mockups.py <out_dir>
import sys, json
OUT = sys.argv[1] if len(sys.argv) > 1 else "."
TH = {
 "black": dict(ground="#000000", surface="#202020", hair="#303030", outline="#585858", track="#303030", ink="#FFFFFF", muted="#A0A0A0", gold="#C8A060", goldtext="#C8A060", fill="#FFFFFF", onfill="#000000", cool="#88B0D0"),
 "navy": dict(ground="#0B1220", surface="#131D33", hair="#243352", outline="#5A6E94", track="#243352", ink="#F2F5FA", muted="#9AA8C2", gold="linear-gradient(90deg,#7F8FAE,#E1E8F4 50%,#7F8FAE)", goldtext="#B9C6DC", fill="#E8EDF5", onfill="#0B1220", cool="#8FB4E0"),
 "white": dict(ground="#FFFFFF", surface="#F0F0F0", hair="#D8D8D8", outline="#A0A0A0", track="#E8E8E8", ink="#101010", muted="#686868", gold="#B88830", goldtext="#806018", fill="#101010", onfill="#FFFFFF", cool="#205888"),
}
TABS = ["בית", "מתג", "מזגן", "מוזיקה", "עוזר"]
ICON = {"up": "M6 15l6-6 6 6", "down": "M6 9l6 6 6-6", "stop": "M8 8h8v8H8z", "minus": "M6 12h12", "plus": "M12 6v12M6 12h12",
        "prev": "M7 6v12M18 6l-8 6 8 6z", "next": "M17 6v12M6 6l8 6-8 6z", "play": "M9 6l9 6-9 6z"}

def svg(name, size, c):
    return f'<svg viewBox="0 0 24 24" width="{size}" height="{size}"><path d="{ICON[name]}" fill="none" stroke="{c}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'

def page(title, room, body, theme="black", active=None, bottom=None):
    t = TH[theme]
    tabs = ""
    for x in TABS:
        if x == active:
            tabs += f'<span style="position:relative;color:{t["ink"]}">{x}<i style="position:absolute;left:50%;bottom:-14px;width:6px;height:6px;margin-left:-3px;border-radius:50%;background:{t["gold"]}"></i></span>'
        else:
            tabs += f'<span>{x}</span>'
    foot = bottom if bottom is not None else f'<div style="height:72px;display:flex;justify-content:center;align-items:center;gap:48px;font-size:24px;line-height:30px;color:{t["muted"]}">{tabs}</div>'
    return f'''<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500&display=swap" rel="stylesheet">
<style>
html,body{{margin:0;overflow:hidden}}
</style>
</helmet>
<div style="width:854px;height:480px;box-sizing:border-box;background:{t["ground"]};color:{t["ink"]};font-family:'Heebo',system-ui,sans-serif;display:flex;flex-direction:column;padding:32px 48px 0">
<div style="display:flex;justify-content:space-between;font-size:22px;line-height:28px;font-weight:500"><span style="color:{t["muted"]}">{room}</span><span style="direction:ltr;letter-spacing:.3em;color:{t["goldtext"]}">LUMERA</span></div>
<div style="flex:1;display:flex;align-items:stretch;padding:24px 0">
{body}
</div>
{foot}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":854,"height":480}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''

def nm(t, th, on=True): return f'<span style="font-size:32px;line-height:40px;font-weight:500;color:{th["ink"] if on else th["muted"]}">{t}</span>'
def cap(t, th, c=None): return f'<span style="font-size:24px;line-height:30px;color:{c or th["muted"]}">{t}</span>'
def bar(th, on): return f'<i style="display:block;height:6px;border-radius:3px;background:{th["gold"] if on else th["track"]}"></i>'
def column(inner, th, first, bg=""):
    b = "" if first else f";border-inline-start:1px solid {th['hair']}"
    return f'<div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:stretch;text-align:center;gap:16px;padding:0 24px{b}{bg}">{inner}</div>\n'
def light(name, th, first, on, room=None):
    return column(nm(name, th, on) + (cap(room, th) if room else "") + bar(th, on), th, first)
def pill(text, th, active=False, w=None):
    st = f'background:{th["fill"]};border:1px solid {th["fill"]};color:{th["onfill"]}' if active else f'border:1px solid {th["outline"]};color:{th["ink"]}'
    return f'<span style="display:inline-flex;align-items:center;justify-content:center;height:72px;padding:0 40px;border-radius:36px;box-sizing:border-box;font-size:28px;line-height:36px;{st}">{text}</span>'
def round_btn(icon, th):
    return f'<span style="display:inline-flex;align-items:center;justify-content:center;width:80px;height:80px;border-radius:40px;border:1px solid {th["outline"]};box-sizing:border-box">{svg(icon, 36, th["ink"])}</span>'
def shutter(name, pct, th, first):
    state = "סגור" if pct == 0 else f"פתוח {pct}%"
    up = f'<div style="flex:1;display:flex;align-items:center;justify-content:center;border-bottom:1px solid {th["hair"]}">{svg("up", 48, th["ink"])}</div>'
    mid = f'<div style="display:flex;flex-direction:column;gap:8px;padding:16px 0;text-align:center">{nm(name, th)}{cap(state, th)}<i style="display:block;height:6px;border-radius:3px;background:{th["track"]};margin-top:8px"><b style="display:block;width:{pct}%;height:6px;border-radius:3px;background:{th["ink"]}"></b></i></div>'
    dn = f'<div style="flex:1;display:flex;align-items:center;justify-content:center;border-top:1px solid {th["hair"]}">{svg("down", 48, th["ink"])}</div>'
    b = "" if first else f";border-inline-start:1px solid {th['hair']}"
    return f'<div style="flex:1;display:flex;flex-direction:column;padding:0 24px{b}">{up}{mid}{dn}</div>\n'

def build(T=None):
    boards = {}
    only = T is not None
    T = T or 'black'
    kitchen = lambda th: light("תאורת מטבח", th, True, False) + light("ספוטים", th, False, False) + light("פינת אוכל", th, False, True) + light("מרפסת ראשי", th, False, False)
    for fn, theme in ((("Keys", T),) if only else (("Main", "black"), ("Kitchen-White", "white"))):
        th = TH[theme]
        boards[fn] = page("מסך 7 במטבח", "מטבח", kitchen(th), theme, "מתג")
    th = TH[T]
    # dimmer (package DimmerScreen layout, centred)
    dim = f'''<div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:16px;text-align:center">
{nm("פינת אוכל", th)}{cap("גוררים את הפס", th)}
<div style="font-size:96px;line-height:96px;font-weight:300;direction:ltr">60<span style="font-size:24px;color:{th["muted"]}">%</span></div>
<div dir="ltr" style="width:100%;height:40px;border-radius:3px;background:{th["track"]};overflow:hidden"><div style="width:60%;height:100%;background:{th["gold"]}"></div></div>
<div style="display:flex;gap:24px;margin-top:8px">{pill("כיבוי", th)}{pill("סיום", th, True)}</div>
</div>'''
    boards["Dim-Black"] = page("עמעם", "מטבח", dim, T, bottom='<div style="height:24px"></div>')
    # colour / CCT page
    def handle(pos): return f'<b style="position:absolute;top:-12px;left:{pos}%;width:6px;height:48px;margin-left:-3px;background:{th["ink"]};border-radius:3px"></b>'
    def gbar(lbl, lo, hi, grad, pos):
        return (f'<div style="display:flex;flex-direction:column;gap:8px;width:100%"><div dir="ltr" style="display:flex;justify-content:space-between">{cap(lo, th)}{cap(lbl, th, th["ink"])}{cap(hi, th)}</div>'
                f'<div dir="ltr" style="position:relative;height:24px;border-radius:3px;background:{grad}">{handle(pos)}</div></div>')
    cct = "linear-gradient(90deg,#FF8A2B 0%,#FFC98B 35%,#FFFFFF 65%,#BFD7FF 100%)"
    hue = "linear-gradient(90deg,#FF3B30,#FFCC00,#34C759,#32ADE6,#5856D6,#FF2D92,#FF3B30)"
    colour = f'''<div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:24px;text-align:center">
{nm("פינת אוכל", th)}
{gbar("3000K", "חם", "קר", cct, 25)}
{gbar("צבע", "", "", hue, 62)}
<div dir="ltr" style="width:100%;height:24px;border-radius:3px;background:{th["track"]};overflow:hidden"><div style="width:60%;height:100%;background:{th["gold"]}"></div></div>
</div>'''
    boards["Color-Page"] = page("עמעם וצבע", "מטבח", colour, T, bottom=f'<div style="height:72px;display:flex;justify-content:center;align-items:center;margin-bottom:24px">{pill("סיום", th, True)}</div>')
    # shutter + 2 lights, 2 shutters
    boards["Shutter-2Lights"] = page("תריס ושתי תאורות", "סלון", shutter("תריס סלון", 40, th, True) + light("תאורת סלון", th, False, True) + light("ספוטים", th, False, False), T, "מתג")
    boards["Shutters-2"] = page("שני תריסים", "מטבח", shutter("תריס ימין", 0, th, True) + shutter("תריס אמצעי", 65, th, False), T, "מתג")
    # key types
    scen = column(f'<span style="display:inline-flex;align-self:center;align-items:center;justify-content:center;height:72px;padding:0 24px;border-radius:36px;border:1px solid {th["outline"]};box-sizing:border-box;white-space:nowrap;font-size:28px;color:{th["ink"]}">לילה טוב</span>' + cap("תרחיש", th), th, False)
    boards["Key-Types"] = page("סוגי מקשים", "מטבח", light("תאורת מטבח", th, True, True) + light("תאורת סלון", th, False, False, "סלון") + scen + light("מרפסת", th, False, False), T, "מתג")
    # home
    rows = "".join(f'<div style="border-top:1px solid {th["hair"]};padding:16px 0;font-size:28px;line-height:36px;text-align:center;{"border-bottom:1px solid "+th["hair"] if i==2 else ""}">{x}</div>' for i, x in enumerate(["לילה טוב", "יציאה מהבית", "חזרתי הביתה"]))
    home = f'''<div style="flex:1;display:flex;align-items:center;justify-content:space-between">
<div><div style="font-size:168px;line-height:168px;font-weight:300;direction:ltr">21:02</div>{cap("יום חמישי · 19.11.2026", th)}</div>
<div style="width:222px">{rows}</div></div>'''
    boards["Home"] = page("מסך בית", "בית", home, T, "בית")
    # assistant
    eq = "".join(f'<i style="display:block;width:8px;height:{h}px;border-radius:3px;background:{th["ink"]}"></i>' for h in (24, 48, 80, 48, 24))
    asst = f'<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:16px;text-align:center"><div style="display:flex;align-items:center;gap:8px;height:80px">{eq}</div>{nm("מקשיב", th)}{cap("אמור מה לעשות", th)}</div>'
    boards["Assistant"] = page("מצב עוזר", "עוזר", asst, T, "עוזר")
    # AC (package ControlsScreen)
    ac = f'''<div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:16px;text-align:center">
<div>{nm("מזגן סלון", th)}<div>{cap("פועל · ", th)}<span style="font-size:24px;color:{th["cool"]}">קירור</span></div></div>
<div dir="ltr" style="display:flex;align-items:center;gap:32px">{round_btn("minus", th)}<span style="font-size:96px;line-height:96px;font-weight:300">24°</span>{round_btn("plus", th)}</div>
<div style="display:flex;gap:24px">{pill("כיבוי", th)}{pill("מצב", th)}</div></div>'''
    boards["AC"] = page("מזגן", "סלון", ac, T, "מזגן")
    # music
    music = f'''<div style="flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;gap:16px;text-align:center">
<div>{nm("שם השיר", th)}<div>{cap("אמן", th)}</div></div>
<div dir="ltr" style="display:flex;gap:24px">{round_btn("prev", th)}{round_btn("play", th)}{round_btn("next", th)}</div>
<div style="width:100%;display:flex;flex-direction:column;gap:8px">{cap("עוצמה 40%", th)}<i dir="ltr" style="display:block;height:6px;border-radius:3px;background:{th["track"]}"><b style="display:block;width:40%;height:6px;border-radius:3px;background:{th["ink"]}"></b></i></div></div>'''
    boards["Music"] = page("מוזיקה", "סלון", music, T, "מוזיקה")
    return boards

if __name__ == "__main__":
    for name, html in build().items():
        open(f"{OUT}/{name}.dc.html", "w").write(html)
    if "--themes" in sys.argv:
        for T in ("black", "white", "navy"):
            for name, html in build(T).items():
                open(f"{OUT}/T-{T}-{name}.dc.html", "w").write(html)
    print("ok")
