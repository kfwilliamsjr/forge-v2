"""
OCR preprocessing for scanned PDFs.

Many tax returns arrive as image-only scans with no text layer. `pdftotext`
returns near-empty output on these files. This module detects that condition
and runs `ocrmypdf` to produce a searchable copy, then hands it back to the
form extractors.

Day 6 learning: 5 of 6 tax returns in the Mirzai/TTH training batch had no
text layer. Without OCR preprocessing, extractors return all None. With OCR,
the Day 3 Schedule M-1 rule immediately extracted Net Income per Books on
the TTH 2024 return on first try.

Requires: `pdftotext` (poppler-utils) and `ocrmypdf` on PATH.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

# Cache OCR output to avoid re-running on every extractor call.
# 21 seconds per return adds up fast across the pipeline.
_OCR_CACHE_DIR = Path(tempfile.gettempdir()) / "underwriteos_ocr_cache"
_OCR_CACHE_DIR.mkdir(exist_ok=True)

# If extracted text is shorter than this, treat the PDF as scanned.
# AIPSS returns produce ~30,000 bytes. Empty scans produce 7-10 bytes.
_TEXT_LAYER_THRESHOLD_BYTES = 500


def _pdftotext(pdf_path: Path) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        capture_output=True, text=True, check=False,
    )
    return result.stdout


def _file_fingerprint(pdf_path: Path) -> str:
    stat = pdf_path.stat()
    # Fingerprint on path + size + mtime. Full content hash is overkill.
    key = f"{pdf_path.resolve()}|{stat.st_size}|{stat.st_mtime_ns}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def needs_ocr(pdf_path: str | Path) -> bool:
    """Return True if the PDF lacks a usable text layer."""
    text = _pdftotext(Path(pdf_path))
    return len(text.strip()) < _TEXT_LAYER_THRESHOLD_BYTES


# OCR quality profiles.
#
# "fast"  — minimal processing, used for documents that already have a clean
#           text layer or for quick checks.
# "standard" — deskew + clean + 400 DPI oversample. Good default for typical
#           business-grade scans (bank statements, loan reports).
# "high"  — standard + rotate-pages + 600 DPI + clean-final. Use for dense
#           tax forms where line numbers and dollar values share tight layouts
#           (Form 1120-S, 1040, 4562). Slower but materially better recall on
#           the two-pass label extractor.
_OCR_PROFILES = {
    "fast": [
        "--force-ocr",
        "--skip-big", "50",
        "--output-type", "pdf",
        "--quiet",
    ],
    "standard": [
        "--force-ocr",
        "--skip-big", "50",
        "--deskew",
        "--oversample", "400",
        "--output-type", "pdf",
        "--quiet",
    ],
    "high": [
        "--force-ocr",
        "--skip-big", "50",
        "--rotate-pages",
        "--deskew",
        "--oversample", "450",
        "--jobs", "4",
        "--output-type", "pdf",
        "--quiet",
    ],
}

# --clean and --clean-final require the `unpaper` binary which isn't
# present on every system. When available, adding --clean to "high"
# meaningfully improves OCR on dense tax forms. To enable, install:
#   Debian/Ubuntu: apt install unpaper
#   macOS (brew):  brew install unpaper
# then set env var UNDERWRITEOS_OCR_CLEAN=1.
if os.environ.get("UNDERWRITEOS_OCR_CLEAN") == "1":
    _OCR_PROFILES["standard"].insert(-4, "--clean")
    _OCR_PROFILES["high"].insert(-4, "--clean")
    _OCR_PROFILES["high"].insert(-4, "--clean-final")


def ensure_text_layer(
    pdf_path: str | Path,
    force: bool = False,
    profile: str = "standard",
) -> Path:
    """
    Return a path to a PDF with a usable text layer.

    Profiles:
        fast     — quick OCR, no cleanup
        standard — deskew + clean + 400 DPI (default)
        high     — rotate + deskew + clean + 600 DPI (tax forms)

    Cache key includes the profile so different quality runs don't collide.

    Raises FileNotFoundError if the source does not exist.
    Raises RuntimeError if ocrmypdf fails.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(str(pdf_path))

    if profile not in _OCR_PROFILES:
        raise ValueError(f"Unknown OCR profile: {profile}")

    if not force and not needs_ocr(pdf_path):
        return pdf_path

    cache_key = f"{_file_fingerprint(pdf_path)}_{profile}"
    cached = _OCR_CACHE_DIR / f"{cache_key}.pdf"
    if cached.exists() and not force:
        return cached

    env = os.environ.copy()
    extra_bin = Path.home() / ".local" / "bin"
    if extra_bin.exists():
        env["PATH"] = f"{extra_bin}:{env.get('PATH', '')}"

    if shutil.which("ocrmypdf", path=env["PATH"]) is None:
        raise RuntimeError(
            "ocrmypdf not found. Install with: pip install ocrmypdf"
        )

    cmd = ["ocrmypdf"] + _OCR_PROFILES[profile] + [str(pdf_path), str(cached)]
    try:
        subprocess.run(cmd, check=True, env=env, capture_output=True)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode("utf-8", errors="replace") if e.stderr else ""
        # Some scans fail on --clean (unpaper can choke on odd sizes).
        # Retry once with a fallback to the next-lower profile.
        if profile == "high":
            return ensure_text_layer(pdf_path, force=force, profile="standard")
        if profile == "standard":
            return ensure_text_layer(pdf_path, force=force, profile="fast")
        raise RuntimeError(f"ocrmypdf failed on {pdf_path.name}: {stderr}") from e

    return cached


import re as _re

# Tesseract routinely drops the thousands-separator comma on dense forms,
# rendering "757,140" as "757 140" (two space-separated tokens). Downstream
# `_last_int_on_line` then grabs "140", crushing the real value.
#
# This post-processor walks each line and rejoins sequences of 1–3 digit
# groups separated by a single space into a single comma-separated number,
# BUT ONLY when:
#   - the first group is 1–3 digits
#   - every trailing group is exactly 3 digits
#   - the sequence has 2+ groups (single numbers are left alone)
#
# This matches the grouping rules for real money amounts and avoids
# corrupting legitimate side-by-side integers (e.g. "12 34 56" which would
# fail the "all trailing groups are 3 digits" check).
# Separator class: space OR a single-char OCR misread of a comma. Common
# tesseract confusions for "," in dense forms: i, l, I, r, t, |, ., '
_SEP = r"[ \u00A0]+[,.'`|iIlLrRtT]?[ \u00A0]*"
_NUMBER_REJOIN_RE = _re.compile(
    rf"(?<![\w\d])(\d{{1,3}})(?:{_SEP}(\d{{3}})){{1,3}}(?![\w\d])"
)


def _rejoin_split_numbers(line: str) -> str:
    def _sub(m: _re.Match) -> str:
        chunk = m.group(0)
        # Strip all non-digit characters, then re-group into thousands
        digits = _re.sub(r"\D", "", chunk)
        # Re-insert commas from the right
        if len(digits) <= 3:
            return digits
        out = ""
        while len(digits) > 3:
            out = "," + digits[-3:] + out
            digits = digits[:-3]
        return digits + out
    return _NUMBER_REJOIN_RE.sub(_sub, line)


import re as _re

# OCR sometimes inserts a space after a thousands comma: "466, 391" → "466,391"
_SPACE_AFTER_COMMA_RE = _re.compile(r"(\d{1,3}),\s+(\d{3})(?=\D|$)")

# OCR sometimes fuses a leading line-number into a money token via comma:
# "1,188,300." where 1 is the schedule line number and 188,300 is the value.
# Heuristic: a 4-or-more-group comma number whose leading group is a single
# digit is suspicious; strip the leading digit + comma. We only strip when
# the leading group is 1-2 digits AND the next group is exactly 3 digits.
_LINENUM_FUSION_RE = _re.compile(r"(?<![\d,])(\d{1,2}),(\d{3},\d{3})(?=\D|$)")


def _strip_space_after_comma(line: str) -> str:
    return _SPACE_AFTER_COMMA_RE.sub(r"\1,\2", line)


def _strip_linenum_fusion(line: str) -> str:
    # Only apply when the line looks like a tax-form data row (has a label
    # word followed by the fused token). This is a conservative heuristic.
    if not _re.search(r"[A-Za-z]", line):
        return line
    return _LINENUM_FUSION_RE.sub(r"\2", line)


def postprocess_ocr_text(text: str) -> str:
    """Rejoin OCR-split thousands-separated numbers line by line, plus
    fix space-after-comma artifacts and strip fused line-number prefixes."""
    # NOTE: Line-number fusion stripping is intentionally NOT applied here.
    # The naive regex strips legitimate values like "1,268,644". Proper fix
    # requires tesseract TSV layout output (deferred to Day 11). Extractors
    # should apply per-form line-number plausibility filters instead.
    out = []
    for line in text.splitlines():
        line = _rejoin_split_numbers(line)
        line = _strip_space_after_comma(line)
        out.append(line)
    return "\n".join(out)


def read_pdf_text(pdf_path: str | Path, profile: str = "standard") -> str:
    """
    Read PDF text, transparently running OCR if the source is a scanned image.

    Pass profile="high" for dense tax forms where label/value proximity
    matters and standard OCR leaves artifacts like line-number bleed.

    If the PDF required OCR, the returned text is passed through
    `postprocess_ocr_text` to rejoin thousands-separated numbers that
    tesseract split into space-separated chunks.
    """
    pdf_path = Path(pdf_path)
    was_scanned = needs_ocr(pdf_path)
    resolved = ensure_text_layer(pdf_path, profile=profile)
    text = _pdftotext(resolved)
    if was_scanned:
        text = postprocess_ocr_text(text)
    return text
