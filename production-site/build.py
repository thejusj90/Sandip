"""Build the editable Dipatma content and bundled images for production."""
from pathlib import Path
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parent
out = root / "dist"
if out.exists():
    shutil.rmtree(out)
subprocess.run([
    sys.executable, str(root / "generate.py"),
    "--out", str(out),
    "--domain", "https://www.dipatmawellness.com",
    "--form-action", "https://formsubmit.co/hello@dipatmawellness.com",
    "--privacy-file", str(root / "privacy-notice.md"),
], check=True)

# Fail the release if generated pages, navigation or enquiry fields regress.
subprocess.run([sys.executable, str(root / "verify.py")], check=True)
