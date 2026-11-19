# מדריך עבודה: עיצוב נפרד מתוכנה

## מבנה
- `design/themes.json` – ערכות צבע (black, white, navy, navygrad, blackgrad, whitegrad). מקור יחיד.
- `design/screens/*.json` – תוכן המסכים (שמות מפתחות, ממסרים, טאבים).
- `design/VERSION` – גרסת העיצוב.
- `tools/gen_mockups.py` – מחולל תצוגות העיצוב (קנבס).
- `tools/gen_firmware.py` – מחולל `firmware/generated/ui.yaml` (LVGL, עברית הפוכה, צבעים, גרדיאנט).
- `firmware/lumera-bench.yaml` – לוגיקה כתובה ביד (חומרה, ממסרים, Zigbee). כוללת את הקובץ המחולל.
- `tools/build.sh [ערכה]` – מריץ הכל ובודק `esphome config`.

## זרימת שינוי
1. משנים צבע/שם/מסך בקבצי `design/` (לא ב-`generated/`).
2. `tools/build.sh navygrad`
3. מעתיקים את `firmware/` ל-ESPHome Builder, Compile בלבד, ואז OTA למסך 15.
4. בדיקה חיה + צילום מסך, ואז commit ותגית גרסה.

## לא מאומת עדיין על חומרה
- סיבוב landscape (`rotation: 90`) והתאמת מגע (`swap_xy`), כרגע `swap_xy: false`.
- גרדיאנט על הפאנל (banding).
- קומפילציה: אפשרית רק ב-Builder של HA (הסנדבוקס חסום מ-dl.espressif.com).
