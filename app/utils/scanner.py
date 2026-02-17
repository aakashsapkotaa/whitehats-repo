"""
VirusTotal API Scanner for EduHub
Cloud-based virus scanning - no installation needed
"""
import requests
import time
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# PASTE YOUR API KEY HERE
VIRUSTOTAL_API_KEY = "b30ae986e7db7735f9912cf489fac7cb322e35b00d78216a62aaf5cd69caac45"


def scan_upload(file_content: bytes, filename: str = "upload") -> Tuple[bool, str]:
    """
    Scan file using VirusTotal API
    Returns: (is_clean: bool, message: str)
    """
    
    if VIRUSTOTAL_API_KEY == "YOUR_API_KEY_HERE":
        logger.error("API key not configured")
        return (False, "Scanner not configured")
    
    try:
        # Upload file
        url = "https://www.virustotal.com/api/v3/files"
        headers = {"x-apikey": VIRUSTOTAL_API_KEY}
        files = {"file": (filename, file_content)}
        
        response = requests.post(url, headers=headers, files=files, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        analysis_id = result['data']['id']
        
        # Wait for scan (check every 5 seconds, max 60 seconds)
        analysis_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
        
        for i in range(12):
            time.sleep(5)
            
            analysis = requests.get(analysis_url, headers=headers, timeout=10).json()
            status = analysis['data']['attributes']['status']
            
            if status == 'completed':
                stats = analysis['data']['attributes']['stats']
                malicious = stats.get('malicious', 0)
                suspicious = stats.get('suspicious', 0)
                
                if malicious > 0:
                    return (False, f"Virus detected by {malicious} security engines")
                
                if suspicious > 0:
                    return (False, f"File suspicious ({suspicious} flags)")
                
                return (True, "File is clean")
        
        return (False, "Scan timeout")
        
    except Exception as e:
        logger.error(f"Scan error: {e}")
        return (False, f"Scan failed: {str(e)}")