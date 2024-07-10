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
from fpdf import FPDF

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

def split_request(text, number, subject, tone, response_json):
    mcqs = []
    reviews = []
    batch_size = 3

    for i in range(0, number, batch_size):
        current_number = min(batch_size, number - i)
        try:
            with get_openai_callback() as cb:
                response = generate_evaluate_chain({
                    'text': text,
                    'number': current_number,
                    'subject': subject,
                    'tone': tone,
                    'response_json': json.dumps(response_json)
                })
            if isinstance(response, dict):
                mcqs.append(response.get('quiz', ''))
                reviews.append(response.get('review', ''))
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            st.error(f'Error: {e}')
            break
    
    return mcqs, reviews

if button and uploaded_file is not None and mcq_count and subject and tone:
    with st.spinner("Loading..."):
        try:
            text = read_file(uploaded_file)
            mcqs, reviews = split_request(text, mcq_count, subject, tone, RESPONSE_JSON)
            combined_mcqs = ''.join(mcqs)
            combined_reviews = ' '.join(reviews)
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            st.error(f'Error: {e}')
        else:
            if combined_mcqs:
                table_data = get_table_data(combined_mcqs)
                if table_data:
                    if isinstance(table_data, list) and all(isinstance(i, dict) for i in table_data):
                        df = pd.DataFrame(table_data)
                        df.index = df.index + 1
                        st.table(df)
                        st.text_area(label='Review', value=combined_reviews)
                    else:
                        st.error('Error: table_data is not in the correct format')
                else:
                    st.error('Error: table_data is empty')
            else:
                st.write('No MCQs generated.')

if table_data:
    df = pd.DataFrame(table_data)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download quiz and answers as CSV",
        data=csv,
        file_name='quiz_and_answers.csv',
        mime='text/csv'
    )
    
    def create_pdf(data, subject, review):
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"MCQ Quiz for {subject}", 0, 1, 'C')
        pdf.ln(10)
        
        pdf.set_font("Arial", size=12)
        for index, row in data.iterrows():
            pdf.cell(0, 10, f"Q{index+1}. {row['MCQ']}", 0, 1)
            options = row['Choices'].split(' || ')
            for option in options:
                pdf.cell(0, 10, f" {option}", 0, 1)
            pdf.cell(0, 10, f"Answer: {row['Correct']}", 0, 1)
            pdf.ln(5)
        
        # # Review
        # if review:
        #     pdf.add_page()
        #     pdf.set_font("Arial", 'B', 14)
        #     pdf.cell(0, 10, "Review", 0, 1, 'C')
        #     pdf.ln(10)
        #     pdf.set_font("Arial", size=12)
        #     for line in review.split('\n'):
        #         pdf.cell(0, 10, line, 0, 1)
        #         pdf.ln(2)
        
        return pdf.output(dest='S').encode('latin1')

    pdf_data = create_pdf(df, subject, combined_reviews)
    st.download_button(
        label="Download quiz and answers as PDF",
        data=pdf_data,
        file_name='quiz_and_answers.pdf',
        mime='application/pdf'
    )
