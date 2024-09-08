import os
import sys

from dotenv import load_dotenv
from unstract.llmwhisperer.client import LLMWhispererClient

from langchain.output_parsers import StructuredOutputParser
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage, SystemMessage

import pandas as pd
import spacy

import prompts

# EDIT: path to save text files to
txt_path = "/Users/mwalton/Documents/ELTE/PDF data extraction/sample_cc_statements/txt_files/"


def make_llm_whisperer_call(file_path):
    print(f"Processing file:{file_path}...")
    # LLMWhisperer API key is picked up from the environment variable
    client = LLMWhispererClient()
    result = client.whisper(file_path=file_path, processing_mode="ocr", output_mode="line-printer")
    return result["extracted_text"]

def error_exit(error_message):
    print(error_message)
    sys.exit(1)


def show_usage_and_exit():
    error_exit("Please pass name of directory or file to process.")


def enumerate_pdf_files(file_path):
    files_to_process = []
    # Users can pass a directory or a file name
    if os.path.isfile(file_path):
        if os.path.splitext(file_path)[1][1:].strip().lower() == 'pdf':
            files_to_process.append(file_path)
    elif os.path.isdir(file_path):
        files = os.listdir(file_path)
        for file_name in files:
            full_file_path = os.path.join(file_path, file_name)
            if os.path.isfile(full_file_path):
                if os.path.splitext(file_name)[1][1:].strip().lower() == 'pdf':
                    files_to_process.append(full_file_path)
    else:
        error_exit(f"Error. {file_path} should be a file or a directory.")

    return files_to_process

def get_filename_from_path(path):
    file_path_arr = path.split('/')
    filename_arr = file_path_arr[-1].split('.')
    filename = filename_arr[0]
    return filename

def extract_txt_from_pdf(file_path, filename):
    # check if text file is already created for PDF
    full_txt_path = f'{txt_path}{filename}.txt'

    if os.path.exists(full_txt_path) is False:
        raw_file_data = make_llm_whisperer_call(file_path)

        with open(txt_path, 'w') as file:
            file.write(raw_file_data)
        print(f"{filename}.txt created")
    else:
        print(f"{filename}.txt already exists")

def TextToDict(doc_text):
    output_parser = StructuredOutputParser.from_response_schemas(prompts.response_schemas)
    format_instructions = output_parser.get_format_instructions()
    print(format_instructions)

    prompt = ChatPromptTemplate.from_template(template=prompts.review_template_2)

    messages = prompt.format_messages(text=doc_text, 
                                format_instructions=format_instructions)
    
    print(messages[0].content)

    model = ChatVertexAI(model="gemini-1.5-flash")

    response = model.invoke(messages)

    print(response.content)

    output_dict = output_parser.parse(response.content)
    return output_dict


def main():
    load_dotenv()
    if len(sys.argv) < 2:
        show_usage_and_exit()

    print(f"Processing path {sys.argv[1]}...")
    file_list = enumerate_pdf_files(sys.argv[1])
    print(f"Processing {len(file_list)} files...")
    print(f"Processing first file: {file_list[0]}...")
    for file_path in file_list:
        filename = get_filename_from_path(file_path)
        extract_txt_from_pdf(file_path, filename)

    for file_path in file_list:
        filename = get_filename_from_path(file_path)
        full_txt_path = f'{txt_path}{filename}.txt'
        f = open(full_txt_path, "r")
        text = f.read()
        dict = TextToDict(text) 
        print(dict)



if __name__ == '__main__':
    main()
