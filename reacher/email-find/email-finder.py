import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def find_website(name):
    query = name + " official website"
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    for link in soup.find_all("a", href=True):
        url_match = re.search(r"https?://(www\.)?([a-zA-Z0-9-]+)\.[a-z]{2,}", link["href"])
        if url_match:
            return url_match.group(0)  # Return first valid URL
    return "Website not found"

email_list = ["info", "hr", "jobs", "careers", "humanresources", "recruitment", "hiring", "talent", "recruiter", "apply",
              "talent", "talentacquisition", "joinus", "opportunities", "workwithus", "recruit", "campushiring", "internships",
              "earlycareers", "techrecruitment", "staffing", "jobopenings", "careeropportunities", "employment", "nowhiring",
              "team", "wearehiring", "diversityhiring", "dei.recruitment", "headhunting", "specializedhiring"]

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

def scrape_emails(url, visited=set(), emails=set()):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        base_url = "{0.scheme}://{0.netloc}".format(urlparse(url))

        # Extract and store emails from the page
        page_emails = set(re.findall(EMAIL_REGEX, response.text))
        if page_emails:
            print(f"Emails found on {url}: {page_emails}")
            valid_emails = []
            for email in page_emails:
                front = email.split("@")[0]
                if front in email_list:
                    valid_emails.append(email)
            emails.update(valid_emails)

        # Extract internal links and visit them recursively
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            full_url = urljoin(base_url, href)
            parsed_url = urlparse(full_url)

            # Ensure it's an internal link and hasn't been visited
            if parsed_url.netloc == urlparse(url).netloc and full_url not in visited:
                visited.add(full_url)
                print(f"Visiting: {full_url}")
                scrape_emails(full_url, visited, emails)

    except Exception as e:
        print(f"Error visiting {url}: {e}")


# start_url = "https://example.com" 
# found_emails = set()
# scrape_emails(start_url, emails=found_emails)

# print("\nAll collected emails:")
# for email in found_emails:
#     print(email)

print(find_website("Algebris"))