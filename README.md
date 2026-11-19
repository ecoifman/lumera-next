# Lumera Next

תוכנה חדשה למתגי Lumera L10: פשוטה, מקומית קודם. מאגר נפרד.

- `docs/spec.md`: אפיון
- `mockups/`: מוקאפים של מסכים (Design canvas), ערכת Lumera Panel
- `tools/gen_mockups.py`: מחולל לוחות המוקאפ מהטוקנים של Lumera Panel
- `firmware/`: אב-טיפוס ESPHome (עדיין ריק)

## כללים
- לא נוגעים בקוד של גיא (lumera-hs/home-eyal). קוראים ממנו בלבד, ומעתיקים רק דרייברים ומנגנוני שליחה, עם הערת מקור.
- סודות (Wi-Fi, מפתחות API/OTA) ב-`firmware/secrets.yaml`, לא בגיט.
- צריבה: מסך אחד בשולחן, רק אחרי אישור עיצוב, עם גיבוי bin קודם.
