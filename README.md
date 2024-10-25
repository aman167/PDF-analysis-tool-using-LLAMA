# PDF Document Analysis and Q&A System

## Problem Statement

In today's digital age, organizations and individuals often deal with numerous PDF documents containing valuable information. However, extracting specific information from multiple PDFs can be time-consuming and inefficient. Traditional methods of searching through PDFs are limited to basic keyword matching and don't understand the context or semantic meaning of the content. This creates a need for an intelligent system that can:

- Process multiple PDF documents efficiently
- Understand the context and content of the documents
- Provide accurate answers to natural language queries
- Scale with growing document collections

## Solution

This project implements an intelligent PDF analysis and question-answering system that leverages Large Language Models (LLMs) and vector embeddings to provide contextual answers from PDF documents. The solution:

- Automatically processes and ingests PDF documents
- Creates semantic embeddings for efficient information retrieval
- Uses LLMs to generate human-like responses based on document content
- Provides a simple command-line interface for querying documents
- Supports multiple LLM models through Ollama integration
- Scales efficiently with document collection growth

## Tech Stack

- **Python**: Primary programming language
- **Ollama**: Local LLM deployment and management
- **LangChain**: Framework for developing LLM applications
- **Vector Database**: For storing and retrieving document embeddings
- **PDF Processing Libraries**: For extracting text from PDF documents
- **Supported Models**:
  - llama2:13b
  - llama3.1:8b
  - Other Ollama-compatible models

### Source of Information from PDF document.

![PDF Ingestion Process](screenshots\Mortgage_confermation.png)
_Screenshot showing the PDF ingestion process with progress bar_

### Question and Answer Interface

![Query Interface](screenshots\Mortgage_confermation.png)
_Screenshot of the command-line interface showing a sample query and response_

## Setup and Installation

#### Step 1: Step a Virtual Environment

#### Step 2: Install the Requirements

```
pip install -r requirements.txt
```

#### Step 3: Pull the models (if you already have models loaded in Ollama, then not required)

#### Make sure to have Ollama running on your system from https://ollama.ai

```
ollama pull llama3.1:8b
```

#### Step 4: put your files in the my_pdfs folder after making a directory

```
mkdir my_pdfs
```

#### Step 5: Ingest the files (use python3 if on mac)

```
python readpdf.py
```

Output should look like this:

```shell
Creating new vectorstore
Loading documents from my_pdfs
Loading new documents: 100%|██████████████████████| 1/1 [00:01<00:00,  1.99s/it]
Loaded 235 new documents from my_pdfs
Split into 1268 chunks of text (max. 500 tokens each)
Creating embeddings. May take some minutes...
Ingestion complete! You can now run Talkingpdfs.py to query your documents
```

#### Step 6: Run this command (use python3 if on mac)

```
python Talkingpdfs.py
```

##### Play with your docs

Enter a query: How many locations does WeWork have?

### Try with a different model:

```
ollama pull llama2:13b
MODEL=llama2:13b python Talkingpdfs.py
```

## Add more files

Put any and all your files into the `my_pdfs` directory

The supported extensions are:

- `.pdf`: Portable Document Format (PDF),
