from bs4 import BeautifulSoup

# Read HTML content from input.txt
with open("input.txt", "r", encoding="utf-8") as file:
    html_content = file.read()

# Parse HTML using BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Extract company names from div elements with class "select__option"
company_names = [div.text.strip() for div in soup.find_all("div", class_="select__option")]

# Write extracted company names to output.txt
with open("output.txt", "w", encoding="utf-8") as output_file:
    for name in company_names:
        output_file.write(name + "\n")

print("Company names saved to output.txt")
