# Changelog

## 2026-02-13
- Move scoreboard to dedicated right panel outside court area (canvas widened from 800 to 1060)
- Restructure scoreboard columns to match Wimbledon layout: Previous Sets | Name | Sets | Games | Points
- Add dark background panel and separator line for right sidebar
- Limit overlay backdrops (question, title, point, game over) to court area so scoreboard stays visible
- Add COURT_AREA_WIDTH (800) and COURT_CENTER_X constants for court-vs-panel separation
- Update smoke test for new CANVAS_WIDTH of 1060
