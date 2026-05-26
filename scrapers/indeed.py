from .base import BaseScraper
import time, random

QUERIES = [
    "cybersecurity intern", "cyber security internship",
    "information security intern", "SOC analyst intern",
    "network security internship", "penetration testing intern",
    "security engineer intern", "DevSecOps intern",
    "securite informatique stage", "analyste securite stage"
]
LOCATIONS = [
    ("Tunisia", "tn.indeed.com"), ("Tunis", "tn.indeed.com"),
    ("Remote", "www.indeed.com"), ("Paris", "www.indeed.com"),
    ("Dubai", "www.indeed.com"), ("Germany", "www.indeed.com"),
    ("Canada", "ca.indeed.com"),
]

class IndeedScraper(BaseScraper):
    def __init__(self):
        super().__init__("Indeed")

    def scrape(self):
        results = []
        for q in QUERIES[:5]:
            for loc, domain in LOCATIONS[:5]:
                base = f"https://{domain}/jobs"
                soup = self.fetch_html(base, params={"q": q, "l": loc, "fromage": "30"})
                if not soup:
                    continue
                cards = soup.select("div.job_seen_beacon, div.tapItem, div.slider_item, div.result")
                for card in cards[:8]:
                    try:
                        title_el = card.select_one("h2.jobTitle span[title], h2.jobTitle a span, h2 span[id]")
                        company_el = card.select_one("span.companyName, [data-testid='company-name'], .companyInfo span")
                        loc_el = card.select_one("div.companyLocation, [data-testid='text-location'], .companyLocation")
                        link_el = card.select_one("a[id^='job_'], a.jcs-JobTitle, h2 a")
                        snippet_el = card.select_one("div.job-snippet ul, div.job-snippet, .summary")
                        salary_el = card.select_one(".salary-snippet, .estimated-salary, [data-testid='attribute_snippet_testid']")
                        date_el = card.select_one(".date, [data-testid='myJobsStateDate'], span.date")

                        title = title_el.get_text(strip=True) if title_el else ""
                        if not title:
                            continue
                        if not self.is_cybersec_relevant(title + " " + (snippet_el.get_text() if snippet_el else "")):
                            continue

                        company = company_el.get_text(strip=True) if company_el else "N/A"
                        location = loc_el.get_text(strip=True) if loc_el else loc
                        href = link_el.get("href", "") if link_el else ""
                        full_url = f"https://{domain}{href}" if href.startswith("/") else href
                        desc = snippet_el.get_text(strip=True)[:400] if snippet_el else ""
                        salary = salary_el.get_text(strip=True) if salary_el else ""
                        posted = date_el.get_text(strip=True) if date_el else ""

                        results.append(self.build_entry(
                            title=title, company=company, location=location,
                            url=full_url, description=desc,
                            job_type="Internship", salary=salary, posted=posted,
                            tags=["indeed", "cybersecurity", loc.lower()]
                        ))
                    except Exception:
                        continue
                time.sleep(random.uniform(2, 4))
        return results
