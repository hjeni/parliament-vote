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

    def __init__(self, html_paths_gen_factory, download=False, redownload=False, download_dir_path=None, csv_sep=',', verbose=False, n_files=None, log_every=1000):
        # declarations
        self._soup = None
        self._html_file_path = None
        self._end = False
        self._page_counter = 0
        # file generating
        self._html_paths_gen_factory = html_paths_gen_factory
        self._html_paths_gen = self._html_paths_gen_factory()
        # download parameters
        assert not download or download_dir_path is not None, 'Download directory has to be provided!'
        self._download = download
        self._redownload = redownload
        self._download_dir_path = None
        self.change_dir(download_dir_path)
        self._csv_sep = csv_sep
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
        failed = []
        try:
            while True:
                try:
                    yield self.extract_current()
                    if self._verbose:
                        print_progress(self._page_counter, start=0, end=self._n_files, log_every=self._log_every)
                    self._page_counter += 1
                except _DataScrappingError:
                    failed.append(self._page_counter)
                    self._page_counter += 1
        except StopIteration:
            self._end = True

        if self._verbose:
            print('---------------------------------')
            print_download_result(self._page_counter, failed, self._download_dir_path)

    def extract_current(self):
        """
        Returns a dataframe from current page
        """
        mkdir_safe(self._download_dir_path)
        path = self._download_dir_path + f'{self._page_counter}.csv'

        if not os.path.exists(path) or self._redownload:
            # scrape data
            data = self._do_extract()
            if self._download:
                if not os.path.exists(path) or self._redownload:
                    data.to_csv(path, sep=self._csv_sep)
        else:
            # just read data from local directory
            data = pd.read_csv(path, sep=self._csv_sep)
            self._move()
        return data

    @abstractmethod
    def _do_extract(self):
        """
        Actual extraction function to be overwritten in descendants
        """
        pass

    def reset(self):
        """
        Resets the file generator
        """
        self._end = False
        self._page_counter = 0
        self._html_paths_gen = self._html_paths_gen_factory()

    def end(self) -> bool:
        """
        Returns True when there are no pages left to be generated
        """
        return self._end

    def change_dir(self, dir_path):
        """
        Allows to change the working directory
        """
        if dir_path is None:
            return
        self._download_dir_path = dir_path if dir_path[-1] in '/\\' else f'{dir_path}/'

    def _get_soup(self):
        """
        Returns bs4 beautiful soup of current page
        """
        self._html_file_path = next(self._html_paths_gen)
        content_tmp = codecs.open(self._html_file_path, 'r')
        return BeautifulSoup(content_tmp.read(), 'html.parser')

    def _move(self):
        return next(self._html_paths_gen)


class _ParlDataScrapper(_DataScrapper):
    """
    Extracts voting results from HTML pages
    """

    def __init__(self, data_extractor_class, html_paths_gen_factory, column_names, download, redownload, download_dir_path, csv_sep, verbose, n_files, log_every):
        super().__init__(html_paths_gen_factory, download, redownload, download_dir_path, csv_sep, verbose, n_files, log_every)
        self._data_extractor = data_extractor_class(column_names)

    def _do_extract(self):
        """
        Returns a dataframe from current page
        """
        # move to the next page
        self._soup = self._get_soup()
        # extract the data
        return self._extract_data()

    def _extract_data(self) -> pd.DataFrame:
        """
        Generates voting results
        """
        return self._data_extractor.extract_data(self._soup)


class PartiesDataScrapper(_ParlDataScrapper):
    """
    Extracts voting results aggregated by political parties
    """
    def __init__(self, html_paths_gen_factory, column_names, download=False, redownload=False, download_dir_path=None, csv_sep=',', verbose=False, n_files=None, log_every=1000):
        super().__init__(_PartiesDataExtractor, html_paths_gen_factory, column_names, download, redownload, download_dir_path, csv_sep, verbose, n_files, log_every)


class PoliticiansDataScrapper(_ParlDataScrapper):
    """
    Extracts voting results aggregated by political parties
    """
    def __init__(self, html_paths_gen_factory, column_names, download=False, redownload=False, download_dir_path=None, csv_sep=',', verbose=False, n_files=None, log_every=1000):
        super().__init__(_PoliticiansDataExtractor, html_paths_gen_factory, column_names, download, redownload, download_dir_path, csv_sep, verbose, n_files, log_every)

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


class _PartiesDataExtractor(_PageDataExtractor):
    """
    Collects party voting from HTML page
    """

    def __init__(self, df_column_names=None, n_columns=None, keep_copy=False):
        super().__init__(df_column_names, n_columns, keep_copy)
        self._soup = None
        # hardcoded translation for now
        self._translate_dict = {
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
            raise _DataScrappingError

        self._data = pd.DataFrame(columns=self._column_names)
        curr_row = []
        # # go through all values in the HTML table
        for i, value in enumerate(self._generate_table_values()):
            # all values which do not identify a club should be integers
            if i % len(self._column_names) != 0 and not _is_int(value):
                raise _DataScrappingError
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
            raise _DataScrappingError
        # the first page should be the one
        for f in table[1].find_all('td'):
            yield f.string


class _PoliticiansDataExtractor(_PageDataExtractor):
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


class _DataScrappingError(Exception):
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


