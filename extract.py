import os
import sys

from dotenv import load_dotenv
from unstract.llmwhisperer.client import LLMWhispererClient

from langchain.prompts import ChatPromptTemplate
from langchain_google_vertexai import ChatVertexAI
from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate, \
    HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser

import pandas as pd
import json

from schema import ParsedCreditCardStatement

# EDIT: 
# 1) path to save text files
# 2) path to save json files
txt_path = "/Users/mwalton/Documents/ELTE/PDF data extraction/sample_cc_statements/results/txt_files/"
json_path = "/Users/mwalton/Documents/ELTE/PDF data extraction/sample_cc_statements/results/json_files/"
csv_path = "/Users/mwalton/Documents/ELTE/PDF data extraction/sample_cc_statements/results/json_files/"


def make_llm_whisperer_call(file_path):
    print(f"Processing file:{file_path}...")
    # LLMWhisperer API key is picked up from the environment variable
    client = LLMWhispererClient()
    result = client.whisper(file_path=file_path, processing_mode="ocr", output_mode="line-printer")
    return result["extracted_text"]

def make_llm_chat_call(text):
    preamble = ("\n"
                "Your ability to extract and summarize this information accurately is essential for effective "
                "credit card statement analysis. Pay close attention to the credit card statement's language, "
                "structure, and any cross-references to ensure a comprehensive and precise extraction of "
                "information. Do not use prior knowledge or information from outside the context to answer the "
                "questions. Only use the information provided in the context to answer the questions.\n")
    postamble = "Do not include any explanation in the reply. Only include the extracted information in the reply."
    system_template = "{preamble}"
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_template = "{format_instructions}\n{raw_file_data}\n{postamble}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    parser = PydanticOutputParser(pydantic_object=ParsedCreditCardStatement)

    # compile chat template
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    request = chat_prompt.format_prompt(preamble=preamble,
                                        format_instructions=parser.get_format_instructions(),
                                        raw_file_data=text,
                                        postamble=postamble).to_messages()

    model = ChatVertexAI(model="gemini-1.5-flash")
    response = model.invoke(request)

    cc_statement_object = parser.parse(response.content)

    return cc_statement_object

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

def textToJson(doc_text, filename):
    # check if text file is already created for PDF
    full_json_path = f'{json_path}{filename}.json'

    if os.path.exists(full_json_path) is False:
        cc_statement_obj = make_llm_chat_call(doc_text)
        json_obj = cc_statement_obj.model_dump_json()

        with open(full_json_path, "w") as file:
            #outfile.write(json_obj)
            file.write(json_obj)

        print(f"{filename}.json created")
    else:
        print(f"{filename}.json already exists")


def main():
    load_dotenv()
    if len(sys.argv) < 2:
        show_usage_and_exit()

    print(f"Processing path {sys.argv[1]}...")
    file_list = enumerate_pdf_files(sys.argv[1])
    print(f"Processing {len(file_list)} files...")
    print(f"Processing first file: {file_list[0]}...")

    # extract text from PDF file and save to txt file
    for file_path in file_list:
        filename = get_filename_from_path(file_path)
        extract_txt_from_pdf(file_path, filename)

    # use LLM to prompt desired information from text and save to json file
    for file_path in file_list:
        filename = get_filename_from_path(file_path)
        full_txt_path = f'{txt_path}{filename}.txt'
        f = open(full_txt_path, "r")
        text = f.read()
        textToJson(text, filename)



if __name__ == '__main__':
    main()
