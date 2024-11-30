# LLM Task
 
# Gemini PDF Question Answering System

### This CLI app let's users upload, process it, and ask questions on the content using a conversational chat powered by Google's Gemini-pro.

## Prerequisites
* Python 3.10 or higher
* PyPDF2
* Langchain
* Google Generative AI
* Google Cloud SDK

## Installation
1. Clone this repository to your local machine.
2. Create a virtual environment and activate it.
3. Install the required packages by running ```pip install langchain google-generativeai faiss-cpu python-dotenv PyPDF2 langchain_google_genai```
4. Create a ```.env```file in the root directory of the project and add your Google API key:

```python
GOOGLE_API_KEY=your_google_api_key
```
5. Run the application by executing ```python new_app [file_name]```
   - change the file_name with the pdf name that you want to work on.
6. After processing the PDF, the application will enter an interactive mode where you can ask questions. 
   
   
## Code Structure
* ```app.py```: The main Streamlit application.
* ```get_pdf_text```: A function to extract text from the uploaded PDF files.
* ```get_text_chunks```: A function to split the extracted text into smaller chunks.
* ```get_vector_store```: A function to create a vector database for the text chunks.
* ```get_conversional_chain```: A function to create a conversational chain for question answering.
* ```user_input```: A function to handle user input and generate answers.
* ```main```: The main function that sets up the Streamlit application and runs the user input function.
