 
import argparse
from metapub import PubMedFetcher

def fetch_article_metadata(pmid):
    # Initialize the PubMedFetcher
    fetch = PubMedFetcher()

    # Retrieve the article using the PubMed ID
    article = fetch.article_by_pmid(pmid)

    # Extract and format metadata
    first_author = str(article.author_list[0]) if article.author_list else "N/A"
    last_author = str(article.author_list[-1]) if article.author_list else "N/A"
    authors = ', '.join([str(author) for author in article.author_list]) if article.author_list else "N/A"
    mesh_tags = ', '.join(article.mesh) if article.mesh else 'N/A'
    keywords = ', '.join(article.keywords) if article.keywords else 'N/A'

    # Print metadata
    print(f"Title: {article.title}")
    print(f"First Author: {first_author}")
    print(f"Last Author: {last_author}")
    print(f"Authors: {authors}")
    print(f"Abstract: {article.abstract}")
    print(f"MESH Tags: {mesh_tags}")
    print(f"Keywords: {keywords}")
    print(f"Year of Publication: {article.year}")
    print(f"Journal: {article.journal}")

def main():
    parser = argparse.ArgumentParser(description='Fetch and display metadata for a given PubMed ID.')
    parser.add_argument('pmid', type=str, nargs='?', help='PubMed ID of the article to fetch')
    args = parser.parse_args()

    if not args.pmid:
        args.pmid = input("Please enter a PubMed ID: ")

    fetch_article_metadata(args.pmid)

if __name__ == "__main__":
    main()