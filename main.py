from scraping import *
from download import *


# ----------------------------------------------------------------------

def gen_html_test():
    for i in range(10):
        yield f'https://www.psp.cz/sqw/hlasy.sqw?g={67260 + i}&l=cz'


URL_PREFIX = 'https://www.psp.cz/sqw/hlasy.sqw?g='
URL_SUFIX = '&l=cz'
ID_FIRST = 67018


def generate_urls(first, last):
    """
    Generates all URLs with parliament voting results
    """
    for page_id in range(first, last):
        yield f'{URL_PREFIX}{page_id}{URL_SUFIX}'

# ----------------------------------------------------------------------


test_dir = '_pages_test/'

hpd = HtmlPagesDownloader(test_dir, verbose=True, log_every=1)
hpd.download(generate_urls(ID_FIRST, ID_FIRST + 10), n_pages=10)
