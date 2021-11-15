from scraping import *
from download import *

# ------------------------------------------------------


COLUMN_NAMES_PARTIES = ['Club', 'Total', 'Yes', 'No', 'Not-logged-in', 'Excused', 'Refrained']
COLUMN_NAMES_INDIVIDUALS = ['TODO']

DATA_DIR_PATH = './csv_data/'
PAGES_DIR_PATH = './pages/'

N_FILES = 100


def generate_htmls():
    for i in range(N_FILES):
        yield f'{PAGES_DIR_PATH}{i}.html'


# ------------------------------------------------------


pds = PartiesDataScrapper(generate_htmls,
                          COLUMN_NAMES_PARTIES,
                          download=True,
                          download_dir_path=DATA_DIR_PATH,
                          verbose=True,
                          n_files=N_FILES,
                          log_every=10)

for _ in pds.generate_all():
    pass
