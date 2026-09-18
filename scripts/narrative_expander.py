# scripts/narrative_expander.py
"""
Narrative Expansion & LaTeX Escaping Engine.

Provides utilities for:
1. escape_latex: Escapes LaTeX special characters in text.
2. expand_narrative: Transforms concise internship bullet points into formal
   Indonesian professional sentences suitable for Polinema's official logbook.
"""

import re
from typing import Optional

# LaTeX special character mappings
LATEX_ESCAPE_MAP = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

_LATEX_ESCAPE_PATTERN = re.compile(r"([\\&%$#{}_~^])")


def escape_latex(text: Optional[str]) -> str:
    """
    Escapes LaTeX special characters in string.
    Special chars handled: \\ & % $ # _ { } ~ ^

    Uses a single-pass regex replacement to ensure macro-generated
    characters (such as braces in \\textbackslash{}) are not re-escaped.
    """
    if not text:
        return ""

    return _LATEX_ESCAPE_PATTERN.sub(lambda m: LATEX_ESCAPE_MAP[m.group(0)], text)


EXPANSION_RULES = [
    (
        r"^(?:onboarding|orientasi)\b(.*)",
        r"Mengikuti kegiatan onboarding magang dan pengenalan lingkungan kerja industri\1.",
    ),
    (
        r"^(?:setup laptop|setup environment|setup env|setup dev)\b(.*)",
        r"Melakukan instalasi dan konfigurasi lingkungan pengembangan perangkat lunak pada perangkat kerja\1.",
    ),
    (
        r"^(?:pelajari|belajar|analisis)\b(.*)",
        r"Mempelajari dan menganalisis arsitektur sistem serta dokumentasi proyek\1.",
    ),
    (
        r"^(?:meeting|rapat|daily standup|standup)\b(.*)",
        r"Menghadiri rapat koordinasi tim dan sinkronisasi tugas harian\1.",
    ),
    (
        r"^(?:code review|review code|review)\b(.*)",
        r"Melakukan peninjauan kembali kode program (code review) dan diskusi implementasi\1.",
    ),
    (
        r"^(?:eksplorasi|riset)\b(.*)",
        r"Melakukan eksplorasi teknis dan riset implementasi terhadap\1.",
    ),
    (
        r"^(?:implementasi|coding|develop|buat|membuat)\b(.*)",
        r"Mengembangkan dan mengimplementasikan modul fitur\1.",
    ),
    (
        r"^(?:testing|uji|pengujian)\b(.*)",
        r"Melakukan pengujian sistem serta verifikasi fungsionalitas fitur\1.",
    ),
    (
        r"^(?:bugfix|fixing|perbaikan bug|perbaikan)\b(.*)",
        r"Melakukan penelusuran masalah dan perbaikan kendala teknis (bug fixing)\1.",
    ),
    (
        r"^(?:dokumentasi|susun dokumen)\b(.*)",
        r"Menyusun dan memperbarui dokumentasi teknis kegiatan magang\1.",
    ),
]


def expand_narrative(bullet: Optional[str]) -> str:
    """
    Expands a concise bullet point into a formal Indonesian professional sentence.
    If the sentence is already formal (starts with capital and ends with period/punctuation),
    returns it normalized without modifications.
    """
    if not bullet or not bullet.strip():
        return ""

    clean = bullet.strip().lstrip("-*•1234567890. ").strip()
    if not clean:
        return ""

    # Check if already a formal complete sentence
    if clean[0].isupper() and clean.endswith((".", "!", "?")):
        return clean

    # Attempt pattern matches
    for pattern, template in EXPANSION_RULES:
        m = re.search(pattern, clean, flags=re.IGNORECASE)
        if m:
            tail = m.group(1).strip().lstrip(":- ").strip()
            if tail:
                expanded = template.replace(r"\1", f" {tail}")
            else:
                expanded = template.replace(r"\1", "")
                expanded = re.sub(r"\s+terhadap(?=\.|$)", "", expanded)

            expanded = re.sub(r"\s+", " ", expanded).strip().rstrip(".") + "."
            return expanded[0].upper() + expanded[1:]

    # Fallback: capitalize first letter, prepend "Melakukan " if starts with lowercase verb/noun, and add period
    if not clean[0].isupper():
        clean = "Melakukan " + clean
    clean = clean.rstrip(".") + "."
    return clean[0].upper() + clean[1:]
