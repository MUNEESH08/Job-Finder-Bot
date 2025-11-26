import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
}

# -------------------- INDEED SCRAPER --------------------
def scrape_indeed(query, location=None):
    results = []
    base = 'https://www.indeed.co.in/jobs'
    params = f'?q={quote_plus(query)}'
    if location:
        params += f'&l={quote_plus(location)}'
    url = base + params

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')

        for card in soup.select('div.job_seen_beacon')[:20]:
            title = card.select_one('h2.jobTitle')
            company = card.select_one('.companyName')
            loc_tag = card.select_one('.companyLocation')
            link_tag = card.select_one('a')

            if not link_tag:
                continue

            link = link_tag.get('href')
            if link and not link.startswith('http'):
                link = "https://www.indeed.co.in" + link

            results.append({
                'title': title.get_text(strip=True) if title else query,
                'company': company.get_text(strip=True) if company else "-",
                'location': loc_tag.get_text(strip=True) if loc_tag else (location or "-"),
                'salary': "-",
                'link': link,
                'source': 'Indeed'
            })

    except Exception:
        results.append({'title': f'Indeed search: {query}', 'company': '-', 
                        'location': location or '-', 'link': url, 'source': 'Indeed'})

    return results


# -------------------- NAUKRI SCRAPER --------------------
def scrape_naukri(query, location=None):
    results = []
    base = 'https://www.naukri.com/search'
    params = f'?q={quote_plus(query)}'
    if location:
        params += f'&l={quote_plus(location)}'

    url = base + params

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')

        tuples = soup.select('.jobTuple')
        for t in tuples[:20]:
            link_tag = t.select_one('a[href]')
            if not link_tag:
                continue

            link = link_tag.get('href')
            title = link_tag.get_text(strip=True)
            company_tag = t.select_one('.company, .companyInfo')
            loc_tag = t.select_one('.location')
            salary_tag = t.select_one('.salary')

            results.append({
                'title': title,
                'company': company_tag.get_text(strip=True) if company_tag else '-',
                'location': loc_tag.get_text(strip=True) if loc_tag else (location or '-'),
                'salary': salary_tag.get_text(strip=True) if salary_tag else '-',
                'link': link,
                'source': 'Naukri'
            })

    except Exception:
        results.append({'title': f'Naukri search: {query}', 'company': '-', 
                        'location': location or '-', 'link': url, 'source': 'Naukri'})

    return results


# ------------------ LINKEDIN SCRAPER (FIXED) ------------------
# Uses the LinkedIn public "seeMoreJobPostings" API
def scrape_linkedin(query, location=None):
    q = quote_plus(query)
    loc = quote_plus(location or "")

    url = (
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        f"?keywords={q}&location={loc}"
    )

    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)

        soup = BeautifulSoup(r.text, "lxml")

        for job in soup.select("li")[:20]:
            title = job.select_one("h3").get_text(strip=True) if job.select_one("h3") else "-"
            company = job.select_one("h4").get_text(strip=True) if job.select_one("h4") else "-"
            link_tag = job.select_one("a")

            if not link_tag:
                continue

            link = "https://www.linkedin.com" + link_tag.get('href')

            results.append({
                "title": title,
                "company": company,
                "location": location or "-",
                "salary": "-",
                "link": link,
                "source": "LinkedIn"
            })

    except Exception:
        results.append({
            "title": f"LinkedIn search: {query}",
            "company": "-",
            "location": location or "-",
            "salary": "-",
            "link": url,
            "source": "LinkedIn"
        })

    return results
