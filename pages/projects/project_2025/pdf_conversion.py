import numpy as np
import pandas as pd
from pypdf import PdfReader
import re
import unicodedata

chapter_pdf_names = ["P2025-NOTE", "FOREWORD"] + [f"CHAPTER-{str(i).zfill(2)}" for i in range(1, 31)] + ["AFTERWORD"]

section_names = [
    "Section 1: Taking the Reins of Government",
    "Section 2: The Common Defense",
    "Section 3: The General Welfare",
    "Section 4: The Economy",
    "Section 5: Independent Regulatory Agencies"
]

section_lens = [3, 7, 11, 8, 5]

chapter_names = [
    "A Note on 'Project 2025'",
    "Foreword: A Promise to America",
    "White House Office",
    "Executive Office of the President of the United States",
    "Central Personnel Agencies: Managing the Bureaucracy",
    "Department of Defense",
    "Department of Homeland Security",
    "Department of State",
    "Intelligence Community",
    "Media Agencies",
    "Agency for International Development",
    "Department of Agriculture",
    "Department of Education",
    "Department of Energy and Related Commissions",
    "Environmental Protection Agency",
    "Department of Health and Human Services",
    "Department of Housing and Urban Development",
    "Department of the Interior",
    "Department of Justice",
    "Department of Labor and Related Agencies",
    "Department of Transportation",
    "Department of Veterans Affairs",
    "Department of Commerce",
    "Department of the Treasury",
    "Export-Import Bank",
    "Federal Reserve",
    "Small Business Administration",
    "Trade",
    "Financial Regulatory Agencies",
    "Federal Communications Commission",
    "Federal Election Commission",
    "Federal Trade Commission",
    "Afterword",
    "Onward!"
]

has_subchapter = [8, 23, 26, 27]

subchapter_pages = [
    [1,11], [12, 17],
    [1,7], [8, 14],
    [1, 31], [32, 59],
    [1,8], [9, 15]
]

subchapter_names = [
    "U.S. Agency for Global Media",
    "Corporation for Public Broadcasting",
    "The Export-Import Bank Should Be Abolished",
    "The Case for the Export-Import Bank",
    "The Case for Fair Trade",
    "The Case for Free Trade",
    "Securities and Exchange Commission and Related Agencies",
    "Consumer Financial Protection Bureau",
]

has_multiple_authors = [3, 22]

author_names = [
    "Paul Dans",
    "Kevin D. Roberts, PhD",
    "Rick Dearborn",
    "Russ Vought",
    "Donald Devine",
    "Dennis Dean Kirk",
    "Paul Dans",
    "Christopher Miller",
    "Ken Cuccinelli",
    "Kiron K. Skinner",
    "Dustin J. Carmack",
    "Mora Namdar",
    "Mike Gonzalez",
    "Max Primorac",
    "Daren Bakst",
    "Lindsey M. Burke",
    "Bernard L. McNamee",
    "Mandy M. Gunasekara",
    "Roger Severino",
    "Benjamin S. Carson, Sr., MD",
    "William Perry Pendley",
    "Gene Hamilton",
    "Jonathan Berry",
    "Diana Furchtgott-Roth",
    "Brooks D. Tucker",
    "Thomas F. Gilman",
    "William L. Walton",
    "Stephen Moore",
    "David R. Burton",
    "Veronique de Rugy",
    "Jennifer Hazelton",
    "Paul Winfree",
    "Karen Kerrigan",
    "Peter Navarro",
    "Kent Lassman",
    "David R. Burton",
    "Robert Bowes",
    "Brendan Carr",
    "Hans A. von Spakovsky",
    "Adam Candeub",
    "Edwin J. Feulner"
]

def normalize_text(text):
    normalized_text = unicodedata.normalize('NFKD', text)
    ascii_text = normalized_text.encode('ascii', 'ignore').decode('ascii')
    return ascii_text

def remove_tab_patterns(text):
    pattern = r'(\/[a-zA-Z]+\.tab)+'
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text

def remove_bullet_points(text):
    pattern = r' l(?=[A-Z])'
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text

def convert_dash(text):
    pattern = r'—'
    cleaned_text = re.sub(pattern, "-", text)
    return cleaned_text

def convert_parenth(text):
    pattern1 = r'“'
    pattern2 = r'”'
    cleaned_text = re.sub(pattern1, "\"", text)
    cleaned_text2 = re.sub(pattern2, "\"", cleaned_text)
    return cleaned_text2


def get_chapter_text(pdf_name: str, sp: int = 1, ep: int = -1) -> str:

    pdf = PdfReader("./data/2025_MandateForLeadership_" + pdf_name + ".pdf")

    fulltext = ""

    if ep == -1:
        ep = len(pdf.pages)

    for p in range(sp - 1, ep):
        page = pdf.pages[p]
        text = page.extract_text().strip()

        text = convert_dash(text)
        text = convert_parenth(text)

        text = normalize_text(text)
        text = remove_tab_patterns(text)
        text = remove_bullet_points(text)

        split_text = text.split("\n")

        fulltext += "\n".join(split_text[1:]) + "\n"

    endnotes_position = fulltext.find('ENDNOTES')

    if endnotes_position != -1:
        fulltext = fulltext[:endnotes_position]

    return fulltext

# Data Structure
# section name | chapter # | chapter name | subsection name | author/s | text

cols, rows = (6, 37)

table = [[None for i in range(cols)] for j in range(rows)]

non_chapters = [0, 1, 36]

chapter = 1
s = 0
a = 2
sub = 0

for i in range(2, len(table) - 1):
    table[i][0] = section_names[s]
    table[i][1] = chapter
    table[i][2] = chapter_names[chapter + 1]

    section_lens[0] -= 1
    if section_lens[0] == 0:
        section_lens.pop(0)
        s += 1

    if chapter in has_multiple_authors:
        table[i][4] = author_names[a] + ", " + author_names[a + 1] + ", " + author_names[a + 2]
        a += 3
        has_multiple_authors.pop(0)
    else:
        table[i][4] = author_names[a]
        a += 1

    if table[i][5] is None: 
        table[i][5] = get_chapter_text(chapter_pdf_names[chapter + 1])

    if chapter in has_subchapter:
        has_subchapter.pop(0)

        table[i][3] = subchapter_names[sub]
        table[i][5] = get_chapter_text(chapter_pdf_names[chapter + 1], subchapter_pages[sub][0], subchapter_pages[sub][1])
        table[i+1][3] = subchapter_names[sub+1]
        table[i+1][5] = get_chapter_text(chapter_pdf_names[chapter + 1], subchapter_pages[sub+1][0], subchapter_pages[sub+1][1])
        sub += 2
    else:
        chapter += 1

    

for i in range(len(non_chapters)):
    tbl_index = non_chapters[i]
    if tbl_index == 36:
        table[tbl_index][0] = "Afterword"
        table[tbl_index][2] = chapter_names[len(chapter_names) - 1]
        table[tbl_index][4] = author_names[len(author_names) - 1]
        table[tbl_index][5] = get_chapter_text(chapter_pdf_names[len(chapter_pdf_names) - 1])
    else:
        table[i][0] = "Introduction"
        table[i][2] = chapter_names[i]
        table[i][4] = author_names[i]
        table[i][5] = get_chapter_text(chapter_pdf_names[i])


df = pd.DataFrame(table, columns=["section_name", "chapter", "chapter_name", "subsection_name", "authors", "text"])

df.to_csv("project2025.csv", encoding = "utf-8")

# Manually move extra lines CH 23 and CH 27