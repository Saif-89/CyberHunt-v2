import requests
from bs4 import BeautifulSoup
import time
import random
import logging

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
]

CYBERSEC_KEYWORDS = [
    "cybersecurity", "cyber security", "information security", "infosec",
    "penetration testing", "pentest", "ethical hacking", "SOC analyst",
    "network security", "cloud security", "application security", "appsec",
    "SIEM", "threat intelligence", "vulnerability", "incident response",
    "forensics", "blue team", "red team", "security operations",
    "malware analyst", "cryptography", "firewall", "zero trust",
    "IAM", "identity access", "security engineer", "security analyst",
    "CISO", "GRC", "compliance security", "risk analyst", "DevSecOps",
    "CTF", "bug bounty", "reverse engineering", "exploit", "OSINT",
    "securite informatique", "securite reseau", "analyste securite",
]

INTERN_KEYWORDS = [
    "intern", "internship", "stage", "stagiaire", "trainee",
    "graduate", "entry level", "junior", "apprentice", "alternance"
]

class BaseScraper:
    def __init__(self, name, delay_range=(2.0, 4.5)):
        self.name = name
        self.delay_range = delay_range
        self.session = requests.Session()
        self._rotate_headers()

    def _rotate_headers(self):
        ua = random.choice(USER_AGENTS)
        self.session.headers.update({
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,fr;q=0.8,ar;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })

    def _sleep(self, extra=0):
        t = random.uniform(*self.delay_range) + extra
        time.sleep(t)

    def fetch_html(self, url, params=None, extra_headers=None, retries=2):
        self._rotate_headers()
        if extra_headers:
            self.session.headers.update(extra_headers)
        for attempt in range(retries + 1):
            try:
                self._sleep()
                resp = self.session.get(url, params=params, timeout=18, allow_redirects=True)
                resp.raise_for_status()
                return BeautifulSoup(resp.text, "lxml")
            except Exception as e:
                logger.warning(f"[{self.name}] Attempt {attempt+1} failed for {url}: {e}")
                if attempt < retries:
                    time.sleep(random.uniform(3, 6))
        return None

    def fetch_json(self, url, params=None, extra_headers=None, retries=2):
        self._rotate_headers()
        h = {"Accept": "application/json", "Content-Type": "application/json"}
        if extra_headers:
            h.update(extra_headers)
        for attempt in range(retries + 1):
            try:
                self._sleep()
                resp = self.session.get(url, params=params, headers={**self.session.headers, **h}, timeout=18)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                logger.warning(f"[{self.name}] JSON attempt {attempt+1} failed: {e}")
                if attempt < retries:
                    time.sleep(random.uniform(2, 5))
        return None

    def is_cybersec_relevant(self, text):
        t = text.lower()
        return any(k in t for k in CYBERSEC_KEYWORDS)

    def is_intern_level(self, text):
        t = text.lower()
        return any(k in t for k in INTERN_KEYWORDS)

    def build_entry(self, title, company, location, url, description="",
                    source=None, job_type="Internship", tags=None,
                    salary="", posted="", deadline=""):
        return {
            "title": title.strip(),
            "company": company.strip() if company else "N/A",
            "location": location.strip() if location else "N/A",
            "url": url.strip() if url else "#",
            "description": description.strip()[:500] if description else "",
            "source": source or self.name,
            "type": job_type,
            "tags": tags or [],
            "salary": salary,
            "posted": posted,
            "deadline": deadline,
        }

    def scrape(self):
        raise NotImplementedError
