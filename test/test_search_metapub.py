import argparse
import logging
from metapub import PubMedFetcher
NCBI_API_KEY="XXXX"
# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def search_with_dictionary(params):
    fetch = PubMedFetcher()
    logger.debug(f"Searching with dictionary parameters: {params}")
    # Perform search using dictionary parameters
    pmids_dict = fetch.pmids_for_query(**params)
    return pmids_dict

def search_with_query_string(query):
    fetch = PubMedFetcher()
    logger.debug(f"Searching with query string: {query}")
    # Perform search using query string
    pmids_query = fetch.pmids_for_query(query)
    return pmids_query

def main():
    parser = argparse.ArgumentParser(description='Search PubMed using dictionary parameters.')
    parser.add_argument('--journal', type=str, help='Journal name')
    parser.add_argument('--author1', type=str, help='First author')
    parser.add_argument('--year', type=str, help='Year of publication')
    parser.add_argument('--keyword', type=str, help='Keyword')
    parser.add_argument('--query', type=str, help='Traditional PubMed query string')
    args = parser.parse_args()

    params = {}
    if args.journal:
        params['journal'] = args.journal
    if args.author1:
        params['first author'] = args.author1
    if args.year:
        params['year'] = args.year
    if args.keyword:
        params['keyword'] = args.keyword

    if args.query:
        pmids_query = search_with_query_string(args.query)
        logger.info(f"PMIDs from query string: {pmids_query}")

    if params:
        pmids_dict = search_with_dictionary(params)
        logger.info(f"PMIDs from dictionary: {pmids_dict}")

if __name__ == "__main__":
    main()

# python test_search_metapub.py --journal "Journal of Clinical Oncology" --keyword "leukemia"