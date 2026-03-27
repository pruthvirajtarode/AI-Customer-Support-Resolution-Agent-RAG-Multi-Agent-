def retriever_agent(query, vectordb):
    # Retrieve top 3 chunks
    docs = vectordb.similarity_search(query, k=3)
    return [{
        "text": d.page_content,
        "citation": {
            "filename": d.metadata.get("filename"),
            "chunk_id": d.metadata.get("chunk_id")
        }
    } for d in docs]
