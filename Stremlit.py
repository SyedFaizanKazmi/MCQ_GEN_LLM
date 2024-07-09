import os
import json
import pandas as pd
import traceback
from dotenv import load_dotenv
from src.mcq_generator.util import read_file, get_table_data
import streamlit as st
from langchain_community.callbacks.manager import get_openai_callback
from src.mcq_generator.mcq_generator import generate_evaluate_chain
from src.mcq_generator.logger import logging

with open(r'F:\MCQ_GEN_LLM\response.json', 'r') as file:
    RESPONSE_JSON = file.read()

st.title("MCQ GENERATOR APPLICATION")

uploaded_file = None
mcq_count = None
subject = None
tone = None
response = None
table_data = None

with st.form("users_input"):
    uploaded_file = st.file_uploader('Upload a PDF file:')
    mcq_count = st.number_input("Number of MCQs", min_value=3, max_value=50)
    subject = st.text_input('Insert subject')
    tone = st.text_input('Complexity level of questions', placeholder='simple')
    button = st.form_submit_button("Create MCQs")

if button and uploaded_file is not None and mcq_count and subject and tone:
    with st.spinner("Loading..."):
        try:
            text = read_file(uploaded_file)
            with get_openai_callback() as cb:
                response = generate_evaluate_chain({
                    'text': text,
                    'number': mcq_count,
                    'subject': subject,
                    'tone': tone,
                    'response_json': json.dumps(RESPONSE_JSON)
                })
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            st.error('Error')
        else:
            print(f"Total tokens: {cb.total_tokens}")
            print(f"Prompt tokens: {cb.prompt_tokens}")
            print(f"Completion tokens: {cb.completion_tokens}")
            print(f"Total cost: {cb.total_cost}")
            # print("response:", response)

            if isinstance(response, dict):
                quiz = response.get('quiz', None)
                
                # print("quiz:", quiz)

                if quiz is not None:
                    table_data = get_table_data(quiz)
                    
                    print("table_data:", table_data)

                    if table_data:
                        if isinstance(table_data, list) and all(isinstance(i, dict) for i in table_data):
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            st.table(df)
                            st.text_area(label='Review', value=response['review'])
                        else:
                            st.error('Error: table_data is not in the correct format')
                    else:
                        st.error('Error: table_data is empty')
            else:
                st.write(response)

if table_data:
    df = pd.DataFrame(table_data)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download quiz and answers as CSV",
        data=csv,
        file_name='quiz_and_answers.csv',
        mime='text/csv'
    )
