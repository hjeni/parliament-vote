from scraping import *
from download import *

# ------------------------------------------------------


COLUMN_NAMES_PARTIES = ['Club', 'Total', 'Yes', 'No', 'Not-logged-in', 'Excused', 'Refrained']
COLUMN_NAMES_INDIVIDUALS = ['TODO']

DATA_DIR_PATH = './csv_data/'
PAGES_DIR_PATH = './pages/'

N_FILES = 100


def generate_html_files():
    for i in range(N_FILES):
        yield f'{PAGES_DIR_PATH}{i}.html'


# ------------------------------------------------------


parties_scrapper = PartiesDataScrapper(generate_html_files,
                                       COLUMN_NAMES_PARTIES,
                                       download=True,
                                       download_dir_path=DATA_DIR_PATH + 'parties/',
                                       verbose=True,
                                       log_every=10,
                                       n_files=N_FILES)
for _ in parties_scrapper.generate_all():
    pass








