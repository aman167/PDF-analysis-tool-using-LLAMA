
import os
import glob
from typing import List
from multiprocessing import Pool
from tqdm import tqdm
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from constants import CHROMA_SETTINGS


# Load environment variables
persist_directory = os.environ.get('PERSIST_DIRECTORY', 'vector_db')
source_directory = os.environ.get('SOURCE_DIRECTORY', 'my_pdfs')
embeddings_model_name = os.environ.get('EMBEDDINGS_MODEL_NAME', 'all-MiniLM-L6-v2')
chunk_size = 500
chunk_overlap = 50

LOADER_MAPPING = {
    ".pdf": (PyMuPDFLoader, {}) # for file type .pdf
}


def load_single_document(file_path: str) -> List[Document]:
    """
    Loads a single document given its file path.
    
    Args:
        file_path (str): Path to the document file
    
    Returns:
        List[Document]: List of documents loaded from the file
    """
    loader_class, loader_args = LOADER_MAPPING['.pdf']
    loader = loader_class(file_path, **loader_args)
    return loader.load()

def load_documents(source_dir: str, ignored_files: List[str] = []) -> List[Document]:
    """
    Loads documents from a given directory.

    This function will recursively search for files in the given directory that match any of the
    file extensions specified in the LOADER_MAPPING dictionary. Each matching file will be loaded
    using the corresponding loader class and added to the list of documents.

    Args:
        source_dir (str): Directory to load documents from
        ignored_files (List[str], optional): List of file paths to ignore. Defaults to [].

    Returns:
        List[Document]: List of documents loaded from the directory
    """
    all_files = []
    for ext in LOADER_MAPPING:
        all_files.extend(
            glob.glob(os.path.join(source_dir, f"**/*{ext}"), recursive=True)
        )
    filtered_files = [file_path for file_path in all_files if file_path not in ignored_files]

    with Pool(processes=os.cpu_count()) as pool:
        results = []
        with tqdm(total=len(filtered_files), desc='Loading new documents', ncols=80) as pbar:
            for i, docs in enumerate(pool.imap_unordered(load_single_document, filtered_files)):
                results.extend(docs)
                pbar.update()

    return results

def process_documents(ignored_files: List[str] = []) -> List[Document]:
    """
    Process documents from source directory.

    Loads documents from source directory, ignores specified files, and splits
    the documents into chunks of text using a RecursiveCharacterTextSplitter.

    Args:
        ignored_files (List[str], optional): List of file paths to ignore. Defaults to [].

    Returns:
        List[Document]: List of processed documents in chunks of text
    """
    print(f"Loading documents from {source_directory}")
    documents = load_documents(source_directory, ignored_files)

    print(f"Loaded {len(documents)} new documents from {source_directory}")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = text_splitter.split_documents(documents)
    print(f"Split into {len(texts)} chunks of text (max. {chunk_size} tokens each)")
    return texts

def does_vectorstore_exist(persist_directory: str) -> bool:
    """
    Checks if a vectorstore exists in the given persist_directory.

    Checks if the 'index' directory exists and if it contains at least 3 documents.
    Also checks if the 'chroma-collections.parquet' and 'chroma-embeddings.parquet' files exist.

    Args:
        persist_directory (str): Path to the directory where the vectorstore is stored.

    Returns:
        bool: True if the vectorstore exists, False otherwise.
    """
    if os.path.exists(os.path.join(persist_directory, 'index')):
        if os.path.exists(os.path.join(persist_directory, 'chroma-collections.parquet')) and os.path.exists(os.path.join(persist_directory, 'chroma-embeddings.parquet')):
            list_index_files = glob.glob(os.path.join(persist_directory, 'index/*.bin'))
            list_index_files += glob.glob(os.path.join(persist_directory, 'index/*.pkl'))
            # At least 3 documents are needed in a working vectorstore
            if len(list_index_files) > 3:
                return True
    return False

def main():
    # Create embeddings
    """
    Main function to create and update a vectorstore.

    If a vectorstore already exists at persist_directory, it appends new documents to it.
    Otherwise, it creates a new vectorstore from scratch.

    Args:
        persist_directory (str): Path to the directory where the vectorstore is stored.
        embeddings_model_name (str): Name of the embeddings model to use.

    Returns:
        None
    """
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

    if does_vectorstore_exist(persist_directory):
        # Update and store locally vectorstore
        print(f"Appending to existing vectorstore at {persist_directory}")
        db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, client_settings=CHROMA_SETTINGS)
        collection = db.get()
        texts = process_documents([metadata['source'] for metadata in collection['metadatas']])
        print(f"Creating embeddings. May take some minutes...")
        db.add_documents(texts)
    else:
        # Create and store locally vectorstore
        print("Creating new vectorstore")
        texts = process_documents()
        print(f"Creating embeddings. May take some minutes...")
        db = Chroma.from_documents(texts, embeddings, persist_directory=persist_directory)
    db.persist()
    db = None

    print(f"Embbedding and vectorstore created at {persist_directory}")


if __name__ == "__main__":
    main()
