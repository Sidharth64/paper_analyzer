import csv
import logging
import time
from typing import List, Dict

from src.main.paper_analyzer.State import State
from src.main.paper_analyzer.download.Downloader import Downloader
from src.main.paper_analyzer.results_extractor.ResultsExtractor import ResultsExtractor
from src.main.paper_analyzer.summarize.Summarizer import Summarizer


class PaperAnalyzer:
    """
    Main class that triggers the analysis, submits tasks for - download, summarization & results_extractor extraction.
    """

    # constants
    DOWNLOAD_DIR = "../resources/downloads"
    SUMMARY_DIR = "../resources/summaries"
    RESULTS_DIR = "../resources/results"

    # Configure the logger for the class
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.downloader = Downloader(self.on_download, self.DOWNLOAD_DIR)
        self.summarizer = Summarizer(self.on_summarization, self.DOWNLOAD_DIR, self.SUMMARY_DIR)
        self.results_extractor = ResultsExtractor(self.on_results_extraction, self.DOWNLOAD_DIR, self.RESULTS_DIR)
        self.analysis_status = {}

    def start_analysis(self, csv_file_path: str):
        paper_details = self.read_paper_details(csv_file_path)
        for paper in paper_details:
            # Submit download tasks for each paper
            self.analysis_status[paper["pmid"]] = [State.DOWNLOADING]
            self.downloader.submit_download_task(paper["pmid"], paper["pdf_download_url"], paper["token"])

    @staticmethod
    def read_paper_details(csv_file_path: str) -> List[Dict[str, str]]:
        paper_details = []
        with open(csv_file_path, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                paper_details.append(row)
        return paper_details

    def check_and_wait_for_analysis_completion(self):
        analysis_complete = False
        while not analysis_complete:
            analysis_complete = True
            for states in self.analysis_status.values():
                if not self.is_complete(states):
                    analysis_complete = False
                    break
            # sleep for 5 seconds before checking again
            time.sleep(5)

    @staticmethod
    def is_complete(states):
        if State.DOWNLOAD_FAILED in states:
            return True
        if (State.DOWNLOAD_SUCCEEDED in states
                and (State.SUMMARIZATION_FAILED in states or State.SUMMARIZATION_SUCCEEDED in states))\
                and (State.RESULTS_EXTRACTION_FAILED in states or State.RESULTS_EXTRACTION_SUCCEEDED in states):
            return True
        return False

    def on_download(self, paper_id: str, status: bool):
        # When download succeeds, submit tasks to summarizer and results_extractor extractor
        if not status:
            self.analysis_status[paper_id].append(State.DOWNLOAD_FAILED)
            self.logger.info(f"Download task failed for paper {paper_id}.")
            return

        self.analysis_status[paper_id].append(State.DOWNLOAD_SUCCEEDED)
        self.logger.info(f"Download task succeeded for paper {paper_id}.")

        self.analysis_status[paper_id].append(State.SUMMARIZING)
        self.summarizer.submit_summarize_task(paper_id)

        self.analysis_status[paper_id].append(State.EXTRACTING_RESULTS)
        self.results_extractor.submit_extract_results_task(paper_id)

    def on_summarization(self, paper_id: str, status: bool):
        # Handle post-summarization actions
        if not status:
            self.analysis_status[paper_id].append(State.SUMMARIZATION_FAILED)
            self.logger.info(f"Summarization task failed for paper {paper_id}.")
            return

        self.analysis_status[paper_id].append(State.SUMMARIZATION_SUCCEEDED)
        self.logger.info(f"Summarization task succeeded for paper {paper_id}")

    def on_results_extraction(self, paper_id: str, status: bool):
        # Handle post-results_extractor extraction actions
        if not status:
            self.analysis_status[paper_id].append(State.RESULTS_EXTRACTION_FAILED)
            self.logger.info(f"Results extraction task failed for paper {paper_id}.")
            return

        self.analysis_status[paper_id].append(State.RESULTS_EXTRACTION_SUCCEEDED)
        self.logger.info(f"Results extraction task succeeded for paper {paper_id}")

