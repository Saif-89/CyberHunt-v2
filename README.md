# 🔐 CyberHunt v2 — Cybersecurity Jobs Intelligence

A professional LAN-accessible web app that scrapes **10+ platforms** for cybersecurity
internships and jobs in Tunisia and remotely worldwide.

---

## 🚀 Quick Start

```bash
# 1. Install Python 3.8+
# 2. Run:
python start.py
# 3. Open: http://localhost:5050
```

That's it. `start.py` installs all dependencies automatically.

---

## 📡 Platforms Scraped

| Platform | Region | Type | Method |
|---|---|---|---|
| **Keejob** | 🇹🇳 Tunisia | Stage / CDI | HTML scrape |
| **Emploi.com.tn** | 🇹🇳 Tunisia | Stage / Emploi | HTML scrape |
| **TunisieJobs** | 🇹🇳 Tunisia | Stage / Emploi | HTML scrape |
| **RemoteOK** | 🌐 Remote | Remote | Public JSON API ✅ |
| **Jobicy** | 🌐 Remote | Remote | Public JSON API ✅ |
| **Arbeitnow** | 🌍 EU Remote | Remote / Hybrid | Public JSON API ✅ |
| **WeWorkRemotely** | 🌐 Remote | Remote | HTML scrape |
| **Indeed** | 🌍 International | Internship | HTML scrape |
| **LinkedIn** | 🌍 International | Internship | HTML scrape |
| **Adzuna** | 🇪🇺 Europe | Internship / Job | HTML scrape |
| **Glassdoor** | 🌍 International | Internship | HTML scrape |

---

## 📊 Features

- **Relevance Scoring** — every listing scored 0–10 based on cybersec keyword density
- **Smart Deduplication** — same job from multiple sources appears only once
- **Region Classification** — auto-detects Tunisia 🇹🇳 / Remote 🌐 / France 🇫🇷 / etc.
- **Analytics Dashboard** — charts for region, source, keywords, companies, timeline
- **Real-time Progress** — live badge updates per source during scraping
- **CSV + JSON Export** — export all results for offline analysis
- **Filters** — by region, source, sort (relevance / date / company)
- **Pagination** — handles large datasets cleanly
- **LAN accessible** — open on any device on your network

---

## 🔍 Cybersecurity Keywords Searched

```
cybersecurity, pentest, SOC, SIEM, infosec, network security,
cloud security, appsec, DevSecOps, GRC, malware analyst,
threat intelligence, forensics, red team, blue team,
vulnerability, incident response, IAM, cryptography,
bug bounty, ethical hacking, CTF, OSINT, reverse engineering,
securite informatique, analyste securite, reseau securite ...
```

---

## 🗂 Project Structure

```
cyberhunt-v2/
├── app.py                  # Flask server + API
├── start.py                # Auto-install + launch
├── requirements.txt
├── data/
│   └── jobs.json           # Scraped results (auto-created)
├── templates/
│   └── index.html          # Full dashboard UI
└── scrapers/
    ├── engine.py           # Orchestrator + scoring + dedup
    ├── base.py             # Base class + helpers
    ├── keejob.py
    ├── emploi_tn.py
    ├── tunisie_jobs.py
    ├── remoteok.py         # Public API
    ├── jobicy.py           # Public API
    ├── arbeitnow.py        # Public API
    ├── weworkremotely.py
    ├── indeed.py
    ├── linkedin.py
    ├── adzuna.py
    └── glassdoor.py
```

---

## ⚠️ Notes

- Scraping LinkedIn/Indeed/Glassdoor may return 0 results sometimes due to bot
  detection. The 3 public APIs (RemoteOK, Jobicy, Arbeitnow) always work reliably.
- For best Tunisia results: Keejob, Emploi.com.tn, TunisieJobs are most reliable.
- Run scrapes periodically (weekly) to keep data fresh.
- Data persists in `data/jobs.json` between runs.

---

## 🔧 Advanced

To scrape only specific sources, use the **Scrape Control** tab in the UI
and select individual platforms before hitting HUNT.

To access from another device on your LAN:
1. Find your IP: `ipconfig` (Windows) or `ip a` (Linux)
2. Open `http://<your-ip>:5050` on any device

---

Made for cybersecurity students in Tunisia hunting their next internship. 🛡️
