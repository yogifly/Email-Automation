"""
Evaluation Metrics Service
Computes similarity and quality metrics between generated and final responses.

Metrics (computed in parallel):
- Edit distance (normalized)
- BLEU score
- ROUGE scores (1, 2, L)
- Semantic similarity (cosine of embeddings)
- Flesch-Kincaid readability
"""

import re
import math
import asyncio
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from collections import Counter


@dataclass
class EvaluationMetrics:
    """Container for all evaluation metrics."""
    edit_distance: float           # 0-1, normalized (0 = identical)
    zero_edit: bool                # True if exact match
    bleu_score: float              # 0-1
    rouge_1: float                 # 0-1, unigram overlap
    rouge_2: float                 # 0-1, bigram overlap
    rouge_l: float                 # 0-1, longest common subsequence
    semantic_similarity: float     # 0-1, embedding cosine similarity
    readability_generated: float   # Flesch-Kincaid grade level
    readability_final: float       # Flesch-Kincaid grade level

    def to_dict(self) -> dict:
        return asdict(self)


class EvaluationService:
    """Service for computing evaluation metrics."""

    # ==================== EDIT DISTANCE ====================

    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Compute Levenshtein edit distance between two strings."""
        if len(s1) < len(s2):
            s1, s2 = s2, s1

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    @classmethod
    def normalized_edit_distance(cls, generated: str, final: str) -> float:
        """
        Compute normalized edit distance.
        Returns 0 for identical strings, 1 for completely different.
        """
        if not generated and not final:
            return 0.0
        if not generated or not final:
            return 1.0

        distance = cls.levenshtein_distance(generated, final)
        max_len = max(len(generated), len(final))
        return round(distance / max_len, 4)

    # ==================== BLEU SCORE ====================

    @staticmethod
    def get_ngrams(tokens: List[str], n: int) -> Counter:
        """Extract n-grams from token list."""
        return Counter(tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1))

    @classmethod
    def bleu_score(
        cls,
        reference: str,
        candidate: str,
        max_n: int = 4,
        weights: Tuple[float, ...] = (0.25, 0.25, 0.25, 0.25)
    ) -> float:
        """
        Compute BLEU score.
        
        Args:
            reference: Ground truth text (user's final response)
            candidate: Generated text
            max_n: Maximum n-gram order
            weights: Weights for each n-gram precision
        """
        ref_tokens = reference.lower().split()
        cand_tokens = candidate.lower().split()

        if len(cand_tokens) == 0:
            return 0.0

        # Compute n-gram precisions
        precisions = []
        for n in range(1, max_n + 1):
            ref_ngrams = cls.get_ngrams(ref_tokens, n)
            cand_ngrams = cls.get_ngrams(cand_tokens, n)

            if not cand_ngrams:
                precisions.append(0.0)
                continue

            overlap = sum((cand_ngrams & ref_ngrams).values())
            total = sum(cand_ngrams.values())
            precisions.append(overlap / total if total > 0 else 0.0)

        # Compute brevity penalty
        ref_len = len(ref_tokens)
        cand_len = len(cand_tokens)

        if cand_len == 0:
            bp = 0.0
        elif cand_len >= ref_len:
            bp = 1.0
        else:
            bp = math.exp(1 - ref_len / cand_len)

        # Compute weighted geometric mean
        if any(p == 0 for p in precisions[:max_n]):
            return 0.0

        log_sum = sum(w * math.log(p) for w, p in zip(weights, precisions) if p > 0)
        score = bp * math.exp(log_sum)

        return round(min(1.0, score), 4)

    # ==================== ROUGE SCORES ====================

    @classmethod
    def rouge_n(cls, reference: str, candidate: str, n: int = 1) -> float:
        """
        Compute ROUGE-N score (recall-based).
        
        Args:
            reference: Ground truth text
            candidate: Generated text
            n: N-gram order (1 for unigrams, 2 for bigrams)
        """
        ref_tokens = reference.lower().split()
        cand_tokens = candidate.lower().split()

        ref_ngrams = cls.get_ngrams(ref_tokens, n)
        cand_ngrams = cls.get_ngrams(cand_tokens, n)

        if not ref_ngrams:
            return 0.0

        overlap = sum((ref_ngrams & cand_ngrams).values())
        total = sum(ref_ngrams.values())

        return round(overlap / total if total > 0 else 0.0, 4)

    @staticmethod
    def lcs_length(s1: List[str], s2: List[str]) -> int:
        """Compute length of longest common subsequence."""
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        return dp[m][n]

    @classmethod
    def rouge_l(cls, reference: str, candidate: str) -> float:
        """
        Compute ROUGE-L score (LCS-based F1).
        """
        ref_tokens = reference.lower().split()
        cand_tokens = candidate.lower().split()

        if not ref_tokens or not cand_tokens:
            return 0.0

        lcs = cls.lcs_length(ref_tokens, cand_tokens)

        precision = lcs / len(cand_tokens)
        recall = lcs / len(ref_tokens)

        if precision + recall == 0:
            return 0.0

        f1 = 2 * precision * recall / (precision + recall)
        return round(f1, 4)

    # ==================== READABILITY ====================

    @staticmethod
    def count_syllables(word: str) -> int:
        """Estimate syllable count in a word."""
        word = word.lower()
        vowels = "aeiouy"
        count = 0
        prev_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel

        # Handle silent e
        if word.endswith("e") and count > 1:
            count -= 1

        return max(1, count)

    @classmethod
    def flesch_kincaid_grade(cls, text: str) -> float:
        """
        Compute Flesch-Kincaid Grade Level.
        Lower = easier to read (target: 6-9 for emails).
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        words = text.split()

        if not sentences or not words:
            return 0.0

        num_sentences = len(sentences)
        num_words = len(words)
        num_syllables = sum(cls.count_syllables(w) for w in words)

        # Flesch-Kincaid formula
        grade = (
            0.39 * (num_words / num_sentences) +
            11.8 * (num_syllables / num_words) -
            15.59
        )

        return round(max(0, grade), 2)

    # ==================== SEMANTIC SIMILARITY ====================

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return round(dot_product / (norm1 * norm2), 4)

    # ==================== MAIN EVALUATION ====================

    async def evaluate(
        self,
        generated: str,
        final: str,
        generated_embedding: List[float] = None,
        final_embedding: List[float] = None
    ) -> EvaluationMetrics:
        """
        Compute all evaluation metrics between generated and final response IN PARALLEL.
        
        Uses asyncio.gather() to compute independent metrics concurrently:
        - Edit distance
        - BLEU score
        - ROUGE-1, ROUGE-2, ROUGE-L scores
        - Semantic similarity
        - Readability scores (both texts)
        
        Args:
            generated: AI-generated response
            final: User's final (edited) response
            generated_embedding: Optional embedding vector for generated text
            final_embedding: Optional embedding vector for final text
            
        Returns:
            EvaluationMetrics object with all scores
        """
        # Run all metric computations in parallel using asyncio.gather()
        results = await asyncio.gather(
            # Edit distance computation
            self._async_normalized_edit_distance(generated, final),
            
            # BLEU score computation
            self._async_bleu_score(final, generated),
            
            # ROUGE-1 computation
            self._async_rouge_n(final, generated, n=1),
            
            # ROUGE-2 computation
            self._async_rouge_n(final, generated, n=2),
            
            # ROUGE-L computation
            self._async_rouge_l(final, generated),
            
            # Readability for generated text
            self._async_flesch_kincaid_grade(generated),
            
            # Readability for final text
            self._async_flesch_kincaid_grade(final),
            
            # Semantic similarity
            self._async_semantic_similarity(generated_embedding, final_embedding),
            
            return_exceptions=False
        )
        
        # Unpack results
        (edit_dist, bleu, r1, r2, rl, read_gen, read_final, semantic_sim) = results
        
        # Check for exact match
        zero_edit = generated.strip() == final.strip()
        
        return EvaluationMetrics(
            edit_distance=edit_dist,
            zero_edit=zero_edit,
            bleu_score=bleu,
            rouge_1=r1,
            rouge_2=r2,
            rouge_l=rl,
            semantic_similarity=semantic_sim,
            readability_generated=read_gen,
            readability_final=read_final
        )

    # ==================== ASYNC WRAPPER METHODS ====================
    
    async def _async_normalized_edit_distance(self, generated: str, final: str) -> float:
        """Async wrapper for normalized edit distance computation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.normalized_edit_distance,
            generated,
            final
        )
    
    async def _async_bleu_score(self, reference: str, candidate: str) -> float:
        """Async wrapper for BLEU score computation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.bleu_score,
            reference,
            candidate
        )
    
    async def _async_rouge_n(self, reference: str, candidate: str, n: int) -> float:
        """Async wrapper for ROUGE-N computation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.rouge_n,
            reference,
            candidate,
            n
        )
    
    async def _async_rouge_l(self, reference: str, candidate: str) -> float:
        """Async wrapper for ROUGE-L computation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.rouge_l,
            reference,
            candidate
        )
    
    async def _async_flesch_kincaid_grade(self, text: str) -> float:
        """Async wrapper for Flesch-Kincaid computation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.flesch_kincaid_grade,
            text
        )
    
    async def _async_semantic_similarity(
        self,
        generated_embedding: List[float],
        final_embedding: List[float]
    ) -> float:
        """Async wrapper for semantic similarity computation."""
        if generated_embedding and final_embedding:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                self.cosine_similarity,
                generated_embedding,
                final_embedding
            )
        return 0.0


# Singleton instance
evaluation_service = EvaluationService()
