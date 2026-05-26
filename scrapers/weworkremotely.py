from .base import BaseScraper
import time

SEARCH_TERMS = ["cybersecurity", "security engineer", "infosec", "penetration testing", "SOC analyst"]

class WeWorkRemotelyScraper(BaseScraper):
    def __init__(self):
        super().__init__("WeWorkRemotely")

    def scrape(self):
        results = []
        for term in SEARCH_TERMS:
            soup = self.fetch_html("https://weworkremotely.com/remote-jobs/search",
                                   params={"term": term})
            if not soup:
                continue
            cards = soup.select("section.jobs article, ul.jobs > li, li.feature")
            for card in cards:
                try:
                    title_el = card.select_one("span.title, h2, .job-title")
                    company_el = card.select_one("span.company, .company-name")
                    region_el = card.select_one("span.region, .location, span.flag")
                    link_el = card.select_one("a[href*='/remote-jobs/']")

                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title or not self.is_cybersec_relevant(title):
                        continue

                    company = company_el.get_text(strip=True) if company_el else "N/A"
                    location = region_el.get_text(strip=True) if region_el else "Remote Worldwide"
                    href = link_el.get("href", "") if link_el else ""
                    full_url = f"https://weworkremotely.com{href}" if href.startswith("/") else href

                    results.append(self.build_entry(
                        title=title, company=company, location=location,
                        url=full_url, description=f"Remote cybersecurity role at {company}",
                        job_type="Remote", tags=["remote", "weworkremotely", "cybersecurity"]
                    ))
                except Exception:
                    continue
            time.sleep(2)
        return results
