"""
JLPT Vocabulary RAG (Retrieval-Augmented Generation) Service

This service provides intelligent search and retrieval of JLPT vocabulary
using vector embeddings and semantic similarity matching.
"""

import os
import pandas as pd
import kagglehub
import chromadb
from typing import List, Dict, Optional, Any
import hashlib
from sentence_transformers import SentenceTransformer
from loguru import logger
import json
from pathlib import Path


class JLPTVocabularyRAG:
    """RAG system for JLPT vocabulary with semantic search and intelligent retrieval."""
    
    def __init__(self, data_dir: str = "data", collection_name: str = "jlpt_vocabulary"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.model = None
        self.df = None
        
        # Initialize components
        self._initialize_embedding_model()
        self._initialize_vector_db()
    
    def _initialize_embedding_model(self):
        """Initialize the sentence transformer model for embeddings."""
        try:
            # Use a model that's good for multilingual and Japanese text
            model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            logger.info(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def _initialize_vector_db(self):
        """Initialize ChromaDB vector database."""
        try:
            # Initialize ChromaDB client
            db_path = self.data_dir / "chromadb"
            self.client = chromadb.PersistentClient(path=str(db_path))
            
            # Get or create collection
            try:
                self.collection = self.client.get_collection(self.collection_name)
                logger.info(f"Loaded existing collection: {self.collection_name}")
            except chromadb.errors.NotFoundError:
                # Collection doesn't exist, create it
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "JLPT vocabulary with embeddings"}
                )
                logger.info(f"Created new collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize vector database: {e}")
            raise
    
    async def initialize(self):
        """Initialize the JLPT RAG system by downloading and processing data."""
        try:
            logger.info("Initializing JLPT RAG system...")
            
            # Download and load JLPT dataset
            await self._download_and_load_data()
            
            # Check if we need to build the vector index
            if self.collection.count() == 0:
                logger.info("Building vector index for JLPT vocabulary...")
                await self._build_vector_index()
            else:
                logger.info(f"Vector index already exists with {self.collection.count()} entries")
            
            logger.info("JLPT RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize JLPT RAG system: {e}")
            raise
    
    async def _download_and_load_data(self):
        """Download JLPT dataset from Kaggle and load into memory."""
        try:
            logger.info("Downloading JLPT vocabulary dataset...")
            
            # Download dataset using kagglehub
            dataset_path = kagglehub.dataset_download("robinpourtaud/jlpt-words-by-level")
            csv_path = os.path.join(dataset_path, "jlpt_vocab.csv")
            
            # Load dataset
            self.df = pd.read_csv(csv_path)
            
            # Clean and prepare data
            self.df = self.df.dropna()  # Remove any rows with missing data
            self.df['id'] = range(len(self.df))  # Add unique IDs
            
            logger.info(f"Loaded {len(self.df)} JLPT vocabulary entries")
            logger.info(f"JLPT levels: {sorted(self.df['JLPT Level'].unique())}")
            logger.info(f"Level distribution: {dict(self.df['JLPT Level'].value_counts().sort_index())}")
            
        except Exception as e:
            logger.error(f"Failed to download and load data: {e}")
            raise
    
    async def _build_vector_index(self):
        """Build vector embeddings for all vocabulary entries."""
        try:
            logger.info("Building vector embeddings...")
            
            documents = []
            metadatas = []
            ids = []
            
            for _, row in self.df.iterrows():
                # Create comprehensive text for embedding
                text_for_embedding = f"{row['Original']} {row['Furigana']} {row['English']}"
                
                # Create document text
                doc_text = (f"Japanese: {row['Original']} "
                           f"Reading: {row['Furigana']} "
                           f"English: {row['English']} "
                           f"JLPT Level: {row['JLPT Level']}")
                
                documents.append(doc_text)
                
                metadatas.append({
                    "original": row['Original'],
                    "furigana": row['Furigana'],
                    "english": row['English'],
                    "jlpt_level": row['JLPT Level'],
                    "row_id": int(row['id'])
                })
                
                ids.append(f"jlpt_{row['id']}")
            
            # Generate embeddings
            logger.info("Generating embeddings for vocabulary entries...")
            embeddings = self.model.encode(documents, show_progress_bar=True)
            
            # Add to ChromaDB collection in batches
            batch_size = 500
            for i in range(0, len(documents), batch_size):
                end_idx = min(i + batch_size, len(documents))
                
                self.collection.add(
                    embeddings=embeddings[i:end_idx].tolist(),
                    documents=documents[i:end_idx],
                    metadatas=metadatas[i:end_idx],
                    ids=ids[i:end_idx]
                )
                
                logger.info(f"Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
            
            logger.info(f"Successfully built vector index with {len(documents)} entries")
            
        except Exception as e:
            logger.error(f"Failed to build vector index: {e}")
            raise
    
    def search_vocabulary(
        self, 
        query: str, 
        n_results: int = 10,
        jlpt_levels: Optional[List[str]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for vocabulary entries using semantic similarity.
        
        Args:
            query: Search query (can be in Japanese, English, or mixed)
            n_results: Number of results to return
            jlpt_levels: Filter by JLPT levels (e.g., ['N1', 'N2'])
            include_metadata: Whether to include detailed metadata
            
        Returns:
            List of vocabulary entries with similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])
            
            # Build where clause for filtering
            where_clause = None
            if jlpt_levels:
                where_clause = {"jlpt_level": {"$in": jlpt_levels}}
            
            # Search in vector database
            results = self.collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=n_results,
                where=where_clause
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    result = {
                        'id': results['ids'][0][i],
                        'original': results['metadatas'][0][i]['original'],
                        'furigana': results['metadatas'][0][i]['furigana'],
                        'english': results['metadatas'][0][i]['english'],
                        'jlpt_level': results['metadatas'][0][i]['jlpt_level'],
                        'similarity_score': 1.0 - results['distances'][0][i],  # Convert distance to similarity
                    }
                    
                    if include_metadata:
                        result['document'] = results['documents'][0][i]
                        result['metadata'] = results['metadatas'][0][i]
                    
                    formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} results for query: {query}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return []
    
    def get_vocabulary_by_level(self, jlpt_level: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get vocabulary entries for a specific JLPT level."""
        try:
            filtered_df = self.df[self.df['JLPT Level'] == jlpt_level].head(limit)
            
            results = []
            for _, row in filtered_df.iterrows():
                results.append({
                    'original': row['Original'],
                    'furigana': row['Furigana'],
                    'english': row['English'],
                    'jlpt_level': row['JLPT Level']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get vocabulary for level {jlpt_level}: {e}")
            return []
    
    def get_similar_words(self, word: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Find words similar to the given word."""
        return self.search_vocabulary(word, n_results=n_results, include_metadata=False)
    
    def get_level_statistics(self) -> Dict[str, Any]:
        """Get statistics about JLPT vocabulary levels."""
        try:
            if self.df is None:
                return {}
            
            stats = {
                'total_vocabulary': len(self.df),
                'levels': {},
                'collection_count': self.collection.count() if self.collection else 0
            }
            
            for level in sorted(self.df['JLPT Level'].unique()):
                count = len(self.df[self.df['JLPT Level'] == level])
                percentage = (count / len(self.df)) * 100
                
                stats['levels'][level] = {
                    'count': count,
                    'percentage': round(percentage, 2)
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get level statistics: {e}")
            return {}
    
    def search_by_meaning(self, english_meaning: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Search vocabulary by English meaning."""
        return self.search_vocabulary(english_meaning, n_results=n_results)
    
    def search_by_japanese(self, japanese_word: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """Search vocabulary by Japanese word (kanji or hiragana)."""
        return self.search_vocabulary(japanese_word, n_results=n_results)
    
    def get_random_vocabulary(self, jlpt_level: Optional[str] = None, count: int = 5) -> List[Dict[str, Any]]:
        """Get random vocabulary entries, optionally filtered by JLPT level."""
        try:
            if self.df is None:
                return []
            
            df_to_sample = self.df
            if jlpt_level:
                df_to_sample = self.df[self.df['JLPT Level'] == jlpt_level]
            
            if len(df_to_sample) == 0:
                return []
            
            sample_size = min(count, len(df_to_sample))
            random_entries = df_to_sample.sample(n=sample_size)
            
            results = []
            for _, row in random_entries.iterrows():
                results.append({
                    'original': row['Original'],
                    'furigana': row['Furigana'],
                    'english': row['English'],
                    'jlpt_level': row['JLPT Level']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get random vocabulary: {e}")
            return []


# Global instance
_jlpt_rag_instance = None

async def get_jlpt_rag() -> JLPTVocabularyRAG:
    """Get or create the global JLPT RAG instance."""
    global _jlpt_rag_instance
    
    if _jlpt_rag_instance is None:
        _jlpt_rag_instance = JLPTVocabularyRAG()
        await _jlpt_rag_instance.initialize()
    
    return _jlpt_rag_instance