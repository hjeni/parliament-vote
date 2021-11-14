from abc import ABC, abstractmethod

import codecs
from bs4 import BeautifulSoup

import pandas as pd

from utils import *

"""
-------------------------------------------- Scrapper -------------------------------------------- 
"""


class _DataScrapper(ABC):
    """
    Generates Pandas dataframes with data from HTML pages
    """

    def __init__(self, file_paths_generator_factory, verbose=False, n_files=None, log_every=1000):
        # declarations
        self._soup = None
        self._html_file_path = None
        self._end = False
        # file generating
        self._file_paths_generator_factory = file_paths_generator_factory
        self._file_paths_generator = self._file_paths_generator_factory()
        # verbose option parameters
        self._verbose = verbose
        self._n_files = n_files
        self._log_every = log_every

    def generate_all(self):
        """
        Returns a generator of pandas dataframes (or tuples of dataframes)

        Yields one tuple per HTML page
        """
        self.reset()
        try:
            counter = 0
            while True:
                yield self.extract_current()
                if self._verbose:
                    print_progress(counter, start=0, end=self._n_files, log_every=self._log_every)
                    counter += 1
        except StopIteration:
            self._end = True

    @abstractmethod
    def extract_current(self):
        """
        Returns a dataframe (or tuples of dataframes) from current page
        """
        pass

    def reset(self):
        """
        Resets the file generator
        """
        self._end = False
        self._file_paths_generator = self._file_paths_generator_factory()

    def end(self) -> bool:
        """
        Returns True when there are no pages left to be generated
        """
        return self._end

    def _get_soup(self):
        """
        Returns bs4 beautiful soup of current page
        """
        self._html_file_path = next(self._file_paths_generator)
        content_tmp = codecs.open(self._html_file_path, 'r')
        return BeautifulSoup(content_tmp.read(), 'html.parser')


class ParlDataScrapper(_DataScrapper):
    """
    Extracts voting results from HTML pages
    """

    def __init__(self, file_paths_generator_factory, column_names_parties, column_names_individual, verbose=False, n_files=None, log_every=1000):
        super().__init__(file_paths_generator_factory, verbose, n_files, log_every)
        # data extractors
        self._pde = PartiesDataExtractor(column_names_parties)
        self._ide = IndividualsDataExtractor(column_names_individual)

    def extract_current(self):
        """
        Returns a dataframe (or tuple of dataframes) from current page
        """
        # move to the next page
        self._soup = self._get_soup()
        # extract the data
        return self._extract_data()

    def _extract_data(self) -> (pd.DataFrame, pd.DataFrame):
        """
        Generates voting results both per political party and per individual politician
        """
        return self._pde.extract_data(self._soup), self._ide.extract_data(self._soup)


"""
-------------------------------------------- Page data extractors -------------------------------------------- 
"""


class _PageDataExtractor(ABC):
    """
    Template to generate pandas dataframe from a bs4 beautiful soup
    """

    def __init__(self, df_column_names=None, n_columns=None, keep_copy=False):
        # set  column names
        assert n_columns is not None or df_column_names is not None, \
            'At least one of the dataframe columns defining parameters has to be set!'
        if n_columns is not None and df_column_names is not None:
            assert len(df_column_names) == n_columns, 'Column names definition is ambiguous!'
        self._column_names = [str(x) for x in range(n_columns)] if df_column_names is None else df_column_names
        # other assignments
        self._data = None
        self._keep_copy = keep_copy

    @abstractmethod
    def extract_data(self, soup: BeautifulSoup):
        """
        Generation wrapper
        """
        pass

    def get_extracted_data(self):
        """
        Returns the generated dataframe (or None if no dataset has been generated)
        """
        if self._data is None:
            return None

        if self._keep_copy:
            # make a copy and return it
            copy = self._data.copy()
            return copy
        # no copy created
        return self._data


class PartiesDataExtractor(_PageDataExtractor):
    """
    Collects party voting from HTML page
    """

    def __init__(self, df_column_names=None, n_columns=None, keep_copy=False):
        super().__init__(df_column_names, n_columns, keep_copy)
        self._soup = None
        # hardcoded translation for now
        self._translate_dict = PARTY_NAMES_TRANSLATE_DICT = {
            'ANO': 'ANO',
            'ODS': 'ODS',
            'Piráti': 'Pirati',
            'SPD': 'SPD',
            'ČSSD': 'CSSD',
            'KSČM': 'KSCM',
            'KDU-ČSL': 'KDU-CSL',
            'TOP09': 'TOP09',
            'STAN': 'STAN',
            'Celkem': 'Celkem'
        }

    def extract_data(self, soup: BeautifulSoup):
        """
        Extracts voting results aggregated per each political party
        """
        self._soup = soup
        if self._soup is None:
            raise DataScrappingError

        self._data = pd.DataFrame(columns=self._column_names)
        curr_row = []
        # # go through all values in the HTML table
        for i, value in enumerate(self._generate_table_values()):
            # all values which do not identify a club should be integers
            if i % len(self._column_names) != 0 and not _is_int(value):
                raise DataScrappingError
            # add value to the row
            curr_row.append(value)
            # for the last element in the row, append the row and reset
            if (i + 1) % len(self._column_names) == 0:
                s = pd.Series(curr_row, index=self._column_names)
                self._data = self._data.append(s, ignore_index=True)
                curr_row = []

        # remove special characters from parties names etc.
        self._data.replace({self._column_names[0]: self._translate_dict}, inplace=True)

        return self.get_extracted_data()

    def _generate_table_values(self):
        """
        Yields data from the parties voting table
        """
        # look for a table HTML element
        table = self._soup.find_all('table')
        # check whether it was found on the page
        if table is None or len(table) <= 1:
            raise DataScrappingError
        # the first page should be the one
        for f in table[1].find_all('td'):
            yield f.string


class IndividualsDataExtractor(_PageDataExtractor):
    """
    Collects party voting from HTML page
    """

    def extract_data(self, soup: BeautifulSoup):
        """
        TODO
        """

        # TODO: implement
        # no copy created
        return self.get_extracted_data()


"""
-------------------------------------------- Helper --------------------------------------------
"""


class DataScrappingError(Exception):
    """
    Signalizes an error during scrapping process
    """
    pass


def _is_int(s):
    """
    Checks whether 's' can be converted to int or not
    """
    try:
        int(s)
        return True
    except ValueError:
        return False


