from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import threading, json, os, logging
from datetime import datetime
from scrapers.engine import Engine, SCRAPERS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
app = Flask(__name__)
CORS(app)

DATA_FILE = "data/jobs.json"
engine = Engine(DATA_FILE)
PROGRESS = {"status": "idle", "message": "Ready", "progress": 0, "total": 0, "completed": 0}

def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/jobs")
def get_jobs():
    data = load()
    q = request.args.get("q", "").lower().strip()
    source = request.args.get("source", "all").lower()
    region = request.args.get("region", "all")
    jtype = request.args.get("type", "all")
    sort = request.args.get("sort", "relevance")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 24))

    if q:
        data = [d for d in data if q in (d.get("title","") + d.get("company","") + d.get("description","") + " ".join(d.get("tags",[]))).lower()]
    if source != "all":
        data = [d for d in data if source in d.get("source","").lower()]
    if region != "all":
        data = [d for d in data if region.lower() in d.get("region","").lower()]
    if jtype != "all":
        data = [d for d in data if jtype.lower() in d.get("type","").lower()]

    if sort == "relevance":
        data.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    elif sort == "date":
        data.sort(key=lambda x: x.get("scraped_at", ""), reverse=True)
    elif sort == "company":
        data.sort(key=lambda x: x.get("company", "").lower())

    total = len(data)
    start = (page - 1) * per_page
    page_data = data[start:start + per_page]
    return jsonify({"jobs": page_data, "total": total, "page": page, "pages": (total + per_page - 1) // per_page})

@app.route("/api/analytics")
def analytics():
    data = load()
    if not data:
        return jsonify({})

    # Source breakdown
    sources = {}
    for d in data:
        s = d.get("source", "Unknown")
        sources[s] = sources.get(s, 0) + 1

    # Region breakdown
    regions = {}
    for d in data:
        r = d.get("region", "International 🌍")
        regions[r] = regions.get(r, 0) + 1

    # Type breakdown
    types = {}
    for d in data:
        t = d.get("type", "Other")
        types[t] = types.get(t, 0) + 1

    # Top companies
    companies = {}
    for d in data:
        c = d.get("company", "N/A")
        if c and c != "N/A":
            companies[c] = companies.get(c, 0) + 1
    top_companies = sorted(companies.items(), key=lambda x: x[1], reverse=True)[:10]

    # Relevance distribution
    scores = [d.get("relevance_score", 0) for d in data]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    high_rel = len([s for s in scores if s >= 6])
    med_rel = len([s for s in scores if 3 <= s < 6])
    low_rel = len([s for s in scores if s < 3])

    # Keyword frequency in titles
    from collections import Counter
    kw_counter = Counter()
    kws = ["pentest", "SOC", "cloud", "network", "forensics", "malware",
           "devSecOps", "GRC", "appsec", "SIEM", "IAM", "red team", "blue team",
           "threat", "vulnerability", "incident", "compliance", "cryptography"]
    for d in data:
        text = (d.get("title","") + " " + d.get("description","")).lower()
        for kw in kws:
            if kw.lower() in text:
                kw_counter[kw] += 1

    # Timeline (by scrape date)
    timeline = {}
    for d in data:
        dt = d.get("scraped_at", "")[:10]
        if dt:
            timeline[dt] = timeline.get(dt, 0) + 1
    timeline_sorted = [{"date": k, "count": v} for k, v in sorted(timeline.items())]

    last_updated = max((d.get("scraped_at","") for d in data), default="Never")

    return jsonify({
        "total": len(data),
        "sources": sources,
        "regions": regions,
        "types": types,
        "top_companies": [{"name": k, "count": v} for k, v in top_companies],
        "relevance": {"high": high_rel, "medium": med_rel, "low": low_rel, "avg": avg_score},
        "keywords": [{"kw": k, "count": v} for k, v in kw_counter.most_common(12)],
        "timeline": timeline_sorted,
        "last_updated": last_updated,
    })

@app.route("/api/scrape", methods=["POST"])
def start_scrape():
    global PROGRESS
    if PROGRESS.get("status") == "running":
        return jsonify({"error": "Scrape already running"}), 400
    sources = request.json.get("sources", ["all"])
    PROGRESS = {"status": "running", "message": "Initializing...", "progress": 0, "total": 0, "completed": 0}
    def run():
        global PROGRESS
        try:
            engine.run(sources, PROGRESS)
        except Exception as e:
            PROGRESS["status"] = "error"
            PROGRESS["message"] = str(e)
    t = threading.Thread(target=run, daemon=True)
    t.start()
    return jsonify({"ok": True})

@app.route("/api/progress")
def progress():
    return jsonify(PROGRESS)

@app.route("/api/sources")
def get_sources():
    return jsonify({"sources": list(SCRAPERS.keys())})

@app.route("/api/clear", methods=["POST"])
def clear():
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    return jsonify({"ok": True})

@app.route("/api/export")
def export():
    data = load()
    fmt = request.args.get("format", "json")
    if fmt == "csv":
        import csv, io
        out = io.StringIO()
        if data:
            writer = csv.DictWriter(out, fieldnames=data[0].keys())
            writer.writeheader()
            for row in data:
                row2 = {k: (", ".join(v) if isinstance(v, list) else v) for k, v in row.items()}
                writer.writerow(row2)
        from flask import Response
        return Response(out.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition": "attachment;filename=cybersec-jobs.csv"})
    return jsonify(data)

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    print("\n" + "═"*50)
    print("  🔐  CyberHunt v2 — Internship Intelligence")
    print("═"*50)
    print(f"  🌐  http://0.0.0.0:5050  (LAN accessible)")
    print(f"  📡  {len(SCRAPERS)} scrapers loaded")
    print("═"*50 + "\n")
    app.run(host="0.0.0.0", port=5050, debug=False, threaded=True)
