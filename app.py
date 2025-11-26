from flask import Flask, request, jsonify, render_template
from scrapers import scrape_indeed, scrape_naukri, scrape_linkedin
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.get_json()

    if not data or not data.get('skill'):
        return jsonify({"error": "Missing required parameter: skill"}), 400

    skills = data['skill']
    location = data.get('location', '')
    min_salary = data.get('min_salary', 0)
    max_count = int(data.get('max_count', 15))
    sites = data.get('sites', 'all')

    query = ' '.join([s.strip() for s in skills.split(',') if s.strip()])
    jobs = []

    if sites in ('all', 'indeed'):
        jobs.extend(scrape_indeed(query, location))
        time.sleep(1)

    if sites in ('all', 'naukri'):
        jobs.extend(scrape_naukri(query, location))
        time.sleep(1)

    if sites in ('all', 'linkedin'):
        jobs.extend(scrape_linkedin(query, location))

    # Salary filtering
    filtered_jobs = []
    for job in jobs:
        salary_text = job.get('salary', '')
        try:
            numeric = int(''.join([c for c in salary_text if c.isdigit()]) or 0)
            if numeric < min_salary:
                continue
        except:
            pass
        filtered_jobs.append(job)

    # De-duplicate
    seen = set()
    unique_jobs = []
    for j in filtered_jobs:
        link = j.get('link')
        if not link or link in seen:
            continue
        seen.add(link)
        unique_jobs.append(j)

    unique_jobs = unique_jobs[:max_count]

    return jsonify({
        "query": query,
        "location": location,
        "count": len(unique_jobs),
        "jobs": unique_jobs
    })


if __name__ == '__main__':
    app.run(debug=True)
