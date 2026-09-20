# scripts/doctor.py
"""
Pre-flight environment doctor check for XeLaTeX installation.
Provides cross-platform installation instructions when dependencies are missing.
"""

import shutil
import sys
from typing import Tuple

XELATEX_INSTALL_GUIDE = """
[ERROR] Program kompilasi 'xelatex' tidak ditemukan di sistem Anda!
Log book ini memerlukan XeLaTeX untuk mengompilasi lembar PDF dengan presisi tinggi.

Silakan pasang XeLaTeX sesuai sistem operasi Anda:

1. Ubuntu / Debian / Linux Mint:
   sudo apt update && sudo apt install texlive-xetex texlive-fonts-recommended

2. Arch Linux / Manjaro:
   sudo pacman -S texlive-bin texlive-core

3. Fedora / RHEL:
   sudo dnf install texlive-xetex texlive-collection-fontsrecommended

4. macOS (via Homebrew):
   brew install --cask mactex-no-gui
   # Atau MacTeX lengkap: brew install --cask mactex

5. Windows:
   Unduh dan pasang MiKTeX dari: https://miktex.org/download
   Pastikan opsi "Always install missing packages on the fly" diaktifkan.

Setelah instalasi selesai, buka kembali terminal Anda dan jalankan perintah kembali.
"""


def check_xelatex() -> Tuple[bool, str]:
    """
    Checks if xelatex executable is available in PATH.
    Returns (True, path_to_binary) if found, or (False, install_instructions).
    """
    path = shutil.which("xelatex")
    if path:
        return True, path
    return False, XELATEX_INSTALL_GUIDE


def run_doctor(exit_on_failure: bool = True) -> bool:
    """
    Runs pre-flight system checks. Prints clear guidance and exits if missing.
    """
    ok, message = check_xelatex()
    if not ok:
        print(message, file=sys.stderr)
        if exit_on_failure:
            sys.exit(1)
        return False
    return True


if __name__ == "__main__":
    if run_doctor(exit_on_failure=False):
        ok, path = check_xelatex()
        print(f"[OK] XeLaTeX ditemukan di: {path}")
    else:
        sys.exit(1)
