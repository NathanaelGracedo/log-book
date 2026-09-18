# scripts/latex_builder.py
"""
LaTeX Builder and XeLaTeX Compilation Engine.

Renders official weekly internship logbook pages into a complete LaTeX document
and compiles it into a high-quality PDF using XeLaTeX.
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional
from scripts.narrative_expander import escape_latex, expand_narrative


def _resolve_path(rel_path: str) -> str:
    """Resolves a path relative to CWD or to repository root."""
    if os.path.exists(rel_path):
        return rel_path
    repo_root = Path(__file__).resolve().parent.parent
    candidate = repo_root / rel_path
    if candidate.exists():
        return str(candidate)
    return rel_path


def render_week_page(
    week_data: dict,
    notes_map: dict[str, str],
    config: dict,
    assets_dir: str = "assets"
) -> str:
    """Renders a single weekly page (exact 1 page A4)."""
    resolved_assets = _resolve_path(assets_dir)
    mhs = config.get("mahasiswa", {})
    pemb = config.get("pembimbing", {})
    dosen = pemb.get("dosen", {})
    lapangan = pemb.get("lapangan", {})

    nama_mhs = escape_latex(mhs.get("nama", ""))
    nim_mhs = escape_latex(mhs.get("nim", ""))
    prodi_mhs = escape_latex(mhs.get("prodi", "Sarjana Terapan Teknik Informatika"))
    mitra_mhs = escape_latex(mhs.get("mitra", "PT Naraya Telematika"))

    nama_dosen = escape_latex(dosen.get("nama", "...................................."))
    nip_dosen = escape_latex(dosen.get("nip", "...................................."))
    nama_lapangan = escape_latex(lapangan.get("nama", "...................................."))
    nik_lapangan = escape_latex(lapangan.get("nik", "...................................."))

    polinema_logo = os.path.abspath(os.path.join(resolved_assets, "polinema.png"))
    kemendikbud_logo = os.path.abspath(os.path.join(resolved_assets, "kemendikbud.jpg"))

    # Kop surat
    has_polinema = os.path.exists(polinema_logo)
    has_kemen = os.path.exists(kemendikbud_logo)

    logo_left_tex = f"\\includegraphics[height=1.8cm]{{{polinema_logo}}}" if has_polinema else ""
    logo_right_tex = f"\\includegraphics[height=1.8cm]{{{kemendikbud_logo}}}" if has_kemen else ""

    kop_tex = rf"""
\begin{{minipage}}[c]{{0.14\textwidth}}
\centering
{logo_left_tex}
\end{{minipage}}%
\begin{{minipage}}[c]{{0.72\textwidth}}
\centering
{{\fontsize{{9pt}}{{10.5pt}}\selectfont \textbf{{KEMENTERIAN PENDIDIKAN TINGGI, SAINS, DAN TEKNOLOGI}}\\}}
{{\fontsize{{10.5pt}}{{12pt}}\selectfont \textbf{{POLITEKNIK NEGERI MALANG}}\\}}
{{\fontsize{{9.5pt}}{{11pt}}\selectfont \textbf{{JURUSAN TEKNOLOGI INFORMASI}}\\}}
{{\fontsize{{7.5pt}}{{9pt}}\selectfont Jalan Soekarno Hatta Nomor 9, Jatimulyo, Lowokwaru, Malang 65141\\}}
{{\fontsize{{7.5pt}}{{9pt}}\selectfont Telepon (0341) 404424, 404425, Faksimile (0341) 404420\\}}
{{\fontsize{{7.5pt}}{{9pt}}\selectfont Laman www.polinema.ac.id\\}}
\end{{minipage}}%
\begin{{minipage}}[c]{{0.14\textwidth}}
\centering
{logo_right_tex}
\end{{minipage}}

\vspace{{1pt}}
\hrule height 1.2pt
\vspace{{1pt}}
\hrule height 0.5pt
\vspace{{0.2cm}}
"""

    title_tex = r"""
\begin{center}
{\fontsize{11pt}{13pt}\selectfont \textbf{LOG BOOK KEGIATAN}\\}
{\fontsize{11pt}{13pt}\selectfont \textbf{PROGRAM MAGANG INDUSTRI}\\}
\end{center}
\vspace{0.15cm}
"""

    identitas_tex = rf"""
\begin{{tabular}}{{@{{}}p{{3.5cm}} p{{0.2cm}} p{{12.5cm}}@{{}}}}
Nama Mahasiswa & : & {nama_mhs} \\
NIM & : & {nim_mhs} \\
Program Studi & : & {prodi_mhs} \\
Nama Mitra Industri & : & {mitra_mhs} \\
\end{{tabular}}
\vspace{{0.2cm}}
"""

    # Rows for the table
    rows_tex = []
    for d in week_data["days"]:
        d_str = d["date_str"]
        hari_tgl = f"{d['hari']}, {d['tanggal_str']}"
        raw_note = notes_map.get(d_str, "")
        expanded = expand_narrative(raw_note)
        escaped_note = escape_latex(expanded)
        row = f"\\textbf{{{hari_tgl}}} & {d['jam_masuk']} & {d['jam_pulang']} & {escaped_note} \\\\"
        rows_tex.append(row)

    table_rows = "\n\\hline\n".join(rows_tex)

    table_tex = rf"""
\renewcommand{{\arraystretch}}{{1.15}}
\begin{{tabularx}}{{\textwidth}}{{|p{{3.8cm}}|c|c|X|}}
\hline
\textbf{{Hari, Tanggal}} & \textbf{{Jam Masuk}} & \textbf{{Jam Pulang}} & \textbf{{Kegiatan}} \\
\hline
{table_rows}
\hline
\end{{tabularx}}
\vspace{{0.3cm}}
"""

    ttd_tex = rf"""
\noindent
\begin{{tabularx}}{{\textwidth}}{{@{{}}X X X@{{}}}}
Mahasiswa, & Mengetahui, & \\
& Dosen Pembimbing, & Pembimbing Lapangan, \\[1.2cm]
\textbf{{{nama_mhs}}} & \textbf{{{nama_dosen}}} & \textbf{{{nama_lapangan}}} \\
NIM. {nim_mhs} & NIP. {nip_dosen} & NIK. {nik_lapangan} \\
\end{{tabularx}}
"""

    return kop_tex + title_tex + identitas_tex + table_tex + ttd_tex


def generate_latex_document(
    weeks: list[dict],
    notes_map: dict[str, str],
    config: dict,
    assets_dir: str = "assets",
    template_path: str = "templates/logbook_template.tex"
) -> str:
    """Renders all weekly pages into the complete LaTeX document."""
    page_blocks = []
    for w in weeks:
        page_content = render_week_page(w, notes_map, config, assets_dir)
        page_blocks.append(page_content)

    joined_content = "\n\\clearpage\n".join(page_blocks)

    resolved_template = _resolve_path(template_path)
    with open(resolved_template, "r", encoding="utf-8") as f:
        master_template = f.read()

    return master_template.replace("%CONTENT_BLOCK%", joined_content)


def compile_pdf(latex_code: str, output_pdf_path: str, work_dir: Optional[str] = None) -> bool:
    """Compiles LaTeX code using XeLaTeX into the target output PDF path."""
    clean_tmp = False
    if work_dir is None:
        work_dir = tempfile.mkdtemp(prefix="logbook_xelatex_")
        clean_tmp = True

    try:
        tex_path = os.path.join(work_dir, "document.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_code)

        # Run xelatex twice to resolve LastPage references
        for _ in range(2):
            cmd = [
                "xelatex",
                "-interaction=nonstopmode",
                f"-output-directory={work_dir}",
                tex_path
            ]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if proc.returncode != 0:
                raise RuntimeError(f"XeLaTeX compilation failed with exit code {proc.returncode}:\n{proc.stdout[-1500:]}")

        built_pdf = os.path.join(work_dir, "document.pdf")
        if not os.path.exists(built_pdf):
            raise FileNotFoundError("Output PDF was not created by XeLaTeX.")

        target_dir = os.path.dirname(os.path.abspath(output_pdf_path))
        os.makedirs(target_dir, exist_ok=True)
        shutil.copyfile(built_pdf, output_pdf_path)
        return True

    finally:
        if clean_tmp and os.path.exists(work_dir):
            shutil.rmtree(work_dir, ignore_errors=True)
