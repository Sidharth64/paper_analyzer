import os


class Utils:

    @staticmethod
    def construct_pdf_path(download_dir, paper_id):
        return os.path.join(download_dir, f"{paper_id}.pdf")
