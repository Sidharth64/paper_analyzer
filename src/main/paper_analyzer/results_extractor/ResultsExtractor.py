import logging
import os
from concurrent.futures import ThreadPoolExecutor

import pdfplumber
import pandas as pd

from src.main.paper_analyzer.Utils import Utils


class ResultsExtractor:
    """"
        Class to handle results extraction from downloaded paper pdf efficiently.
        Spawns a thread pool to parallelize multiple results extraction tasks.
    """

    # Configure the logger for the class
    logger = logging.getLogger(__name__)

    def __init__(self, on_complete, download_dir, results_dir, max_workers=5):
        """
            :param on_complete: callback method invoked on completion of result extraction task.
            :param download_dir: directory on the file system that contains downloaded pdf(s).
            :param results_dir: directory on the file system to be used for storing results.
            :param max_workers: max threads in TPE.
        """
        self.on_complete = on_complete
        self.download_dir = download_dir
        os.makedirs(results_dir, exist_ok=True)  # Ensure summaries directory exists
        self.results_dir = results_dir
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="results_extractor_tpe")

    def submit_extract_results_task(self, paper_id: str):
        # Submit tasks to the thread pool
        self.executor.submit(self.extract_results, paper_id)

    def extract_results(self, paper_id: str):
        # Simulated results_extractor extraction task
        self.logger.info(f"Results extraction initiated for paper: {paper_id}")
        # Open the PDF file
        try :
            pdf_path = Utils.construct_pdf_path(self.download_dir, paper_id)
            tables_as_df_mapping = {}
            with (pdfplumber.open(pdf_path) as pdf):
                table_count = 0  # Counter for naming CSV files

                # Iterate over each page in the PDF
                for page_number, page in enumerate(pdf.pages, start=1):
                    # Extract tables from the page
                    tables = page.extract_tables()

                    # If there are tables on this page, process them
                    for table in tables:
                        tables_as_df_mapping[f"{paper_id}_{page_number}_{table_count}.csv"] = pd.DataFrame(table[1:], columns=table[0])
                        table_count += 1
                self.logger.info(f"Extracted {table_count} tables for paper: {paper_id}")

            # Call the on_complete callback
            self.logger.info(f"Results extraction finished for paper: {paper_id}")
            self.on_complete(paper_id, True)
        except Exception as e:
            self.logger.error(f"Results extraction failed for paper: {paper_id}, error: {e}")
            self.on_complete(paper_id, False)