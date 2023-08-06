from bs4 import BeautifulSoup
import urllib.request 
from urllib.parse import urlparse, urljoin
import ssl
import re
import sys
import argparse


def get_soup(url):
    # Ignore SSL certificate verification
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    response = urllib.request.urlopen(url, context=ssl_context)
    return BeautifulSoup(response, 'html.parser')


def is_relative_url(url):
    parsed_url = urlparse(url)
    return not bool(parsed_url.scheme)


def find_links(soup, pattern, domain_url):
    links = []
    for link in soup.find_all('a', href=True):
        href = link.get('href')

        # manage relative links
        if is_relative_url(href):
            href = urljoin(domain_url, href)
        
        # exclude external links
        domain = urlparse(domain_url)
        parsed_url = urlparse(href)
        if parsed_url.netloc == domain.netloc:
            links.append(href)
    return links


def list_links_with_pattern(domain_url, pattern):
    visited_urls = set()
    links_with_pattern = set()

    def crawl(url):
        if url in visited_urls:
            return
        visited_urls.add(url)
        try:
            soup = get_soup(url)
            links = find_links(soup, pattern, domain_url)
            for link in links:
                if re.search(pattern, link):
                    links_with_pattern.add(link)
                else: 
                    crawl(link)
        except Exception as e:
            print(f"Error crawling {url}: {e}")

    crawl(domain_url)
    return list(links_with_pattern)



def main(argv):
    parser = argparse.ArgumentParser(description='Crawl your website and find links by pattern')
    parser.add_argument('-u', '--url', required=True, help='website')
    parser.add_argument('-p', '--pattern', required=True, help='pattern')
    args = parser.parse_args()

    links_with_pattern = list_links_with_pattern(args.url, args.pattern)
    
    print("Links containing the text pattern:")
    for link in links_with_pattern:
        print(link)

    print("Pages found: " + str(len(links_with_pattern)))



if __name__ == "__main__":
   main(sys.argv[1:])

