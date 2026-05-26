from .base import BaseScraper
import time, random

# Adzuna has a public API - use the search page as fallback
QUERIES = [
    "cybersecurity intern", "security analyst intern",
    "SOC intern", "penetration testing", "information security"
]

class AdzunaScraper(BaseScraper):
    def __init__(self):
        super().__init__("Adzuna")

    def _scrape_country(self, country_code, country_name, query):
        results = []
        for page in range(1, 3):
            url = f"https://www.adzuna.{country_code}/search"
            params = {
                "q": query,
                "p": page,
                "w": "internship OR stage OR intern",
            }
            soup = self.fetch_html(url, params=params)
            if not soup:
                break
            cards = soup.select("article.result, div[data-aid], li.result")
            if not cards:
                break
            for card in cards:
                try:
                    title_el = card.select_one("h2 a, h3 a, [class*='title'] a")
                    company_el = card.select_one("[class*='company'], [class*='employer']")
                    loc_el = card.select_one("[class*='location'], [class*='location']")
                    desc_el = card.select_one("[class*='description'], p")
                    salary_el = card.select_one("[class*='salary'], [class*='wage']")

                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title or not self.is_cybersec_relevant(title + (desc_el.get_text() if desc_el else "")):
                        continue
                    href = title_el.get("href", "") if title_el else ""
                    full_url = href if href.startswith("http") else f"https://www.adzuna.{country_code}{href}"
                    company = company_el.get_text(strip=True) if company_el else "N/A"
                    location = loc_el.get_text(strip=True) if loc_el else country_name
                    desc = desc_el.get_text(strip=True)[:400] if desc_el else ""
                    salary = salary_el.get_text(strip=True) if salary_el else ""

                    results.append(self.build_entry(
                        title=title, company=company, location=location,
                        url=full_url, description=desc,
                        job_type="Internship / Job", salary=salary,
                        tags=["adzuna", "cybersecurity", country_name.lower()]
                    ))
                except Exception:
                    continue
            time.sleep(random.uniform(2, 3))
        return results

    def scrape(self):
        results = []
        countries = [
            ("fr", "France"), ("de", "Germany"), ("co.uk", "UK"),
            ("com.au", "Australia"), ("ca", "Canada"),
        ]
        for q in QUERIES[:3]:
            for code, name in countries[:3]:
                results.extend(self._scrape_country(code, name, q))
        return results
