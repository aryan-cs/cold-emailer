import requests
from bs4 import BeautifulSoup
import re
from googlesearch import search
from urllib.parse import urljoin, urlparse
import warnings
from urllib3.exceptions import InsecureRequestWarning
import csv

warnings.simplefilter('ignore', InsecureRequestWarning)

def get_company_website(company_name):
    query = f'{company_name} official website'
    # Perform a Google search and get the first result URL
    search_results = search(query, num_results=1)
    return next(search_results, None)

email_list = ["info", "hr", "jobs", "careers", "humanresources", "recruitment", "hiring", "talent", "recruiter", "apply",
              "talent", "talentacquisition", "joinus", "opportunities", "workwithus", "recruit", "campushiring", "internships",
              "earlycareers", "techrecruitment", "staffing", "jobopenings", "careeropportunities", "employment", "nowhiring",
              "team", "wearehiring", "diversityhiring", "dei.recruitment", "headhunting", "specializedhiring"]

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

def find_careers_page(url):
    try:
        response = requests.get(url, timeout=5, verify=False)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        base_url = "{0.scheme}://{0.netloc}".format(urlparse(url))

        # Keywords to look for in the link text or URL
        careers_keywords = ["careers", "jobs", "join-us", "work-with-us", "opportunities", "hiring", "recruitment"]

        for link in soup.find_all('a', href=True):
            href = link.get('href')
            link_text = link.text.lower()
            full_url = urljoin(base_url, href)

            # Check if the link text or URL contains any of the careers keywords
            if any(keyword in link_text or keyword in full_url for keyword in careers_keywords):
                return full_url

    except Exception as e:
        print(f"Error visiting {url}: {e}")
    
    return None

def scrape_emails_from_page(url):
    try:
        response = requests.get(url, timeout=5, verify=False)
        if response.status_code != 200:
            return set()
        
        # Extract emails using regex
        page_emails = set(re.findall(EMAIL_REGEX, response.text))
        valid_emails = set()

        for email in page_emails:
            front = email.split("@")[0]
            if front in email_list:
                valid_emails.add(email)
        
        return valid_emails

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return set()

def process_companies(companies_file):
    with open(companies_file, 'r') as file:
        companies = file.readlines()

    # Open CSV file for writing at the start of processing
    with open('company_emails.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Company Name", "Recruiting Email"])

    for company_name in companies:
        company_name = company_name.strip()  # Clean up the name
        print(f"Processing {company_name}...")

        start_url = get_company_website(company_name)

        if start_url:
            print(f"Found website: {start_url}")
            careers_page = find_careers_page(start_url)
            
            if careers_page:
                print(f"Found Careers/Jobs page: {careers_page}")
                emails = scrape_emails_from_page(careers_page)
                
                if emails:
                    print(f"Found recruiting/career emails: {emails}")
                    # Write the first valid email to the CSV
                    with open('company_emails.csv', 'a', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([company_name, list(emails)[0]])
                else:
                    print(f"No valid recruiting emails found on the Careers/Jobs page.")
                    # Write empty email to the CSV
                    with open('company_emails.csv', 'a', newline='', encoding='utf-8') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([company_name, ""])
            else:
                print(f"Could not find the Careers/Jobs page for {company_name}.")
                # Write empty email to the CSV
                with open('company_emails.csv', 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([company_name, ""])
        else:
            print(f"Could not find the website for {company_name}.")
            # Write empty email to the CSV
            with open('company_emails.csv', 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([company_name, ""])

    print(f"Results saved to company_emails.csv")

# Example usage:
process_companies('companies.txt')