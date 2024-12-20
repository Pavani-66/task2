# -*- coding: utf-8 -*-
"""TASK2.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1jDbmxZww1iiYIJEohJ9_15ot7KG2bc1q
"""

# Install required libraries (uncomment in Colab)
!pip install requests beautifulsoup4 sentence-transformers faiss-cpu

import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Step 1: Crawl and Scrape
def crawl_and_scrape(urls):
    website_data = {}
    for url in urls:
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            text = " ".join([p.get_text() for p in soup.find_all("p")])
            website_data[url] = text
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    return website_data

# Step 2: Chunk and Embed
def chunk_and_embed(data, model, chunk_size=300):
    chunks = []
    for url, content in data.items():
        # Split content into chunks of specified size
        words = content.split()
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            if len(chunk.strip()) > 0:
                chunks.append((url, chunk.strip()))
    # Generate embeddings for all chunks
    texts = [chunk[1] for chunk in chunks]
    embeddings = model.encode(texts, convert_to_tensor=False)
    return chunks, embeddings

# Step 3: Store in FAISS
def store_embeddings(embeddings):
    d = embeddings.shape[1]  # Dimension of embeddings
    index = faiss.IndexFlatL2(d)
    index.add(np.array(embeddings))
    return index

# Step 4: Query Handling
def query_vector_database(query, index, model, chunks, top_k=5):
    query_embedding = model.encode([query], convert_to_tensor=False)
    distances, indices = index.search(np.array(query_embedding), k=top_k)
    results = [chunks[i] for i in indices[0] if i < len(chunks)]
    return results

# Step 5: Generate Response
def generate_response(results):
    if not results:
        return "Sorry, I couldn't find any relevant information."
    response = "Based on your query, here are the results:\n\n"
    for url, text in results:
        response += f"URL: {url}\nContent: {text[:200]}...\n\n"  # Truncate long content
    return response

# Main Function
def main():
    # Step 1: Define URLs
    urls = [
        "https://www.uchicago.edu/",
        "https://www.washington.edu/",
        "https://www.stanford.edu/",
        "https://und.edu/",
    ]

    # Step 2: Initialize embedding model
    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")  # Pre-trained model

    # Step 3: Crawl and scrape websites
    print("Crawling and scraping websites...")
    website_data = crawl_and_scrape(urls)

    # Step 4: Chunk and embed content
    print("Chunking and embedding content...")
    chunks, embeddings = chunk_and_embed(website_data, model)

    # Step 5: Store embeddings in FAISS
    print("Storing embeddings in FAISS...")
    index = store_embeddings(embeddings)

    # Step 6: Handle user queries
    while True:
        query = input("\nEnter your query (or 'exit' to quit): ")
        if query.lower() == "exit":
            print("Exiting the program.")
            break
        print("Searching content...")
        results = query_vector_database(query, index, model, chunks)
        print("Generating response...")
        response = generate_response(results)
        print(response)

if __name__ == "__main__":
    main()