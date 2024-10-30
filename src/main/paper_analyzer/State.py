from enum import Enum

class State(Enum):
    DOWNLOADING = 1
    DOWNLOAD_FAILED = 2
    DOWNLOAD_SUCCEEDED = 3
    SUMMARIZING = 4
    SUMMARIZATION_FAILED = 5
    SUMMARIZATION_SUCCEEDED = 6
    EXTRACTING_RESULTS = 7
    RESULTS_EXTRACTION_FAILED = 8
    RESULTS_EXTRACTION_SUCCEEDED = 9