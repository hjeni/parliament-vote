from scraping import *


# ----------------------------------------------------------------------

def gen_test():
    for i in range(10):
        yield f'./pages/{67260 + i}.html'


COLUMN_NAMES_PARTIES = ['Club', 'Total', 'Yes', 'No', 'Not-logged-in', 'Excused', 'Refrained']
COLUMN_NAMES_INDIVIDUALS = ['TODO']

# ----------------------------------------------------------------------

pds = ParlDataScrapper(gen_test, COLUMN_NAMES_PARTIES, COLUMN_NAMES_INDIVIDUALS)











