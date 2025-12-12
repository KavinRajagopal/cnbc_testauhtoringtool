"""Similarity analyzer using OpenAI embeddings."""

import logging
import os
from typing import List
import numpy as np
from openai import OpenAI

from app.optimizers.models import TestCase, SimilarTestPair

logger = logging.getLogger(__name__)


class SimilarityAnalyzer:
    """
    Detects similar tests using OpenAI embeddings and cosine similarity.
    Flags test pairs with >70% similarity.
    """
    
    def __init__(self):
        """Initialize similarity analyzer."""
        self.threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.70"))
        self.use_embeddings = os.getenv("SIMILARITY_USE_EMBEDDINGS", "true").lower() == "true"
        
        if self.use_embeddings:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.client = OpenAI(api_key=api_key)
                logger.info(f"Similarity analyzer initialized (threshold: {self.threshold})")
            else:
                logger.warning("OpenAI API key not found, similarity detection disabled")
                self.client = None
        else:
            self.client = None
            logger.info("Similarity detection using embeddings is disabled")
    
    def analyze(self, test_cases: List[TestCase]) -> List[SimilarTestPair]:
        """
        Analyze test cases for similarity.
        
        Args:
            test_cases: List of test cases to analyze
            
        Returns:
            List of similar test pairs above threshold
        """
        if not self.client or not test_cases or len(test_cases) < 2:
            return []
        
        try:
            logger.info(f"Analyzing {len(test_cases)} tests for similarity")
            
            # Get embeddings for all tests
            embeddings = self._get_embeddings(test_cases)
            
            if not embeddings:
                return []
            
            # Calculate pairwise similarities
            similar_pairs = []
            
            for i in range(len(test_cases)):
                for j in range(i + 1, len(test_cases)):
                    similarity = self._cosine_similarity(
                        embeddings[i],
                        embeddings[j]
                    )
                    
                    if similarity >= self.threshold:
                        pair = self._create_similar_pair(
                            test_cases[i],
                            test_cases[j],
                            similarity
                        )
                        similar_pairs.append(pair)
                        logger.info(
                            f"Similar tests found: {test_cases[i].name} ↔️ "
                            f"{test_cases[j].name} ({similarity:.1%})"
                        )
            
            return similar_pairs
            
        except Exception as e:
            logger.error(f"Similarity analysis failed: {e}", exc_info=True)
            return []
    
    def _get_embeddings(self, test_cases: List[TestCase]) -> List[List[float]]:
        """
        Get embeddings for all test cases.
        
        Args:
            test_cases: List of test cases
            
        Returns:
            List of embedding vectors
        """
        try:
            # Prepare texts for embedding
            texts = []
            for test in test_cases:
                # Combine test name, docstring, and code for embedding
                text_parts = [test.name]
                if test.docstring:
                    text_parts.append(test.docstring)
                text_parts.append(test.code)
                
                text = " ".join(text_parts)
                texts.append(text)
            
            # Get embeddings from OpenAI
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to get embeddings: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Similarity score (0-1)
        """
        try:
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
            
        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {e}")
            return 0.0
    
    def _create_similar_pair(
        self,
        test1: TestCase,
        test2: TestCase,
        similarity: float
    ) -> SimilarTestPair:
        """
        Create a SimilarTestPair with suggestion.
        
        Args:
            test1: First test case
            test2: Second test case
            similarity: Similarity score
            
        Returns:
            SimilarTestPair object
        """
        # Generate suggestion based on similarity level
        if similarity >= 0.9:
            suggestion = "Tests are nearly identical - consider removing duplicate"
        elif similarity >= 0.8:
            suggestion = "Combine using parametrization with @pytest.mark.parametrize"
        else:
            suggestion = "Consider consolidating or making tests more distinct"
        
        # Generate example code for parametrization
        example_code = self._generate_parametrization_example(test1, test2)
        
        return SimilarTestPair(
            test1=test1.name,
            test2=test2.name,
            similarity=round(similarity, 3),
            suggestion=suggestion,
            example_code=example_code
        )
    
    def _generate_parametrization_example(
        self,
        test1: TestCase,
        test2: TestCase
    ) -> str:
        """
        Generate example parametrization code.
        
        Args:
            test1: First test
            test2: Second test
            
        Returns:
            Example code string
        """
        # Extract common base name
        name1 = test1.name.replace('test_', '')
        name2 = test2.name.replace('test_', '')
        
        # Find common prefix
        common = []
        for c1, c2 in zip(name1, name2):
            if c1 == c2:
                common.append(c1)
            else:
                break
        
        base_name = ''.join(common).rstrip('_')
        if not base_name:
            base_name = "combined"
        
        example = f"""@pytest.mark.parametrize("test_case", [
    "case_1",  # from {test1.name}
    "case_2",  # from {test2.name}
])
def test_{base_name}(test_case):
    # Combined test logic
    pass"""
        
        return example


