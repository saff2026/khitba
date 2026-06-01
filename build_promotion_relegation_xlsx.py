#!/usr/bin/env python3
"""Simplified promotion/relegation table for the first 5 tiers of the
top-5 European football pyramids, with one official-source link per row."""

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

HEADERS = ["Country", "Division", "Tier", "Clubs",
           "Clubs promoted", "Promotion %",
           "Clubs relegated", "Relegation %",
           "Has playoff?", "Official source"]

# country, division, tier, clubs, promoted, promo%, relegated, rel%, playoff, (source_text, source_url)
ROWS = [
    # England
    ["England", "Premier League", 1, "20", "—", "—", "3", "15.0%", "No",
     ("premierleague.com", "https://www.premierleague.com/en/premier-league-explained")],
    ["England", "EFL Championship", 2, "24", "3", "12.5%", "3", "12.5%", "Yes (promotion)",
     ("efl.com", "https://www.efl.com/competitions/efl-championship/")],
    ["England", "EFL League One", 3, "24", "3", "12.5%", "4", "16.7%", "Yes (promotion)",
     ("efl.com", "https://www.efl.com/competitions/efl-league-one/")],
    ["England", "EFL League Two", 4, "24", "4", "16.7%", "2", "8.3%", "Yes (promotion)",
     ("efl.com", "https://www.efl.com/competitions/efl-league-two/")],
    ["England", "National League", 5, "24", "2", "8.3%", "4", "16.7%", "Yes (promotion)",
     ("thenationalleague.org.uk", "https://www.thenationalleague.org.uk/")],
    # Spain
    ["Spain", "LaLiga (EA Sports)", 1, "20", "—", "—", "3", "15.0%", "No",
     ("laliga.com", "https://www.laliga.com/en-GB/laliga-easports")],
    ["Spain", "LaLiga2 (Hypermotion)", 2, "22", "3", "13.6%", "4", "18.2%", "Yes (promotion)",
     ("laliga.com", "https://www.laliga.com/en-GB/laliga-hypermotion")],
    ["Spain", "Primera Federacion", 3, "40 (2 groups x 20)", "4", "10.0%", "10", "25.0%", "Yes (promotion)",
     ("rfef.es", "https://rfef.es/es/competiciones/primera-federacion")],
    ["Spain", "Segunda Federacion", 4, "90 (5 groups x 18)", "10", "11.1%", "~27", "~30%", "Yes (promotion + relegation)",
     ("rfef.es", "https://rfef.es/es/noticias/competiciones-masculinas/segunda-federacion")],
    ["Spain", "Tercera Federacion", 5, "~325 (18 groups)", "27", "~8.3%", "~54+", "~17%", "Yes (promotion)",
     ("rfef.es", "https://rfef.es/es/competiciones/tercera-federacion")],
    # Germany
    ["Germany", "Bundesliga", 1, "18", "—", "—", "2-3", "11.1-16.7%", "Yes (relegation)",
     ("bundesliga.com", "https://www.bundesliga.com/en/bundesliga")],
    ["Germany", "2. Bundesliga", 2, "18", "2-3", "11.1-16.7%", "2-3", "11.1-16.7%", "Yes (promotion + relegation)",
     ("bundesliga.com", "https://www.bundesliga.com/en/2bundesliga")],
    ["Germany", "3. Liga", 3, "20", "2-3", "10.0-15.0%", "4", "20.0%", "Yes (promotion)",
     ("dfb.de", "https://www.dfb.de/en/leagues/3-liga/")],
    ["Germany", "Regionalliga", 4, "~90 (5 groups x 18)", "~4", "~4.4%", "varies", "~10-20%", "Yes (promotion)",
     ("dfb.de", "https://www.dfb.de/maenner/ligen")],
    ["Germany", "Oberliga", 5, "varies (14 leagues)", "~1/league", "~6%", "varies", "varies", "Sometimes (regional)",
     ("dfb.de", "https://www.dfb.de/maenner/ligen")],
    # Italy
    ["Italy", "Serie A", 1, "20", "—", "—", "3", "15.0%", "No",
     ("legaseriea.it", "https://en.legaseriea.it/serie-a")],
    ["Italy", "Serie B", 2, "20", "3", "15.0%", "4", "20.0%", "Yes (promotion + relegation)",
     ("legab.it", "https://www.legab.it/seriebkt")],
    ["Italy", "Serie C", 3, "60 (3 groups x 20)", "4", "6.7%", "~9", "~15%", "Yes (promotion + relegation)",
     ("legapro.it", "https://www.legapro.it/")],
    ["Italy", "Serie D", 4, "~162 (9 groups x 18)", "9", "~5.6%", "~36", "~22%", "Yes (relegation)",
     ("lnd.it", "https://seried.lnd.it/it/serie-d")],
    ["Italy", "Eccellenza", 5, "~474 (~28 groups)", "~36", "~7.6%", "~2-4/group", "~12-20%", "Yes (promotion + relegation)",
     ("lnd.it", "https://www.lnd.it/it/competition")],
    # France
    ["France", "Ligue 1", 1, "18", "—", "—", "2-3", "11.1-16.7%", "Yes (relegation barrage)",
     ("lfp.fr", "https://www.lfp.fr/")],
    ["France", "Ligue 2", 2, "18", "2-3", "11.1-16.7%", "2-3", "11.1-16.7%", "Yes (promotion + relegation barrage)",
     ("lfp.fr", "https://www.lfp.fr/")],
    ["France", "Championnat National", 3, "18", "2-3", "11.1-16.7%", "2", "~11.1%", "Yes (promotion barrage)",
     ("fff.fr", "https://www.fff.fr/")],
    ["France", "National 2", 4, "48 (3 groups x 16)", "3", "~6.25%", "~10", "~20.8%", "No",
     ("fff.fr", "https://media.fff.fr/uploads/documents/reglements-des-championnats-n1-et-n2-20252026-ok.pdf")],
    ["France", "National 3", 5, "140 (10 groups x 14)", "10", "~7.1%", "varies", "variable", "No",
     ("fff.fr", "https://www.fff.fr/")],
]

FOOTNOTES = [
    "Structure as of the 2024-25 / 2025-26 seasons. 'Clubs promoted/relegated' are totals per season including any playoff places; % = clubs moved / clubs in division x 100.",
    "Ranges are given where the count depends on a playoff/barrage, financial licensing, reserve-team eligibility, or ongoing league restructuring (mainly the regionalised lower tiers).",
    "'Has playoff?' covers promotion/relegation playoffs (England playoffs, German Relegation, Italian playout, French barrage). Regionalised tiers' relegation counts are set annually by regional federations.",
    "Sources are the official governing-body / league websites (Premier League, EFL & National League; LaLiga & RFEF; Bundesliga & DFB; Lega Serie A/B, Lega Pro & LND; LFP & FFF).",
]

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
TITLE_FONT = Font(bold=True, size=13, color="1F4E78")
LINK_FONT = Font(color="0563C1", underline="single")
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)
COUNTRY_FILLS = {"England": "FCE4D6", "Spain": "FFF2CC", "Germany": "E2EFDA",
                 "Italy": "DEEBF7", "France": "EDE7F6"}

wb = Workbook()
ws = wb.active
ws.title = "Promotion & Relegation"

ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(HEADERS))
t = ws.cell(row=1, column=1,
            value="Promotion & Relegation - Top 5 European Football Pyramids, Tiers 1-5 (2024-25 / 2025-26)")
t.font = TITLE_FONT
ws.row_dimensions[1].height = 20

for c, h in enumerate(HEADERS, 1):
    cell = ws.cell(row=2, column=c, value=h)
    cell.fill = HEADER_FILL
    cell.font = HEADER_FONT
    cell.alignment = CENTER
    cell.border = BORDER

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

widths = [11, 24, 6, 20, 13, 13, 13, 13, 26, 26]
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
