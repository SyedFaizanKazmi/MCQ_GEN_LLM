import os
import json
import pandas as pd
import traceback
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain,SequentialChain
from langchain.callbacks import get_openai_callback
import PyPDF2
from src.mcq_generator.logger import logging
from src.mcq_generator.util import read_file,get_table_data
from dotenv import load_dotenv
load_dotenv()

api_key=os.getenv('key')
llm=ChatOpenAI(openai_api_key=api_key,model_name='gpt-3.5-turbo',temperature=1.5)

mcq_prompt = PromptTemplate(
    input_variables=['number', 'response_json', 'subject', 'text', 'tone'],
    template="""
    Text: {text}
    You are an expert MCQ maker. Given the above text, it is your job to create a quiz of {number} multiple choice questions for {subject} students in {tone} tone.
    Make sure the questions are not repeated and check all the questions to be conforming the text as well.
    Make sure to format your response like RESPONSE_JSON below and use it as a guide. Ensure to make {number} MCQs.
    ### RESPONSE_JSON
    {response_json}
    """
)
quiz_chain=LLMChain(llm=llm,prompt=mcq_prompt,output_key='quiz',verbose=True)

evaluation_prompt = PromptTemplate(
    input_variables=['quiz', 'subject'],
    template="""
    You are an expert English grammarian and writer. Given a Multiple Choice Quiz for {subject} students,
    you need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity.
    If the quiz is not at par with the cognitive and analytical abilities of the students,
    update the quiz questions which need to be changed and change the tone such that it perfectly fits the student's abilities.
    Quiz_MCQs: {quiz}
    Check from an expert English Writer of the above quiz:
    """
)
review_chain=LLMChain(llm=llm,prompt=evaluation_prompt,output_key='review',verbose=True)
generate_evaluate_chain=SequentialChain(chains=[quiz_chain,review_chain],input_variables=['number', 'response_json', 'subject', 'text', 'tone'],output_variables=['quiz','review'])
