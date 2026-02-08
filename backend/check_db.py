from models import get_vector_collection, list_vector_sources

collection = get_vector_collection()
all_data = collection.get(include=[])
print(f"Total documents in ChromaDB: {len(all_data['ids'])}")
if all_data['ids']:
    print(f"Sample IDs: {all_data['ids'][:5]}")
else:
    print("No documents found")

sources = list_vector_sources('harry')
print(f"Document sources: {sources}")

# Try a test query
if all_data['ids']:
    results = collection.query(
        query_texts=["test query"],
        n_results=3,
        where={"user_id": "harry"}
    )
    print(f"Test query found {len(results['documents'][0])} results")
    if results['documents'][0]:
        print(f"First result preview: {results['documents'][0][0][:100]}...")
