import os

os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_enable_pir_api"] = "0"

from paddleocr import PaddleOCR


ocr = PaddleOCR(
    lang="en",
    device="cpu",
    enable_mkldnn=False
)


def extract_text(image_path: str):

    result = ocr.predict(image_path)

    page = result[0]

    return {
        "rec_texts": page["rec_texts"],
        "rec_scores": page["rec_scores"],
        "rec_boxes": page["rec_boxes"]
    }