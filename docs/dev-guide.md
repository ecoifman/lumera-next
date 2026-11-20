# מדריך עבודה: עיצוב נפרד מתוכנה

## מבנה
- `design/themes.json` – ערכות צבע וסגנון. ערכות זמן ריצה: navy, black, white, lunar, hud, ladder. שדה `style`: card (כרטיס), ladder (סולם פסים), hud (מסגרות פינות). מקור יחיד.
- `design/screens/keys.json` – 6 אריחים (`tiles`): 2 תריסים (`cover.*`) + 4 תאורות (`light.*`) כישויות HA, וטאבים תחתונים. כרגע `CHANGE_ME` – להחליף ל-entity_id אמיתיים ואז לצרוב.
- `design/VERSION` – גרסת העיצוב.
- `tools/gen_mockups.py` – מחולל תצוגות העיצוב (קנבס).
- `tools/gen_firmware.py` – מחולל `firmware/generated/ui.yaml` (LVGL, עברית הפוכה, צבעים, גרדיאנט).
- `firmware/lumera-bench.yaml` – לוגיקה כתובה ביד (חומרה, ממסרים, Zigbee). כוללת את הקובץ המחולל.
- `tools/build.sh [ערכה]` – מריץ הכל ובודק `esphome config`.

## זרימת שינוי
1. משנים צבע/שם/מסך בקבצי `design/` (לא ב-`generated/`).
2. `tools/build.sh navy`
3. מעתיקים את `firmware/` ל-ESPHome Builder, Compile בלבד, ואז OTA למסך 15.
4. בדיקה חיה + צילום מסך, ואז commit ותגית גרסה.

## לא מאומת עדיין על חומרה
- סיבוב landscape (`rotation: 90`) והתאמת מגע (`swap_xy`), כרגע `swap_xy: false`.
- גרדיאנט על הפאנל (banding).
- קומפילציה: אפשרית רק ב-Builder של HA (הסנדבוקס חסום מ-dl.espressif.com).

## מה עובד עכשיו
- לחיצה על תאורה: היפוך מקומי מיידי + `light.toggle` ל-HA; מצב מ-HA מסנכרן חזרה. תריס: `cover.open_cover/stop_cover/close_cover`.
- נדרש ב-HA: אינטגרציית ESPHome ← אפשור 'לבצע פעולות ב-Home Assistant'.
- זמני נסיעת תריס נקבעים ב-HA, לא במסך.
- ידוע: ריצוד קל, אזהרות lvgl (150–175ms) בהחלפת ערכה; HUD וסולם כבדים יותר מהאחרות.
