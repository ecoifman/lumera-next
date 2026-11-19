#!/usr/bin/env bash
# בונה הכל מ-design/: מוקאפים + קושחה, ואז בודק ש-ESPHome מקבל את התצורה.
set -e
cd "$(dirname "$0")/.."
THEME="${1:-navygrad}"
python3 tools/gen_mockups.py mockups --themes
python3 tools/gen_firmware.py --theme "$THEME"
python3 tools/gen_firmware.py --theme "$THEME" --font-local; cd firmware && ${ESPHOME:-esphome} config lumera-local.yaml >/dev/null && echo "esphome config: OK"; cd ..; python3 tools/gen_firmware.py --theme "$THEME"
