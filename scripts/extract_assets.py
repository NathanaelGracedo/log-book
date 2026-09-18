import zipfile
import os
from pathlib import Path

def extract_assets_from_docx(docx_path: str = "Log Book Template.docx", assets_dir: str = "assets") -> dict[str, str]:
    """
    Extracts Polinema and Kemendikbud logo assets from the original docx template.
    """
    target_path = Path(assets_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    
    extracted = {}
    with zipfile.ZipFile(docx_path, 'r') as docx:
        for item in docx.namelist():
            if item == "word/media/image2.png":
                out_file = target_path / "polinema.png"
                with open(out_file, "wb") as f:
                    f.write(docx.read(item))
                extracted["polinema"] = str(out_file)
            elif item == "word/media/image1.jpg":
                out_file = target_path / "kemendikbud.jpg"
                with open(out_file, "wb") as f:
                    f.write(docx.read(item))
                extracted["kemendikbud"] = str(out_file)
                
    # If kemendikbud wasn't a distinct image in docx, copy polinema or fallback
    if "kemendikbud" not in extracted and "polinema" in extracted:
        fallback_kemen = target_path / "kemendikbud.jpg"
        with open(extracted["polinema"], "rb") as src, open(fallback_kemen, "wb") as dst:
            dst.write(src.read())
        extracted["kemendikbud"] = str(fallback_kemen)

    return extracted

if __name__ == "__main__":
    res = extract_assets_from_docx()
    print("Extracted assets:", res)
