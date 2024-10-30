import logging

from src.main.paper_analyzer.PaperAnalyzer import PaperAnalyzer

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(threadName)s - %(name)s - %(message)s')
    analyzer = PaperAnalyzer()
    analyzer.start_analysis("../resources/paper_details.csv")
    analyzer.check_and_wait_for_analysis_completion()
    logging.info("Paper analysis completed")