import sys
from PyPDF2 import PdfReader
from transformers import pipeline
import re

class PDFQuestionAnsweringSystem:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.document_text = self._extract_text_from_pdf()
        self.qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
        self.chunk_size = 1000  # Define chunk size for splitting large text into smaller sections
        self.overlap_size = 200  # Define overlap size for sliding window approach
        self.top_n = 5  # Increased to consider more answers for better context
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")  # Summarizer model

    def _extract_text_from_pdf(self):
        try:
            with open(self.pdf_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            sys.exit(1)

    def _split_text_into_chunks(self, text, chunk_size, overlap_size):
        chunks = []
        for i in range(0, len(text), chunk_size - overlap_size):
            chunks.append(text[i:i + chunk_size])
        return chunks

    def _post_process_answer(self, answers):
        # Remove redundant phrases and join answers into a coherent response
        processed_answers = []
        seen_sentences = set()
        for ans in answers:
            if ans['score'] > 0.3:  # Filtering out very low confidence answers
                cleaned_answer = re.sub(r'\s+', ' ', ans['answer']).strip()
                # Avoid adding repetitive sentences
                if cleaned_answer not in seen_sentences:
                    processed_answers.append(cleaned_answer)
                    seen_sentences.add(cleaned_answer)
        
        # Combine answers and remove redundancy
        combined_answer = " ".join(processed_answers)
        combined_answer = re.sub(r'(\b\w+\b)(?:\s+\1\b)+', r'\1', combined_answer)  # Remove repeated words

        # Use summarizer to create a coherent summary of the combined answer
        if len(combined_answer.split()) > 30:  # Only summarize if the combined answer is sufficiently long
            summary = self.summarizer(combined_answer, max_length=100, min_length=30, do_sample=False)
            return summary[0]['summary_text']
        else:
            return combined_answer

    def answer_question(self, question):
        try:
            chunks = self._split_text_into_chunks(self.document_text, self.chunk_size, self.overlap_size)
            answers = []

            # Iterate over each chunk to find answers
            for chunk in chunks:
                answer = self.qa_pipeline(question=question, context=chunk)
                answers.append(answer)

            # Sort answers by score and take the top N answers
            top_answers = sorted(answers, key=lambda x: x['score'], reverse=True)[:self.top_n]

            # Post-process the top N answers into a more comprehensive response
            combined_answer = self._post_process_answer(top_answers)
            combined_score = sum([ans['score'] for ans in top_answers]) / len(top_answers)

            return {
                'answer': combined_answer,
                'score': combined_score,
                'start': top_answers[0]['start'],
                'end': top_answers[0]['end']
            }
        except Exception as e:
            print(f"Error answering question: {e}")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 question-answering.py /path/to/document 'question goes here'")
        sys.exit(1)

    pdf_path = sys.argv[1]
    question = " ".join(sys.argv[2:])

    qa_system = PDFQuestionAnsweringSystem(pdf_path)
    answer = qa_system.answer_question(question)

    # Providing answer with source citation
    if answer:
        print(f"Answer: {answer['answer']}\n")
        print(f"Confidence: {answer['score']:.2f}")
        print(f"Answer found in context from character {answer['start']} to {answer['end']}")
    else:
        print("No relevant answer found.")
