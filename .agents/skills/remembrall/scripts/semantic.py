#!/usr/bin/env python3
"""
Remembrall Semantic Engine.
Zero external dependencies (pure Python standard library).
Provides TF-IDF vector space modeling, cosine similarity, and concept synonym expansion.
"""

import math
import re
from collections import Counter

CONCEPT_SYNONYMS = {
    "auth": ["authentication", "oauth", "jwt", "token", "login", "signin", "masuk", "autentikasi", "credential", "session"],
    "billing": ["payment", "stripe", "checkout", "subscription", "invoice", "bayar", "transaksi", "duit", "langganan"],
    "database": ["db", "sqlite", "postgres", "postgresql", "mysql", "sql", "migration", "alembic", "orm", "prisma", "basis data", "tabel"],
    "ui": ["frontend", "react", "tailwind", "css", "layout", "view", "component", "komponen", "halaman", "tampilan", "dashboard"],
    "api": ["backend", "fastapi", "flask", "express", "endpoint", "route", "router", "service", "layanan", "rest", "controller"],
    "testing": ["test", "unittest", "pytest", "spec", "uji", "pengujian", "e2e", "mock", "assert"],
    "memory": ["remembrall", "context", "state", "cache", "ingat", "memori", "history", "tracking"]
}


def tokenize(text):
    return [t.lower() for t in re.findall(r"\w+", text)]


class SemanticEngine:
    def __init__(self, items):
        """
        items: list of dicts with fields: id, title, files, notes, status
        """
        self.items = items
        self.doc_tokens = []
        self.doc_count = len(items)
        self.vocabulary = set()
        self.idf = {}
        
        # Build vocabulary & tokens
        for item in items:
            combined = f"{item.get('title', '')} {item.get('files', '')} {item.get('notes', '')} {item.get('status', '')}"
            tokens = tokenize(combined)
            self.doc_tokens.append(tokens)
            self.vocabulary.update(tokens)
            
        # Compute IDF
        for word in self.vocabulary:
            doc_freq = sum(1 for tokens in self.doc_tokens if word in tokens)
            self.idf[word] = math.log((1 + self.doc_count) / (1 + doc_freq)) + 1.0

    def _expand_query(self, query_tokens):
        expanded = set(query_tokens)
        for token in query_tokens:
            for concept, synonyms in CONCEPT_SYNONYMS.items():
                if token == concept or token in synonyms:
                    expanded.add(concept)
                    expanded.update(synonyms[:4])
        return list(expanded)

    def _tfidf_vector(self, tokens):
        counts = Counter(tokens)
        total = len(tokens) if tokens else 1
        vec = {}
        for word, count in counts.items():
            tf = count / total
            idf = self.idf.get(word, 1.0)
            vec[word] = tf * idf
        return vec

    def _cosine_similarity(self, vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum(vec1[k] * vec2[k] for k in intersection)
        
        norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
        
        if not norm1 or not norm2:
            return 0.0
        return numerator / (norm1 * norm2)

    def search(self, query_str, limit=5):
        query_tokens = tokenize(query_str)
        if not query_tokens:
            return []
            
        expanded_tokens = self._expand_query(query_tokens)
        q_vec = self._tfidf_vector(expanded_tokens)
        
        results = []
        for idx, item in enumerate(self.items):
            d_tokens = self.doc_tokens[idx]
            d_vec = self._tfidf_vector(d_tokens)
            similarity = self._cosine_similarity(q_vec, d_vec)
            
            # Concept intersection boost
            concept_boost = 0.0
            item_text = f"{item.get('title', '')} {item.get('files', '')} {item.get('notes', '')}".lower()
            for token in query_tokens:
                for concept, synonyms in CONCEPT_SYNONYMS.items():
                    if (token == concept or token in synonyms) and any(syn in item_text for syn in [concept] + synonyms):
                        concept_boost += 0.2
                        
            final_score = min(1.0, similarity + concept_boost)
            if final_score > 0.05:
                results.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "files": item.get("files"),
                    "notes": item.get("notes"),
                    "status": item.get("status"),
                    "similarity": round(final_score, 4)
                })
                
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:limit]
