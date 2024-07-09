from setuptools import find_packages,setup
setup(
    name='mcq_generator',
    version='0.0.1',
    author='faizan kazmi',
    author_email='faizan3kazmi@gmail.com',
    install_requires=['openai','langchain','streamlit','python-dotenv','PyPDF2','langchain_community'],
    packages=find_packages()
)
