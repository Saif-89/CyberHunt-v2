from .base import BaseScraper
import time

class JobicyScraper(BaseScraper):
    def __init__(self):
        super().__init__("Jobicy")

    def scrape(self):
        results = []
        # Jobicy has a real public API
        for tag in ["cybersecurity", "security", "infosec"]:
            data = self.fetch_json(
                "https://jobicy.com/api/v2/remote-jobs",
                params={"tag": tag, "count": 50}
            )
            if not data:
                continue
            jobs = data.get("jobs", []) if isinstance(data, dict) else []
            for job in jobs:
                try:
                    title = job.get("jobTitle", "")
                    if not title or not self.is_cybersec_relevant(title + " " + job.get("jobIndustry", "")):
                        continue
                    company = job.get("companyName", "N/A")
                    location = job.get("jobGeo", "Remote") or "Remote Worldwide"
                    url = job.get("url", "#")
                    desc = job.get("jobExcerpt", "")[:400]
                    salary = job.get("annualSalaryMin", "")
                    if salary and job.get("annualSalaryMax"):
                        salary = f"${salary}–${job['annualSalaryMax']} {job.get('salaryCurrency','')}"
                    posted = job.get("pubDate", "")
                    level = job.get("jobLevel", "")
                    tags = [tag, "remote", "jobicy"]
                    if level:
                        tags.append(level.lower())

                    results.append(self.build_entry(
                        title=title, company=company, location=location,
                        url=url, description=desc,
                        job_type="Remote", salary=str(salary), posted=posted,
                        tags=tags
                    ))
                except Exception:
                    continue
            time.sleep(2)
        return results
