"""
File scanning utilities — SHA256 hashing + VirusTotal API scanner.
Falls back to simulated scan (always clean) when no API key is configured.
"""
import hashlib
import requests
import time
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Set your VirusTotal API key here (or leave empty for simulated scan)
VIRUSTOTAL_API_KEY = ""

# --- File size & extension limits ---
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".txt", ".md", ".csv", ".zip", ".rar", ".7z",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",
    ".mp4", ".mp3", ".wav",
    ".py", ".js", ".html", ".css", ".json", ".xml",
    ".c", ".cpp", ".java",
}


def compute_sha256(content: bytes) -> str:
    """Compute SHA256 hash of file content."""
    return hashlib.sha256(content).hexdigest()


def scan_upload(file_content: bytes, filename: str = "upload") -> Tuple[bool, str]:
    """
    Scan file using VirusTotal API.
    Returns: (is_clean: bool, message: str)
    Falls back to simulated scan if no API key is set.
    """

    if not VIRUSTOTAL_API_KEY:
        logger.info("No VirusTotal API key — simulated scan (clean)")
        return (True, "File is clean (simulated scan)")

    try:
        url = "https://www.virustotal.com/api/v3/files"
        headers = {"x-apikey": VIRUSTOTAL_API_KEY}
        files = {"file": (filename, file_content)}

        response = requests.post(url, headers=headers, files=files, timeout=30)
        response.raise_for_status()

        result = response.json()
        analysis_id = result["data"]["id"]

        analysis_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"

        for _ in range(12):
            time.sleep(5)
            analysis = requests.get(analysis_url, headers=headers, timeout=10).json()
            status = analysis["data"]["attributes"]["status"]

            if status == "completed":
                stats = analysis["data"]["attributes"]["stats"]
                malicious = stats.get("malicious", 0)
                suspicious = stats.get("suspicious", 0)

                if malicious > 0:
                    return (False, f"Virus detected by {malicious} security engines")
                if suspicious > 0:
                    return (False, f"File suspicious ({suspicious} flags)")
                return (True, "File is clean")

        return (False, "Scan timeout")

    except Exception as e:
        logger.error(f"Scan error: {e}")
        return (False, f"Scan failed: {str(e)}")