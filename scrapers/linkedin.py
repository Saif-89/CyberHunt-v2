from .base import BaseScraper
import time, random

QUERIES = [
    "cybersecurity internship", "cyber security intern", "SOC analyst intern",
    "information security internship", "penetration testing intern",
    "network security intern", "security engineer intern", "DevSecOps intern",
    "bug bounty intern", "cloud security intern"
]
LOCATIONS = ["Tunisia", "Remote", "France", "Germany", "UAE", "Canada", "Netherlands"]

class LinkedInScraper(BaseScraper):
    def __init__(self):
        super().__init__("LinkedIn")

    def scrape(self):
        results = []
        for q in QUERIES[:5]:
            for loc in LOCATIONS[:4]:
                params = {
                    "keywords": q,
                    "location": loc,
                    "f_JT": "I",   # Internship
                    "f_E": "1",    # Entry level
                    "start": 0,
                }
                soup = self.fetch_html("https://www.linkedin.com/jobs/search", params=params)
                if not soup:
                    continue
                cards = soup.select("div.base-card, div.job-search-card, li.jobs-search-results__list-item")
                for card in cards[:12]:
                    try:
                        title_el = card.select_one("h3.base-search-card__title, h3.job-result-card__title")
                        company_el = card.select_one("h4.base-search-card__subtitle, a.job-result-card__company-name")
                        loc_el = card.select_one("span.job-search-card__location, span.job-result-card__location")
                        link_el = card.select_one("a.base-card__full-link, a[href*='/jobs/view/']")
                        date_el = card.select_one("time, .job-search-card__listdate")

                        title = title_el.get_text(strip=True) if title_el else ""
                        if not title or not self.is_cybersec_relevant(title):
                            continue
                        company = company_el.get_text(strip=True) if company_el else "N/A"
                        location = loc_el.get_text(strip=True) if loc_el else loc
                        href = link_el.get("href", "") if link_el else ""
                        posted = date_el.get("datetime", "") if date_el else ""

                        results.append(self.build_entry(
                            title=title, company=company, location=location,
                            url=href.split("?")[0] if href else "#",
                            description=f"Cybersecurity internship at {company} ({location})",
                            job_type="Internship", posted=posted,
                            tags=["linkedin", "cybersecurity", loc.lower()]
                        ))
                    except Exception:
                        continue
                time.sleep(random.uniform(3, 5))
        return results
