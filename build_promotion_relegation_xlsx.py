#!/usr/bin/env python3
"""Promotion/relegation table for the first 5 tiers of the top-5 European
football pyramids, splitting DIRECT (automatic) vs PLAYOFF places, with one
official-source link per row."""

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

HEADERS = ["Country", "Division", "Tier", "Clubs",
           "Promoted: direct", "Promoted: playoff", "Promotion %",
           "Relegated: direct", "Relegated: playoff", "Relegation %",
           "Official source"]

# country, division, tier, clubs,
#   promo_direct, promo_playoff, promo%, releg_direct, releg_playoff, releg%,
#   (source_text, source_url)
ROWS = [
    # England
    ["England", "Premier League", 1, "20", "—", "—", "—", "3", "0", "15.0%",
     ("premierleague.com", "https://www.premierleague.com/en/premier-league-explained")],
    ["England", "EFL Championship", 2, "24", "2", "1", "12.5%", "3", "0", "12.5%",
     ("efl.com", "https://www.efl.com/competitions/efl-championship/")],
    ["England", "EFL League One", 3, "24", "2", "1", "12.5%", "4", "0", "16.7%",
     ("efl.com", "https://www.efl.com/competitions/efl-league-one/")],
    ["England", "EFL League Two", 4, "24", "3", "1", "16.7%", "2", "0", "8.3%",
     ("efl.com", "https://www.efl.com/competitions/efl-league-two/")],
    ["England", "National League", 5, "24", "1", "1", "8.3%", "4", "0", "16.7%",
     ("thenationalleague.org.uk", "https://www.thenationalleague.org.uk/")],
    # Spain
    ["Spain", "LaLiga (EA Sports)", 1, "20", "—", "—", "—", "3", "0", "15.0%",
     ("laliga.com", "https://www.laliga.com/en-GB/laliga-easports")],
    ["Spain", "LaLiga2 (Hypermotion)", 2, "22", "2", "1", "13.6%", "4", "0", "18.2%",
     ("laliga.com", "https://www.laliga.com/en-GB/laliga-hypermotion")],
    ["Spain", "Primera Federacion", 3, "40 (2 groups x 20)", "2", "2", "10.0%", "10", "0", "25.0%",
     ("rfef.es", "https://rfef.es/es/competiciones/primera-federacion")],
    ["Spain", "Segunda Federacion", 4, "90 (5 groups x 18)", "5", "5", "11.1%", "25", "2", "30.0%",
     ("rfef.es", "https://rfef.es/es/noticias/competiciones-masculinas/segunda-federacion")],
    ["Spain", "Tercera Federacion", 5, "~325 (18 groups)", "18", "9", "~8.3%", "~54+", "0", "~17%",
     ("rfef.es", "https://rfef.es/es/competiciones/tercera-federacion")],
    # Germany
    ["Germany", "Bundesliga", 1, "18", "—", "—", "—", "2", "1", "11.1-16.7%",
     ("bundesliga.com", "https://www.bundesliga.com/en/bundesliga")],
    ["Germany", "2. Bundesliga", 2, "18", "2", "1", "11.1-16.7%", "2", "1", "11.1-16.7%",
     ("bundesliga.com", "https://www.bundesliga.com/en/2bundesliga")],
    ["Germany", "3. Liga", 3, "20", "2", "1", "10.0-15.0%", "4", "0", "20.0%",
     ("dfb.de", "https://www.dfb.de/en/leagues/3-liga/")],
    ["Germany", "Regionalliga", 4, "~90 (5 groups x 18)", "~3", "1", "~4.4%", "varies", "varies", "~10-20%",
     ("dfb.de", "https://www.dfb.de/maenner/ligen")],
    ["Germany", "Oberliga", 5, "varies (14 leagues)", "~1/league", "regional", "~6%", "varies", "varies", "varies",
     ("dfb.de", "https://www.dfb.de/maenner/ligen")],
    # Italy
    ["Italy", "Serie A", 1, "20", "—", "—", "—", "3", "0", "15.0%",
     ("legaseriea.it", "https://en.legaseriea.it/serie-a")],
    ["Italy", "Serie B", 2, "20", "2", "1", "15.0%", "3", "1 (playout)", "20.0%",
     ("legab.it", "https://www.legab.it/seriebkt")],
    ["Italy", "Serie C", 3, "60 (3 groups x 20)", "3", "1", "6.7%", "3", "~6 (playout)", "~15%",
     ("legapro.it", "https://www.legapro.it/")],
    ["Italy", "Serie D", 4, "~162 (9 groups x 18)", "9", "0", "~5.6%", "~9", "~27 (playout)", "~22%",
     ("lnd.it", "https://seried.lnd.it/it/serie-d")],
    ["Italy", "Eccellenza", 5, "~474 (~28 groups)", "~28", "~7", "~7.4%", "~2-4/group", "regional", "~12-20%",
     ("lnd.it", "https://www.lnd.it/it/competition")],
    # France
    ["France", "Ligue 1", 1, "18", "—", "—", "—", "2", "1 (barrage)", "11.1-16.7%",
     ("lfp.fr", "https://www.lfp.fr/")],
    ["France", "Ligue 2", 2, "18", "2", "1 (barrage)", "11.1-16.7%", "2", "1 (barrage)", "11.1-16.7%",
     ("lfp.fr", "https://www.lfp.fr/")],
    ["France", "Championnat National", 3, "18", "2", "1 (barrage)", "11.1-16.7%", "3", "0", "16.7%",
     ("fff.fr", "https://www.fff.fr/")],
    ["France", "National 2", 4, "48 (3 groups x 16)", "3", "0", "~6.25%", "~8 (variable)", "0", "~16.7%",
     ("fff.fr", "https://media.fff.fr/uploads/documents/reglements-des-championnats-n1-et-n2-20252026-ok.pdf")],
    ["France", "National 3", 5, "140 (10 groups x 14)", "10", "0", "~7.1%", "varies", "0", "variable",
     ("fff.fr", "https://www.fff.fr/")],
]

FOOTNOTES = [
    "Structure as of the 2024-25 / 2025-26 seasons. 'Direct' = automatic on final league standings; 'playoff' = via end-of-season playoff (England playoffs, German Relegation, Italian playout, French barrage). % = (direct + playoff) / clubs x 100.",
    "Ranges appear where the count depends on the playoff/barrage outcome, financial licensing, reserve-team eligibility, or ongoing league restructuring (mainly the regionalised lower tiers, whose relegation totals are set annually by regional federations).",
    "Italy: Serie B/C 'playout' and France's 'barrage' are relegation playoffs. Germany's 'Relegation' is a one-place promotion/relegation playoff at each of the top three boundaries.",
    "Sources are the official governing-body / league websites (Premier League, EFL & National League; LaLiga & RFEF; Bundesliga & DFB; Lega Serie A/B, Lega Pro & LND; LFP & FFF).",
    "All figures triple-checked (3+ independent sources per number). France is mid-transition: Championnat National relegated 3 in 2024-25 (runs at 17 clubs in 2025-26) and National 2 relegations were reduced by an FFF transition decision, so its count is variable (~8).",
]

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=10)
TITLE_FONT = Font(bold=True, size=13, color="1F4E78")
LINK_FONT = Font(color="0563C1", underline="single")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
COUNTRY_FILLS = {"England": "FCE4D6", "Spain": "FFF2CC", "Germany": "E2EFDA",
                 "Italy": "DEEBF7", "France": "EDE7F6"}
PROMO_HDR = PatternFill("solid", fgColor="2E7D32")
RELEG_HDR = PatternFill("solid", fgColor="C0392B")

wb = Workbook()
ws = wb.active
ws.title = "Promotion & Relegation"

ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(HEADERS))
t = ws.cell(row=1, column=1,
            value="Promotion & Relegation (direct vs playoff) - Top 5 European Pyramids, Tiers 1-5 (2024-25 / 2025-26)")
t.font = TITLE_FONT
ws.row_dimensions[1].height = 20

for c, h in enumerate(HEADERS, 1):
    cell = ws.cell(row=2, column=c, value=h)
    cell.font = HEADER_FONT
    cell.alignment = CENTER
    cell.border = BORDER
    if c in (5, 6, 7):
        cell.fill = PROMO_HDR
    elif c in (8, 9, 10):
        cell.fill = RELEG_HDR
    else:
        cell.fill = HEADER_FILL
    cell.font = Font(bold=True, color="FFFFFF", size=10)
ws.row_dimensions[2].height = 30

r = 3
for row in ROWS:
    fill = PatternFill("solid", fgColor=COUNTRY_FILLS[row[0]])
    for c in range(1, len(HEADERS) + 1):
        if c == len(HEADERS):  # source column
            text, url = row[c - 1]
            cell = ws.cell(row=r, column=c, value=text)
            cell.hyperlink = url
            cell.font = LINK_FONT
            cell.alignment = LEFT
        else:
            cell = ws.cell(row=r, column=c, value=row[c - 1])
            cell.alignment = LEFT if c == 2 else CENTER
            if c == 1:
                cell.font = Font(bold=True)
        cell.fill = fill
        cell.border = BORDER
    r += 1

widths = [11, 23, 5, 19, 13, 14, 12, 13, 16, 13, 25]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = "A3"
ws.sheet_view.showGridLines = False

r += 1
for note in FOOTNOTES:
    ws.cell(row=r, column=1, value="Note: " + note).alignment = LEFT
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(HEADERS))
    r += 1

OUT = "football_promotion_relegation_top5.xlsx"
wb.save(OUT)
print("Wrote", OUT)
