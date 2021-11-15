from scraping import *
from download import *

# ------------------------------------------------------


COLUMN_NAMES_PARTIES = ['Club', 'Total', 'Yes', 'No', 'Not-logged-in', 'Excused', 'Refrained']
COLUMN_NAMES_INDIVIDUALS = ['TODO']

DATA_DIR_PATH = './csv_data/'
PAGES_DIR_PATH = './pages/'


def generate_htmls():
    for i in range(20):
        yield f'{PAGES_DIR_PATH}{i}.html'


# ------------------------------------------------------


pds = PartiesDataScrapper(generate_htmls,
                          COLUMN_NAMES_PARTIES,
                          download=True,
                          download_dir_path=DATA_DIR_PATH,
                          verbose=True,
                          n_files=10,
                          log_every=1)

for _ in pds.generate_all():
    pass
