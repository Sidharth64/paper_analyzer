import logging

from torch.nn.functional import selu_
from transformers import pipeline


class LLMClient:
    """"
        Class to handle all llm interactions for different tasks.
    """
    # constants
    MODEL_NAME = "t5-small"

    # Configure the logger for the class
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.summarizer = pipeline("summarization", model=self.MODEL_NAME)

    def summarize_text(self, text):
        summary = self.summarizer(text, max_length=250, min_length=150, do_sample=False)[0]['summary_text']
        return summary