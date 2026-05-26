from .base import BaseScraper
import time, random

QUERIES = [
    "cybersecurity", "securite-informatique", "securite-reseau",
    "SOC", "pentest", "analyste-securite", "reseau"
]

class EmploiScraper(BaseScraper):
    def __init__(self):
        super().__init__("Emploi.com.tn")

    def scrape(self):
        results = []
        for q in QUERIES:
            for path in [f"/offres-emploi-tunisie/{q}/stage/", f"/offres-emploi-tunisie/{q}/"]:
                soup = self.fetch_html(f"https://www.emploi.com.tn{path}")
                if not soup:
                    # try with query param
                    soup = self.fetch_html("https://www.emploi.com.tn/offres-emploi-tunisie/",
                                           params={"q": q, "type": "stage"})
                if not soup:
                    continue
                cards = soup.select("div.offer, article.job, li.offer-item, div.job-offer, div[class*='offer']")
                for card in cards:
                    try:
                        title_el = card.select_one("h2 a, h3 a, .offer-title a, a.job-title")
                        company_el = card.select_one(".company, .employer, .company-name")
                        loc_el = card.select_one(".location, .ville, .city, .job-location")
                        desc_el = card.select_one(".description, .summary, p.desc")
                        date_el = card.select_one(".date, time, .posted-date")

                        title = title_el.get_text(strip=True) if title_el else ""
                        if not title:
                            continue
                        if not self.is_cybersec_relevant(title + (desc_el.get_text() if desc_el else "")):
                            continue

                        href = title_el.get("href", "") if title_el else ""
                        full_url = href if href.startswith("http") else f"https://www.emploi.com.tn{href}"
                        company = company_el.get_text(strip=True) if company_el else "N/A"
                        location = loc_el.get_text(strip=True) if loc_el else "Tunisia"
                        desc = desc_el.get_text(strip=True)[:400] if desc_el else ""
                        posted = date_el.get_text(strip=True) if date_el else ""

                        results.append(self.build_entry(
                            title=title, company=company,
                            location=location or "Tunisia",
                            url=full_url, description=desc,
                            job_type="Stage / Emploi", posted=posted,
                            tags=["tunisia", "emploi.com.tn", q]
                        ))
                    except Exception:
                        continue
                time.sleep(random.uniform(1.5, 3))
        return results
