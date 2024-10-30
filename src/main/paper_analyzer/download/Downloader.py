import logging
import os
from concurrent.futures import ThreadPoolExecutor

import requests


class Downloader:
    """"
    Class to handle pdf download tasks efficiently.
    Spawns a thread pool to parallelize multiple download tasks.
    Performs streaming download to ensure efficient memory usage especially for large pdf files.
    """
    # constants
    CHUNK_SIZE = 8192

    # Configure the logger for the class
    logger = logging.getLogger(__name__)
    def __init__(self, on_complete, download_dir,  max_workers=5):
        """

        :param on_complete: callback method invoked on completion of download task.
        :param download_dir: directory on the file system to save downloaded pdf(s).
        :param max_workers: max threads in TPE.
        """
        self.download_dir = download_dir
        self.on_complete = on_complete
        os.makedirs(download_dir, exist_ok=True)  # Ensure download directory exists
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="downloader_tpe")

    def submit_download_task(self, paper_id: str, paper_url: str, token: str):
        """Submit download tasks to the thread pool."""
        self.executor.submit(self.download, paper_id, paper_url, token)

    def download(self, paper_id: str, paper_url: str, token: str):
        """Perform the download of a PDF file in streaming mode."""
        self.logger.info(f"Download task initiated for paper: {paper_id}")

        url_with_token = f"{paper_url}?token={token}"
        local_filename = os.path.join(self.download_dir, f"{paper_id}.pdf")

        try:
            # streaming download
            response = requests.get(url_with_token, stream=True)
            response.raise_for_status()  # Raise error for bad responses

            # Write the PDF to a local file in chunks
            with open(local_filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=self.CHUNK_SIZE):
                    if chunk:
                        file.write(chunk)

            self.logger.info(f"Downloaded {paper_id} to {local_filename}")
            # Invoke the callback on successful download
            self.on_complete(paper_id, True)

        except requests.RequestException as e:
            self.logger.error(f"Failed to download {paper_id}: {e}")
            self.on_complete(paper_id, False)
