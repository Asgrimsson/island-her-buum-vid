from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

required = [
    "app.py",
    "requirements.txt",
    ".streamlit/config.toml",
    "data",
]

for item in required:
    if not (ROOT / item).exists():
        errors.append(f"Vantar: {item}")

for py in ROOT.rglob("*.py"):
    if ".venv" in py.parts or "venv" in py.parts:
        continue
    try:
        compile(py.read_text(encoding="utf-8"), str(py), "exec")
    except Exception as e:
        errors.append(f"Syntax villa í {py.relative_to(ROOT)}: {e}")

if errors:
    print("HEALTHCHECK FAILED")
    print("\n".join(errors))
    sys.exit(1)

print("HEALTHCHECK OK — Ísland hér búum við er tilbúið til deploy.")
