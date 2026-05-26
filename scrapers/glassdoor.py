from .base import BaseScraper
import time, random

QUERIES = [
    "cybersecurity intern", "security analyst intern",
    "SOC analyst intern", "information security intern",
    "penetration testing intern", "network security intern"
]
LOCATIONS = ["Tunisia", "Remote", "France", "Germany", "UAE"]

class GlassdoorScraper(BaseScraper):
    def __init__(self):
        super().__init__("Glassdoor")

    def scrape(self):
        results = []
        for q in QUERIES[:4]:
            for loc in LOCATIONS[:3]:
                soup = self.fetch_html(
                    "https://www.glassdoor.com/Job/jobs.htm",
                    params={"sc.keyword": q, "locT": "N", "jobType": "internship"}
                )
                if not soup:
                    continue
                cards = soup.select("li[data-test='jobListing'], article.job-listing, div.jl")
                for card in cards[:8]:
                    try:
                        title_el = card.select_one("[data-test='job-title'], .jobLink, .job-title")
                        company_el = card.select_one("[data-test='employer-name'], .employer-name")
                        loc_el = card.select_one("[data-test='location'], .location")
                        link_el = card.select_one("a[href*='/job-listing/'], a[href*='/Jobs/']")

                        title = title_el.get_text(strip=True) if title_el else ""
                        if not title or not self.is_cybersec_relevant(title):
                            continue

                        company = company_el.get_text(strip=True) if company_el else "N/A"
                        location = loc_el.get_text(strip=True) if loc_el else loc
                        href = link_el.get("href", "") if link_el else ""
                        full_url = f"https://www.glassdoor.com{href}" if href.startswith("/") else href

                        results.append(self.build_entry(
                            title=title, company=company, location=location,
                            url=full_url,
                            description=f"Cybersecurity internship at {company}",
                            job_type="Internship",
                            tags=["glassdoor", "cybersecurity", loc.lower()]
                        ))
                    except Exception:
                        continue
                time.sleep(random.uniform(2.5, 4))
        return results
