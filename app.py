import streamlit as st
import PyPDF2
import io
from PIL import Image
import pytesseract
from transformers import T5ForConditionalGeneration, T5Tokenizer, RobertaForQuestionAnswering, RobertaTokenizer
import nltk
from nltk.tokenize import sent_tokenize
import re
import torch

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Load models for different tasks
@st.cache_resource
def load_summarization_model():
    tokenizer = T5Tokenizer.from_pretrained("t5-small")
    model = T5ForConditionalGeneration.from_pretrained("t5-small")
    return tokenizer, model

@st.cache_resource
def load_question_generation_model():
    tokenizer = T5Tokenizer.from_pretrained("valhalla/t5-base-qa-qg-hl")
    model = T5ForConditionalGeneration.from_pretrained("valhalla/t5-base-qa-qg-hl")
    return tokenizer, model

@st.cache_resource
def load_question_answering_model():
    tokenizer = RobertaTokenizer.from_pretrained("deepset/roberta-base-squad2")
    model = RobertaForQuestionAnswering.from_pretrained("deepset/roberta-base-squad2")
    return tokenizer, model

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to extract text from image
def extract_text_from_image(image_file):
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    return text

# Function to summarize text
def summarize_text(text, tokenizer, model):
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# Function to split text into paragraphs
def split_into_paragraphs(text):
    # Split text by double newlines or multiple newlines
    paragraphs = re.split(r'\n\s*\n', text)
    # Filter out empty paragraphs
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    # If no paragraphs were found using newlines, create paragraphs based on sentences
    if len(paragraphs) <= 1:
        sentences = sent_tokenize(text)
        paragraphs = []
        current_paragraph = ""
        
        for sentence in sentences:
            current_paragraph += sentence + " "
            if len(current_paragraph) > 500:  # Roughly paragraph size
                paragraphs.append(current_paragraph.strip())
                current_paragraph = ""
        
        if current_paragraph:
            paragraphs.append(current_paragraph.strip())
    
    return paragraphs

# Function to generate questions using Valhalla T5 model
def generate_question(paragraph, tokenizer, model):
    try:
        # Add specific task prefix for better question generation
        input_text = "generate question: " + paragraph.strip()
        inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
        
        # Adjust generation parameters for better questions
        question_ids = model.generate(
            inputs,
            max_length=64,
            min_length=10,
            num_beams=4,
            length_penalty=1.5,
            early_stopping=True,
            no_repeat_ngram_size=2
        )
        
        question = tokenizer.decode(question_ids[0], skip_special_tokens=True)
        return question if question.strip() else "Could not generate a question for this paragraph."
    except Exception as e:
        return f"Error generating question: {str(e)}"

# Function to answer question using RoBERTa model
def answer_question(question, paragraph, tokenizer, model):
    try:
        # Ensure inputs are properly formatted
        question = question.strip()
        paragraph = paragraph.strip()
        
        # Encode with proper handling of long sequences
        inputs = tokenizer.encode_plus(
            question,
            paragraph,
            return_tensors="pt",
            max_length=512,
            truncation=True,
            padding="max_length"
        )
        
        # Get model outputs
        outputs = model(**inputs)
        
        # Find the most probable answer span
        answer_start = torch.argmax(outputs.start_logits)
        answer_end = torch.argmax(outputs.end_logits) + 1
        
        # Ensure answer_end is greater than answer_start
        if answer_end <= answer_start:
            answer_end = answer_start + 1
        
        # Extract and clean the answer text
        answer = tokenizer.convert_tokens_to_string(
            tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end])
        )
        
        return answer.strip() if answer.strip() else "Could not find a suitable answer in the text."
    except Exception as e:
        return f"Error generating answer: {str(e)}"

# Streamlit app
def main():
    st.title("PDF and Image Text Analyzer")
    
    with st.spinner("Loading models..."):
        try:
            # Load models
            summary_tokenizer, summary_model = load_summarization_model()
            question_tokenizer, question_model = load_question_generation_model()
            answer_tokenizer, answer_model = load_question_answering_model()
            st.success("Models loaded successfully!")
        except Exception as e:
            st.error(f"Error loading models: {str(e)}")
            return
    
    # File upload
    uploaded_file = st.file_uploader("Upload a PDF or Image file", type=["pdf", "png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        # Extract text from file
        if uploaded_file.type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)
        else:
            text = extract_text_from_image(uploaded_file)
        
        st.subheader("Extracted Text")
        with st.expander("Show Extracted Text"):
            st.text_area("", text, height=200)
        
        # Summarize text
        summary = summarize_text(text, summary_tokenizer, summary_model)
        st.subheader("Summary")
        st.write(summary)
        
        # Split into paragraphs
        paragraphs = split_into_paragraphs(text)
        st.subheader(f"Paragraphs ({len(paragraphs)})")
        
        for i, paragraph in enumerate(paragraphs):
            with st.expander(f"Paragraph {i+1}"):
                st.write(paragraph)
        
        # User selects paragraph for Q&A
        paragraph_selection = st.number_input("Select paragraph number for Q&A generation", 
                                             min_value=1, 
                                             max_value=len(paragraphs),
                                             value=1)
        
        if st.button("Generate Q&A"):
            selected_paragraph = paragraphs[paragraph_selection-1]
            
            with st.spinner("Generating question..."):
                # Generate question using Valhalla T5 model
                question = generate_question(selected_paragraph, question_tokenizer, question_model)
                if question.startswith("Error"):
                    st.error(question)
                    return
            
            with st.spinner("Generating answer..."):
                # Generate answer using RoBERTa model
                answer = answer_question(question, selected_paragraph, answer_tokenizer, answer_model)
                if answer.startswith("Error"):
                    st.error(answer)
                    return
            
            st.subheader("Generated Q&A")
            st.success("Successfully generated Q&A!")
            st.markdown(f"**Question:** {question}")
            st.markdown(f"**Answer:** {answer}")

if __name__ == "__main__":
    main()