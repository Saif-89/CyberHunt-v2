from .base import BaseScraper
import time, random

QUERIES = [
    "cybersecurity", "cyber-securite", "securite-informatique",
    "securite-reseau", "SOC", "pentest", "analyste-securite",
    "informatique-securite", "reseau-securite"
]

class KeejobScraper(BaseScraper):
    def __init__(self):
        super().__init__("Keejob")

    def scrape(self):
        results = []
        for q in QUERIES:
            for contract in ["stage", "cdi", "cdd"]:
                url = "https://www.keejob.com/offres-emploi/"
                params = {"keywords": q, "contract": contract}
                soup = self.fetch_html(url, params=params)
                if not soup:
                    continue
                cards = soup.select("div.offer-description, div.offer, article.offer, li.offer-item")
                for card in cards:
                    try:
                        title_el = card.select_one("h2 a, h3 a, .offer-title a, a.title")
                        company_el = card.select_one(".company-name, .employer, .company, span.company")
                        loc_el = card.select_one(".location, .city, .ville, span.location")
                        desc_el = card.select_one(".description, .resume, p.desc, .summary")
                        date_el = card.select_one(".date, .posted, time, .date-posted")

                        title = title_el.get_text(strip=True) if title_el else ""
                        if not title:
                            continue
                        if not self.is_cybersec_relevant(title + (desc_el.get_text() if desc_el else "")):
                            continue

                        href = title_el.get("href", "") if title_el else ""
                        full_url = f"https://www.keejob.com{href}" if href.startswith("/") else href
                        company = company_el.get_text(strip=True) if company_el else "N/A"
                        location = loc_el.get_text(strip=True) if loc_el else "Tunisia"
                        desc = desc_el.get_text(strip=True)[:400] if desc_el else ""
                        posted = date_el.get_text(strip=True) if date_el else ""
                        jtype = "Stage" if contract == "stage" else ("CDI" if contract == "cdi" else "CDD")

                        results.append(self.build_entry(
                            title=title, company=company,
                            location=location or "Tunisia",
                            url=full_url, description=desc,
                            job_type=jtype, posted=posted,
                            tags=["tunisia", "keejob", q]
                        ))
                    except Exception:
                        continue
                time.sleep(random.uniform(1.5, 3))
        return results
