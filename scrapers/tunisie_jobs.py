from .base import BaseScraper
import time, random

QUERIES = ["cybersecurity", "securite informatique", "SOC", "reseau securite", "pentest", "analyste securite"]

class TunisieJobsScraper(BaseScraper):
    def __init__(self):
        super().__init__("TunisieJobs")

    def scrape(self):
        results = []
        for q in QUERIES:
            soup = self.fetch_html("https://www.tunisiejobs.com/jobs/search",
                                   params={"keywords": q, "type": "stage"})
            if not soup:
                soup = self.fetch_html("https://www.tunisiejobs.com/offres-emploi-tunisie",
                                       params={"q": q})
            if not soup:
                continue
            cards = soup.select("div.job, li.job-item, article.job-listing, div[class*='job-card']")
            for card in cards:
                try:
                    title_el = card.select_one("h2 a, h3 a, .job-title a, a.title")
                    company_el = card.select_one(".company, .employer, .company-name")
                    loc_el = card.select_one(".location, .city, .ville")
                    desc_el = card.select_one(".description, .summary, p")
                    date_el = card.select_one(".date, time, .posted")

                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title:
                        continue
                    if not self.is_cybersec_relevant(title + (desc_el.get_text() if desc_el else "")):
                        continue

                    href = title_el.get("href", "") if title_el else ""
                    full_url = href if href.startswith("http") else f"https://www.tunisiejobs.com{href}"
                    company = company_el.get_text(strip=True) if company_el else "N/A"
                    location = loc_el.get_text(strip=True) if loc_el else "Tunisia"
                    desc = desc_el.get_text(strip=True)[:400] if desc_el else ""
                    posted = date_el.get_text(strip=True) if date_el else ""

                    results.append(self.build_entry(
                        title=title, company=company,
                        location=location or "Tunisia",
                        url=full_url, description=desc,
                        job_type="Stage / Emploi", posted=posted,
                        tags=["tunisia", "tunisiejobs", q]
                    ))
                except Exception:
                    continue
            time.sleep(random.uniform(2, 3.5))
        return results
