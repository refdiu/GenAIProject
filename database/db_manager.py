
# database/db_manager.py
import chromadb
import os
import json
from chromadb.config import Settings
from chromadb.utils import embedding_functions

class DatabaseManager:
    # def __init__(self, collection_name="project_artifacts"):
    #     # Initialize ChromaDB
    #     try:
    #         # Try PersistentClient first
    #         self.client = chromadb.PersistentClient(path="./chroma_db")
    #     except ImportError:
    #         # Fall back to Client with explicit persistence settings
    #         self.client = chromadb.Client(Settings(
    #             chroma_db_impl="duckdb+parquet",
    #             persist_directory="./chroma_db"
    #         ))
        
    #     # Set up Hugging Face embedding function (optional)
    #     self.embedding_function = embedding_functions.HuggingFaceEmbeddingFunction(
    #         api_key=os.environ.get("HF_API_KEY"),  # Optional, can be None for some models
    #         model_name="sentence-transformers/all-MiniLM-L6-v2"  # Choose an appropriate model
    #     )
        
    #     # Get the list of existing collections
    #     existing_collections = self.client.list_collections()
    #     existing_collection_names = [col.name for col in existing_collections]
        
    #     # Check if collection exists and get it, otherwise create it
    #     if collection_name in existing_collection_names:
    #         print(f"Collection '{collection_name}' already exists. Getting existing collection.")
    #         self.collection = self.client.get_collection(
    #             name=collection_name,
    #             embedding_function=self.embedding_function
    #         )
    #     else:
    #         print(f"Creating new collection: {collection_name}")
    #         self.collection = self.client.create_collection(
    #             name=collection_name,
    #             embedding_function=self.embedding_function
    #         )
    def __init__(self, collection_name="project_artifacts"):
        self.client = chromadb.PersistentClient(path="./chroma_db")

        self.embedding_function = embedding_functions.HuggingFaceEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        try:
            # ⚠️ Try retrieving the collection with the correct embedding function
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            print(f"✅ Collection '{collection_name}' retrieved successfully.")

        except ValueError as e:
            # 🔥 If there's an embedding function mismatch, delete & recreate the collection
            print(f"⚠️ Error: {str(e)}")
            print(f"🛠️ Deleting and recreating collection '{collection_name}'...")

            self.client.delete_collection(name=collection_name)  # Delete the old one

            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )

            print(f"✅ New collection '{collection_name}' created successfully!")
    
    # Rest of the methods remain the same
    def store_artifact(self, artifact_id, content, metadata=None):
        """
        Store an artifact in the database
        
        Args:
            artifact_id (str): Unique identifier for the artifact
            content (str): Content of the artifact
            metadata (dict): Metadata for the artifact
        """
        if metadata is None:
            metadata = {}
        
        # Add document to ChromaDB
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[artifact_id]
        )
        
        return artifact_id
    
    def retrieve_artifact(self, artifact_id):
        """
        Retrieve an artifact by ID
        
        Args:
            artifact_id (str): ID of the artifact to retrieve
            
        Returns:
            dict: The retrieved artifact
        """
        result = self.collection.get(ids=[artifact_id])
        
        if result and result["documents"]:
            return {
                "id": artifact_id,
                "content": result["documents"][0],
                "metadata": result["metadatas"][0] if result["metadatas"] else {}
            }
        
        return None
    
    def retrieve_artifacts_by_type(self, artifact_type):
        """
        Retrieve all artifacts of a specific type
        
        Args:
            artifact_type (str): Type of artifacts to retrieve
            
        Returns:
            list: List of retrieved artifacts
        """
        result = self.collection.get(
            where={"type": artifact_type}
        )
        
        artifacts = []
        for i in range(len(result["ids"])):
            artifacts.append({
                "id": result["ids"][i],
                "content": result["documents"][i],
                "metadata": result["metadatas"][i] if result["metadatas"] else {}
            })
        
        return artifacts
    
    def search_artifacts(self, query, n_results=5):
        """
        Search for artifacts based on a query
        
        Args:
            query (str): Query string
            n_results (int): Number of results to return
            
        Returns:
            list: List of matching artifacts
        """
        result = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        artifacts = []
        for i in range(len(result["ids"][0])):
            artifacts.append({
                "id": result["ids"][0][i],
                "content": result["documents"][0][i],
                "metadata": result["metadatas"][0][i] if result["metadatas"] else {},
                "distance": result.get("distances", [[0]])[0][i]
            })
        
        return artifacts
    
    def update_artifact(self, artifact_id, content=None, metadata=None):
        """
        Update an existing artifact
        
        Args:
            artifact_id (str): ID of the artifact to update
            content (str): New content (optional)
            metadata (dict): New metadata (optional)
            
        Returns:
            bool: Success status
        """
        update_args = {}
        
        if content is not None:
            update_args["documents"] = [content]
        
        if metadata is not None:
            update_args["metadatas"] = [metadata]
        
        if update_args:
            self.collection.update(
                ids=[artifact_id],
                **update_args
            )
            return True
        
        return False