from .base import BaseScraper
import time

TAGS = ["cybersecurity", "security", "infosec", "pentest", "soc"]

class RemoteOKScraper(BaseScraper):
    def __init__(self):
        super().__init__("RemoteOK")

    def scrape(self):
        results = []
        for tag in TAGS:
            data = self.fetch_json(
                f"https://remoteok.com/api?tag={tag}",
                extra_headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
            )
            if not data or not isinstance(data, list):
                continue
            for job in data[1:]:
                try:
                    title = job.get("position", "")
                    if not title:
                        continue
                    if not self.is_cybersec_relevant(title + " " + " ".join(job.get("tags", []))):
                        continue
                    company = job.get("company", "N/A")
                    location = job.get("location", "Remote") or "Remote Worldwide"
                    url = job.get("url") or job.get("apply_url", "#")
                    desc = job.get("description", "")
                    if desc:
                        # strip HTML tags
                        from bs4 import BeautifulSoup
                        desc = BeautifulSoup(desc, "lxml").get_text()[:400]
                    salary_min = job.get("salary_min", "")
                    salary_max = job.get("salary_max", "")
                    salary = f"${salary_min}–${salary_max}" if salary_min and salary_max else ""
                    tags = job.get("tags", [])
                    results.append(self.build_entry(
                        title=title, company=company, location=location,
                        url=url, description=desc,
                        job_type="Remote", salary=salary,
                        tags=list(tags)[:6] + ["remote", "remoteok"]
                    ))
                except Exception:
                    continue
            time.sleep(2)
        return results
