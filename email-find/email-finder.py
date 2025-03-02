import requests
from bs4 import BeautifulSoup
import re
from googlesearch import search
from urllib.parse import urljoin, urlparse
import warnings
from urllib3.exceptions import InsecureRequestWarning
import csv
from collections import defaultdict

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

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zAZ]{2,}"

def scrape_emails(url, visited=set(), emails=set(), csv_writer=None, company_name="", same_pages=defaultdict(int)):
    try:

        response = requests.get(url, timeout=5, verify=False)
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

            if valid_emails:
                print(f"Found matching recruiting/career email: {valid_emails}")
                # Write to CSV as soon as we find a valid email
                csv_writer.writerow([company_name, valid_emails[0]])
                

        # Extract internal links and visit them recursively
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            full_url = urljoin(base_url, href)
            parsed_url = urlparse(full_url)
            subheading = full_url.split('/')[3] if len(full_url.split('/')) > 4 else full_url
            # Ensure it's an internal link and hasn't been visited


            if parsed_url.netloc == urlparse(url).netloc and full_url not in visited and same_pages[subheading] <= 10:
                visited.add(full_url)
                same_pages[subheading] += 1
                print(f"Visiting: {full_url}")
                scrape_emails(full_url, visited, emails, csv_writer, company_name)

    except Exception as e:
        print(f"Error visiting {url}: {e}")

def process_companies(companies_file, output_csv):
    with open(companies_file, 'r') as file:
        companies = file.readlines()

    # Open CSV file for writing at the start of processing
    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Company Name", "Recruiting Email"])

        for company_name in companies:
            company_name = company_name.strip()  # Clean up the name
            print(f"Processing {company_name}...")

            start_url = get_company_website(company_name)

            if start_url:
                print(f"Found website: {start_url}")
                found_emails = set()
                scrape_emails(start_url, emails=found_emails, csv_writer=writer, company_name=company_name)
            else:
                print(f"Could not find the website for {company_name}.")
                # If no website is found, write empty email to the CSV
                writer.writerow([company_name, ""])

    print(f"Results saved to {output_csv}")

# Example usage:
process_companies('companies.txt', 'company_emails.csv')
