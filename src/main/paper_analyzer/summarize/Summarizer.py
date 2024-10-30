import logging
import os
from concurrent.futures import ThreadPoolExecutor
import fitz  # PyMuPDF for reading PDF

from src.main.paper_analyzer.Utils import Utils
from src.main.paper_analyzer.llm.LLMClient import LLMClient


class Summarizer:
    """"
       Class to handle summarization of downloaded paper pdf efficiently.
       Spawns a thread pool to parallelize multiple summarization tasks.
    """

    # Configure the logger for the class
    logger = logging.getLogger(__name__)

    def __init__(self, on_complete, download_dir, summaries_dir, max_workers=5):

        """
            :param on_complete: callback method invoked on completion of summarization task.
            :param download_dir: directory on the file system that contains downloaded pdf(s).
            :param summaries_dir: directory on the file system to be used for storing summaries.
            :param max_workers: max threads in TPE.
        """
        self.on_complete = on_complete
        self.download_dir = download_dir
        os.makedirs(summaries_dir, exist_ok=True)  # Ensure summaries directory exists
        self.summaries_dir = summaries_dir
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="summarizer_tpe")
        self.llm_client = LLMClient()

    def submit_summarize_task(self, paper_id: str):
        # Submit summarize tasks to the thread pool
        self.executor.submit(self.summarize, paper_id)

    def summarize(self, paper_id: str):
        # read the pdf content
        self.logger.info(f"Summarization task initiated for paper: {paper_id}")
        pdf_text = self.read_pdf_text(paper_id)

        if not pdf_text:
            self.logger.error(f"No text found in PDF for paper: {paper_id}")
            # Call the on_complete callback
            self.on_complete(paper_id, False)
            return

        # summarize using LLM
        try:

            summary = self.llm_client.summarize_text(f"Summarize this medical research paper: {pdf_text}")
            self.logger.info(f"Generated summary for paper: {paper_id}")

            # write summary to a .txt file
            summary_file_path = os.path.join(self.summaries_dir, f"{paper_id}_summary.txt")
            with open(summary_file_path, "w") as file:
                file.write(summary)
            self.logger.info(f"Summary saved to {summary_file_path}")
            self.on_complete(paper_id, True)
        except Exception as e:
            self.logger.error(f"Summarization failed for paper: {paper_id}, error: {e}")
            self.on_complete(paper_id, False)

    def read_pdf_text(self, paper_id):
        pdf_path = Utils.construct_pdf_path(self.download_dir, paper_id)
        text = ""
        try:
            # Open and read the PDF file
            with fitz.open(pdf_path) as pdf:
                for page in pdf:
                    text += page.get_text()
            self.logger.info(f"Extracted text from paper: {paper_id}")
        except Exception as e:
            self.logger.error(f"Error reading pdf text for paper: {paper_id}: {e}")
        return text


