import os
import json
import PyPDF2
import traceback
import pdfplumber
from src.mcq_generator.logger import logging
def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
            return text
        except Exception as e:
            logging.error(f"Error reading the PDF file: {e}")
            logging.error(traceback.format_exc())
            raise Exception("Error reading the PDF file") from e
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    else:
        raise Exception("Unsupported file format. Only PDF and text files are supported.")



def get_table_data(quiz_str):
    try:
        quiz_dict = json.loads(quiz_str)
        quiz_table_data = []
        for key, value in quiz_dict.items():
            mcq = value["mcq"]
            options = " || ".join(
                [
                    f"{option} : {option_value}" for option, option_value in value["options"].items()
                ]
            )
            
            correct = value["correct"]
            quiz_table_data.append({"MCQ": mcq, "Choices": options, "Correct": correct})
        
        return quiz_table_data
    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False
