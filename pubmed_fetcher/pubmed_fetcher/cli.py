import argparse
from fetch import fetch_pubmed_data, save_to_csv  # Import your functions

def main():
    parser = argparse.ArgumentParser(description="Fetch PubMed data and save as CSV.")
    parser.add_argument("query", type=str, help="Search query for PubMed API")
    parser.add_argument("--output", type=str, default="pubmed_results.csv", help="Output CSV file name")

    args = parser.parse_args()
    
    print(f"🔍 Fetching PubMed data for query: {args.query}...")
    results = fetch_pubmed_data(args.query)  # Call your function

    if results:
        save_to_csv(results, args.output)  # Save data to CSV
    else:
        print("⚠️ No results found!")

if __name__ == "__main__":
    main()
