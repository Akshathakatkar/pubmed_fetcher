import requests
import pandas as pd  
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor

query = input("Enter your PubMed search query: ").strip()

search_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmode=json&retmax=6"
search_response = requests.get(search_url)
search_data = search_response.json()

if search_response.status_code != 200:
    print(f"Error: Received status code {search_response.status_code}")
    exit() 

pmid_list = search_data['esearchresult'].get('idlist', [])

if not pmid_list:
    print("No results found for the query.")
    exit()

def fetch_pubmed_data(PMID):
    print(f"Fetching details for PMID: {PMID}...")

    esummary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={PMID}&retmode=json"
    esummary_response = requests.get(esummary_url)
    esummary_data = esummary_response.json()

    print("Raw API Response:", esummary_data)  # Debugging print

    if 'result' in esummary_data:
        pub_data = esummary_data['result'].get(PMID, {})
    else:
        print("Error: 'result' key not found in response")
        return None

    title = pub_data.get('title', 'N/A')
    pub_date = pub_data.get('pubdate', 'N/A')
    authors = [author['name'] for author in pub_data.get('authors', [])]
    last_author = pub_data.get('lastauthor', 'N/A')

    efetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={PMID}&retmode=xml"
    efetch_response = requests.get(efetch_url)
    if efetch_response.status_code != 200 or not efetch_response.text.strip():
      print(f"⚠️ Warning: Empty or invalid XML response for PMID {PMID}")
      return {
            "PubMed ID": PMID,
            "Title": title,
            "Publication Date": pub_date,
            "Authors": ", ".join(authors),
            "Last Author": last_author,
            "Affiliations": "N/A",
            "Corresponding Author Email": "N/A"
        }

    try:
        root = ET.fromstring(efetch_response.text)
    except ET.ParseError:
        print(f"❌ Error: Failed to parse XML for PMID {PMID}. Response was:\n{efetch_response.text}")
        return {
            "PubMed ID": PMID,
            "Title": title,
            "Publication Date": pub_date,
            "Authors": ", ".join(authors),
            "Last Author": last_author,
            "Affiliations": "N/A",
            "Corresponding Author Email": "N/A"
        }

    affiliations = []
    email = "N/A"

    for author in root.findall(".//Author"):
        affil = author.find("AffiliationInfo/Affiliation")
        if affil is not None:
            affiliations.append(affil.text)

        if affil is not None and "@" in affil.text:
            email = affil.text  

    return {
        "PubMed ID": PMID,
        "Title": title,
        "Publication Date": pub_date,
        "Authors": ", ".join(authors),
        "Last Author": last_author,
        "Affiliations": "; ".join(affiliations) if affiliations else "N/A",
        "Corresponding Author Email": email
    }
    

with ThreadPoolExecutor() as executor:
    results = list(executor.map(fetch_pubmed_data, pmid_list))

def save_to_csv(data, filename="pubmed_results.csv"):
    if not data:
        print("No data to save!")
        return
    
    df = pd.DataFrame(data)  # Convert JSON list to DataFrame
    df.to_csv(filename, index=False, encoding="utf-8")  # Save as CSV
    print(f"✅ Data saved to {filename}")

print("\n🔍 Debugging: Checking 'results' before saving...")
print(results)  # Print the data to check its format

if not results:
    print("⚠️ Error: No results found. Exiting...")
    exit()

# ✅ Use the function to save results instead of calling df.to_csv directly
save_to_csv(results)
