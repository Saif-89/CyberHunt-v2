from .base import BaseScraper
import time

class ArbeitnowScraper(BaseScraper):
    def __init__(self):
        super().__init__("Arbeitnow")

    def scrape(self):
        results = []
        # Arbeitnow has a real public JSON API - great for remote + EU jobs
        for page in range(1, 4):
            data = self.fetch_json(
                "https://www.arbeitnow.com/api/job-board-api",
                params={"page": page}
            )
            if not data:
                break
            jobs = data.get("data", [])
            if not jobs:
                break
            for job in jobs:
                try:
                    title = job.get("title", "")
                    desc_raw = job.get("description", "")
                    tags = job.get("tags", [])
                    combined = title + " " + " ".join(tags) + " " + desc_raw[:300]
                    if not self.is_cybersec_relevant(combined):
                        continue
                    company = job.get("company_name", "N/A")
                    location = job.get("location", "Remote / EU") or "Remote / EU"
                    url = job.get("url", "#")
                    remote = job.get("remote", False)
                    job_type = "Remote" if remote else "On-site / Hybrid"
                    posted = job.get("created_at", "")
                    from bs4 import BeautifulSoup
                    desc = BeautifulSoup(desc_raw, "lxml").get_text()[:400] if desc_raw else ""

                    results.append(self.build_entry(
                        title=title, company=company, location=location,
                        url=url, description=desc,
                        job_type=job_type, posted=str(posted),
                        tags=list(tags)[:5] + ["arbeitnow", "eu"]
                    ))
                except Exception:
                    continue
            time.sleep(1.5)
        return results
