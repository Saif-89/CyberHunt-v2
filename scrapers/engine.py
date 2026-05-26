import json, os, time, logging
from datetime import datetime
from .keejob import KeejobScraper
from .emploi_tn import EmploiScraper
from .tunisie_jobs import TunisieJobsScraper
from .remoteok import RemoteOKScraper
from .weworkremotely import WeWorkRemotelyScraper
from .indeed import IndeedScraper
from .linkedin import LinkedInScraper
from .adzuna import AdzunaScraper
from .jobicy import JobicyScraper
from .arbeitnow import ArbeitnowScraper

logger = logging.getLogger(__name__)

SCRAPERS = {
    "keejob":         KeejobScraper,
    "emploi_tn":      EmploiScraper,
    "tunisiejobs":    TunisieJobsScraper,
    "remoteok":       RemoteOKScraper,
    "weworkremotely": WeWorkRemotelyScraper,
    "indeed":         IndeedScraper,
    "linkedin":       LinkedInScraper,
    "adzuna":         AdzunaScraper,
    "jobicy":         JobicyScraper,
    "arbeitnow":      ArbeitnowScraper,
}

RELEVANCE_BOOST = [
    "cybersecurity", "cyber security", "pentest", "penetration testing",
    "SOC", "infosec", "information security", "bug bounty", "red team",
    "blue team", "SIEM", "threat", "vulnerability", "forensics", "malware",
    "DevSecOps", "cloud security", "network security", "appsec", "GRC",
    "securite informatique", "analyste securite"
]

INTERN_BOOST = [
    "intern", "internship", "stage", "stagiaire", "trainee",
    "junior", "entry level", "graduate", "alternance", "apprentice"
]

def compute_relevance_score(job):
    text = f"{job.get('title','')} {job.get('description','')} {' '.join(job.get('tags',[]))}".lower()
    score = 0
    for kw in RELEVANCE_BOOST:
        if kw.lower() in text:
            score += 2
    for kw in INTERN_BOOST:
        if kw.lower() in text:
            score += 1
    # Tunisia bonus
    loc = job.get("location", "").lower()
    if any(x in loc for x in ["tunis", "sfax", "sousse", "bizerte", "monastir", "tn"]):
        score += 1
    # Remote bonus
    if "remote" in loc or "worldwide" in loc:
        score += 1
    return min(score, 10)  # cap at 10

def classify_region(job):
    loc = job.get("location", "").lower()
    source = job.get("source", "").lower()
    if any(x in loc for x in ["tunis", "sfax", "sousse", "bizerte", "tn", "tunisia"]):
        return "Tunisia 🇹🇳"
    if any(x in loc for x in ["remote", "worldwide", "anywhere", "global"]):
        return "Remote 🌐"
    if any(x in loc for x in ["france", "paris", "lyon"]):
        return "France 🇫🇷"
    if any(x in loc for x in ["germany", "berlin", "munich", "deutschland"]):
        return "Germany 🇩🇪"
    if any(x in loc for x in ["dubai", "uae", "emirates", "abu dhabi"]):
        return "UAE 🇦🇪"
    if any(x in loc for x in ["canada", "toronto", "montreal"]):
        return "Canada 🇨🇦"
    if any(x in loc for x in ["uk", "london", "england", "britain"]):
        return "UK 🇬🇧"
    if any(x in source for x in ["keejob", "emploi", "tunisie"]):
        return "Tunisia 🇹🇳"
    return "International 🌍"

def dedup(listings):
    seen = set()
    out = []
    for item in listings:
        key = (
            item.get("title", "").lower().strip()[:60],
            item.get("company", "").lower().strip()[:40],
        )
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out

class Engine:
    def __init__(self, data_file="data/jobs.json"):
        self.data_file = data_file
        os.makedirs(os.path.dirname(data_file), exist_ok=True)

    def load(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save(self, data):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def run(self, sources, progress):
        selected = list(SCRAPERS.keys()) if "all" in sources else [s for s in sources if s in SCRAPERS]
        progress["total"] = len(selected)
        progress["completed"] = 0
        progress["errors"] = []
        all_new = []

        for i, name in enumerate(selected):
            progress["current"] = name
            progress["progress"] = i
            progress["message"] = f"Scanning {name.capitalize()}..."
            try:
                scraper = SCRAPERS[name]()
                results = scraper.scrape()
                ts = datetime.now().isoformat()
                for r in results:
                    r["scraped_at"] = ts
                    r["region"] = classify_region(r)
                    r["relevance_score"] = compute_relevance_score(r)
                all_new.extend(results)
                progress["message"] = f"✓ {name}: {len(results)} listings"
                progress["completed"] = i + 1
            except Exception as e:
                error_msg = str(e)[:180]
                logger.error(f"Scraper {name} crashed: {e}")
                progress["errors"].append(f"{name}: {error_msg}")
                progress["message"] = f"⚠ {name} failed: {error_msg}"
            time.sleep(0.5)

        existing = self.load()
        combined = all_new + existing
        final = dedup(combined)
        # Sort by relevance then date
        final.sort(key=lambda x: (-(x.get("relevance_score", 0)), x.get("scraped_at", "")), reverse=False)
        self.save(final)
        progress["progress"] = len(selected)
        progress["new_found"] = len(all_new)
        progress["total_saved"] = len(final)
        progress["status"] = "done"
        progress["message"] = f"Complete! {len(all_new)} new • {len(final)} total saved"
        if progress.get("errors"):
            progress["message"] += f" • {len(progress['errors'])} scraper(s) failed"
