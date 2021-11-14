import requests
import time

from utils import *


class HtmlPagesDownloader:
    """
    Can be used to download HTML pages to local directory
    """
    def __init__(self, urls_generator_factory, dir_path, redownload=False, delay=1.0, file_names_factory=None, verbose=False, n_pages=None, log_every=1000):
        # declarations
        self._dir_path = None
        self._redownload = redownload
        self._delay = delay
        # url generating
        self._urls_generator_factory = urls_generator_factory
        self._urls_generator = self._urls_generator_factory()
        self.change_dir(dir_path)
        # file naming: simply use a seed and append .html if no naming rule is defined
        self._file_names_factory = lambda x: f'{x}.html' if file_names_factory is None else file_names_factory
        # verbose option parameters
        self._verbose = verbose
        self._n_pages = n_pages
        self._log_every = log_every

    def download_all(self):
        """
        Downloads all URLs to its working directory
        """
        mkdir_safe(self._dir_path)
        self._urls_generator = self._urls_generator_factory()

        failed, counter = [], 0
        for url in self._urls_generator:
            if self._verbose:
                print_progress(counter, start=0, end=self._n_pages, log_every=self._log_every)
            # try to download the page
            try:
                # create path for the new file, use 'counter' as a seed
                file_path = f'{self._dir_path}{self._file_names_factory(counter)}'
                counter += 1
                if os.path.exists(file_path) and not self._redownload:
                    continue
                r = requests.get(url, allow_redirects=True)
                if r.status_code != 200:
                    if self._verbose:
                        print(f'Status code = {r.status_code}, skipping page {counter}')
                    failed.append(counter)
                    continue
                open(file_path, 'wb').write(r.content)
                # delay next request to avoid server overload
                time.sleep(self._delay)
            except Exception as e:
                if self._verbose:
                    print(f'Exception caught at page ID = {counter}: {e}')
                failed.append(counter)

        if self._verbose:
            print('---------------------------------')
            self._print_download_result(counter, failed, self._dir_path)

    def change_dir(self, dir_path):
        """
        Allows to change the working directory
        """
        self._dir_path = dir_path if dir_path[-1] in '/\\' else f'{dir_path}/'

    @staticmethod
    def _print_download_result(n_pages, failed, dir_path=None):
        """
        Prints result info about a process
        """
        print(f'Download complete.')
        print(f'\tpages processed: {n_pages - len(failed)}')
        print(f'\tpages failed: \t {len(failed)} --> {failed}')
        if dir_path is not None:
            print(f'\nTotal size of the directory at "{dir_path}": {get_dir_size(dir_path) / 1000000:.2f} MB')





