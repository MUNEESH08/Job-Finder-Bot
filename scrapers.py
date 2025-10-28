import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
}

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
        for a in soup.select('a[data-jk], a.jobtitle, a.turnstileLink'):
            href = a.get('href')
            if not href:
                continue
            link = href if href.startswith('http') else 'https://www.indeed.co.in' + href
            title = a.get_text(strip=True)
            card = a.find_parent()
            company = '-'
            loc = location or '-'
            if card:
                comp = card.select_one('.company, .companyName')
                if comp: company = comp.get_text(strip=True)
                loc_tag = card.select_one('.location, .companyLocation')
                if loc_tag: loc = loc_tag.get_text(strip=True)
            results.append({
                'title': title or query,
                'company': company,
                'location': loc,
                'link': link,
                'source': 'Indeed'
            })
            if len(results) >= 20:
                break
    except Exception:
        results.append({'title': f'Indeed search: {query}', 'company': '-', 'location': location or '-', 'link': url, 'source': 'Indeed'})
    return results


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
            company = company_tag.get_text(strip=True) if company_tag else '-'
            loc_tag = t.select_one('.location')
            loc = loc_tag.get_text(strip=True) if loc_tag else (location or '-')
            salary_tag = t.select_one('.salary')
            salary = salary_tag.get_text(strip=True) if salary_tag else '-'
            results.append({
                'title': title, 'company': company, 'location': loc,
                'salary': salary, 'link': link, 'source': 'Naukri'
            })
    except Exception:
        results.append({'title': f'Naukri search: {query}', 'company': '-', 'location': location or '-', 'link': url, 'source': 'Naukri'})
    return results


def scrape_linkedin(query, location=None):
    base = 'https://www.linkedin.com/jobs/search/'
    params = f'?keywords={quote_plus(query)}'
    if location:
        params += f'&location={quote_plus(location)}'
    url = base + params
    results = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')
        for a in soup.select('a[href*="/jobs/view/"]')[:20]:
            href = a.get('href')
            link = href if href.startswith('http') else 'https://www.linkedin.com' + href
            title = a.get_text(strip=True)
            results.append({'title': title or query, 'company': '-', 'location': location or '-', 'link': link, 'source': 'LinkedIn'})
    except Exception:
        results.append({'title': f'LinkedIn search: {query}', 'company': '-', 'location': location or '-', 'link': url, 'source': 'LinkedIn (search URL)'})
    if not results:
        results.append({'title': f'LinkedIn search: {query}', 'company': '-', 'location': location or '-', 'link': url, 'source': 'LinkedIn (search URL)'})
    return results
