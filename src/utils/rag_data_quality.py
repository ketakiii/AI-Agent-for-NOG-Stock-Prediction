import json
import re
import pandas as pd
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
from sentence_transformers import SentenceTransformer
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import hashlib

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class RAGDataQualityPipeline:
    """
    Comprehensive pipeline for creating high-quality RAG training data.
    """
    
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.stop_words = set(stopwords.words('english'))
        
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text for better chunking.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep important ones
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\$\%\#\@\&\+]', '', text)
        
        # Normalize quotes and dashes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace('–', '-').replace('—', '-')
        
        return text
    
    def calculate_text_quality_score(self, text: str) -> float:
        """
        Calculate a quality score for text based on various metrics.
        
        Args:
            text: Text to evaluate
            
        Returns:
            Quality score between 0 and 1
        """
        if not text or len(text.strip()) < 10:
            return 0.0
        
        score = 0.0
        
        # Length score (optimal length: 100-1000 characters)
        length = len(text)
        if 100 <= length <= 1000:
            score += 0.3
        elif 50 <= length <= 2000:
            score += 0.2
        else:
            score += 0.1
        
        # Sentence structure score
        sentences = sent_tokenize(text)
        if len(sentences) >= 2:
            avg_sentence_length = np.mean([len(s.split()) for s in sentences])
            if 5 <= avg_sentence_length <= 25:
                score += 0.2
            else:
                score += 0.1
        
        # Vocabulary richness score
        words = word_tokenize(text.lower())
        unique_words = set(words) - self.stop_words
        if len(words) > 0:
            vocabulary_richness = len(unique_words) / len(words)
            if vocabulary_richness > 0.3:
                score += 0.2
            else:
                score += 0.1
        
        # Financial content score
        financial_keywords = [
            'revenue', 'profit', 'earnings', 'income', 'assets', 'liabilities',
            'debt', 'equity', 'cash', 'investment', 'stock', 'price', 'market',
            'oil', 'gas', 'energy', 'production', 'drilling', 'wells', 'reserves',
            'quarterly', 'annual', 'financial', 'performance', 'growth', 'decline'
        ]
        
        text_lower = text.lower()
        financial_word_count = sum(1 for word in financial_keywords if word in text_lower)
        if financial_word_count >= 2:
            score += 0.3
        elif financial_word_count >= 1:
            score += 0.2
        
        return min(score, 1.0)
    
    def smart_chunk_text(self, text: str, max_chunk_size: int = 1000, 
                        overlap: int = 200) -> List[str]:
        """
        Create intelligent chunks that preserve semantic meaning.
        
        Args:
            text: Text to chunk
            max_chunk_size: Maximum chunk size in characters
            overlap: Overlap between chunks in characters
            
        Returns:
            List of text chunks
        """
        if len(text) <= max_chunk_size:
            return [text]
        
        chunks = []
        sentences = sent_tokenize(text)
        current_chunk = ""
        
        for sentence in sentences:
            # If adding this sentence would exceed max size
            if len(current_chunk + sentence) > max_chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap
                overlap_text = current_chunk[-overlap:] if overlap > 0 else ""
                current_chunk = overlap_text + sentence
            else:
                current_chunk += " " + sentence
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def enhance_metadata(self, chunk: Dict, source_type: str) -> Dict:
        """
        Enhance metadata with additional useful information.
        
        Args:
            chunk: Original chunk dictionary
            source_type: Type of source (news, financials, sec_filing, etc.)
            
        Returns:
            Enhanced chunk with better metadata
        """
        enhanced_chunk = chunk.copy()
        metadata = chunk.get('metadata', {})
        
        # Add quality score
        text = chunk.get('text', '')
        enhanced_chunk['quality_score'] = self.calculate_text_quality_score(text)
        
        # Add text statistics
        enhanced_chunk['text_stats'] = {
            'length': len(text),
            'word_count': len(word_tokenize(text)),
            'sentence_count': len(sent_tokenize(text)),
            'unique_words': len(set(word_tokenize(text.lower())) - self.stop_words)
        }
        
        # Add content hash for deduplication
        enhanced_chunk['content_hash'] = hashlib.md5(text.encode()).hexdigest()
        
        # Enhance existing metadata
        if source_type == 'news':
            # Add sentiment indicators
            positive_words = ['growth', 'increase', 'positive', 'strong', 'profit', 'gain']
            negative_words = ['decline', 'loss', 'decrease', 'negative', 'weak', 'risk']
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                metadata['sentiment'] = 'positive'
            elif negative_count > positive_count:
                metadata['sentiment'] = 'negative'
            else:
                metadata['sentiment'] = 'neutral'
            
            # Add recency score
            try:
                date_str = metadata.get('date', '')
                if date_str:
                    date = pd.to_datetime(date_str)
                    days_ago = (datetime.now() - date).days
                    metadata['recency_score'] = max(0, 1 - (days_ago / 365))  # Decay over a year
            except:
                metadata['recency_score'] = 0.5
        
        elif source_type == 'financials':
            # Add financial metrics extraction
            financial_metrics = self.extract_financial_metrics(text)
            metadata['extracted_metrics'] = financial_metrics
        
        enhanced_chunk['metadata'] = metadata
        return enhanced_chunk
    
    def extract_financial_metrics(self, text: str) -> Dict:
        """
        Extract financial metrics from text using regex patterns.
        
        Args:
            text: Text containing financial information
            
        Returns:
            Dictionary of extracted metrics
        """
        metrics = {}
        
        # Revenue patterns
        revenue_patterns = [
            r'revenue.*?\$([\d,]+\.?\d*[MBK]?)',
            r'total revenue.*?\$([\d,]+\.?\d*[MBK]?)',
            r'sales.*?\$([\d,]+\.?\d*[MBK]?)'
        ]
        
        for pattern in revenue_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metrics['revenue'] = match.group(1)
                break
        
        # Profit patterns
        profit_patterns = [
            r'net income.*?\$([\d,]+\.?\d*[MBK]?)',
            r'profit.*?\$([\d,]+\.?\d*[MBK]?)',
            r'earnings.*?\$([\d,]+\.?\d*[MBK]?)'
        ]
        
        for pattern in profit_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metrics['profit'] = match.group(1)
                break
        
        # P/E ratio
        pe_match = re.search(r'P/E.*?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if pe_match:
            metrics['pe_ratio'] = float(pe_match.group(1).replace(',', ''))
        
        # ROE
        roe_match = re.search(r'ROE.*?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if roe_match:
            metrics['roe'] = float(roe_match.group(1).replace(',', ''))
        
        return metrics
    
    def filter_low_quality_chunks(self, chunks: List[Dict], 
                                min_quality_score: float = 0.3,
                                min_length: int = 50) -> List[Dict]:
        """
        Filter out low-quality chunks.
        
        Args:
            chunks: List of chunks to filter
            min_quality_score: Minimum quality score threshold
            min_length: Minimum text length
            
        Returns:
            Filtered list of high-quality chunks
        """
        filtered_chunks = []
        
        for chunk in chunks:
            text = chunk.get('text', '')
            quality_score = chunk.get('quality_score', 0)
            
            if (len(text) >= min_length and 
                quality_score >= min_quality_score):
                filtered_chunks.append(chunk)
        
        print(f"[INFO] Filtered {len(chunks)} chunks to {len(filtered_chunks)} high-quality chunks")
        return filtered_chunks
    
    def remove_duplicates(self, chunks: List[Dict]) -> List[Dict]:
        """
        Remove duplicate chunks based on content hash.
        
        Args:
            chunks: List of chunks to deduplicate
            
        Returns:
            Deduplicated list of chunks
        """
        seen_hashes = set()
        unique_chunks = []
        
        for chunk in chunks:
            content_hash = chunk.get('content_hash', '')
            if content_hash and content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_chunks.append(chunk)
            elif not content_hash:
                # Fallback for chunks without hash
                text = chunk.get('text', '').strip()
                if text and text not in [c.get('text', '').strip() for c in unique_chunks]:
                    unique_chunks.append(chunk)
        
        print(f"[INFO] Removed {len(chunks) - len(unique_chunks)} duplicate chunks")
        return unique_chunks
    
    def create_balanced_corpus(self, chunks: List[Dict], 
                             target_size: int = 1000) -> List[Dict]:
        """
        Create a balanced corpus with diverse content types.
        
        Args:
            chunks: List of all chunks
            target_size: Target number of chunks
            
        Returns:
            Balanced list of chunks
        """
        # Group chunks by type
        chunks_by_type = {}
        for chunk in chunks:
            chunk_type = chunk.get('metadata', {}).get('type', 'unknown')
            if chunk_type not in chunks_by_type:
                chunks_by_type[chunk_type] = []
            chunks_by_type[chunk_type].append(chunk)
        
        # Sort chunks by quality score within each type
        for chunk_type in chunks_by_type:
            chunks_by_type[chunk_type].sort(
                key=lambda x: x.get('quality_score', 0), reverse=True
            )
        
        # Calculate target per type (ensure diversity)
        type_weights = {
            'news': 0.4,
            'financials': 0.3,
            'sec_filing': 0.2,
            'fundamentals': 0.1
        }
        
        balanced_chunks = []
        for chunk_type, weight in type_weights.items():
            if chunk_type in chunks_by_type:
                target_count = int(target_size * weight)
                selected_chunks = chunks_by_type[chunk_type][:target_count]
                balanced_chunks.extend(selected_chunks)
        
        # Fill remaining slots with highest quality chunks
        remaining_slots = target_size - len(balanced_chunks)
        if remaining_slots > 0:
            all_chunks = [c for chunks in chunks_by_type.values() for c in chunks]
            all_chunks.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
            
            # Add chunks that aren't already included
            for chunk in all_chunks:
                if len(balanced_chunks) >= target_size:
                    break
                if chunk not in balanced_chunks:
                    balanced_chunks.append(chunk)
        
        print(f"[INFO] Created balanced corpus with {len(balanced_chunks)} chunks")
        return balanced_chunks[:target_size]
    
    def process_data_source(self, source_data: List[Dict], 
                          source_type: str) -> List[Dict]:
        """
        Process a single data source through the quality pipeline.
        
        Args:
            source_data: Raw data from source
            source_type: Type of source (news, financials, etc.)
            
        Returns:
            Processed high-quality chunks
        """
        processed_chunks = []
        
        for item in source_data:
            text = item.get('text', '')
            if not text:
                continue
            
            # Clean text
            cleaned_text = self.clean_text(text)
            if not cleaned_text:
                continue
            
            # Create chunks
            text_chunks = self.smart_chunk_text(cleaned_text)
            
            for chunk_text in text_chunks:
                chunk = {
                    'text': chunk_text,
                    'metadata': item.get('metadata', {})
                }
                
                # Enhance chunk
                enhanced_chunk = self.enhance_metadata(chunk, source_type)
                processed_chunks.append(enhanced_chunk)
        
        return processed_chunks
    
    def build_high_quality_corpus(self, 
                                news_file: str = 'data/chunks/enhanced_news_chunks.json',
                                financials_file: str = 'data/chunks/enhanced_financial_chunks.json',
                                output_file: str = 'data/chunks/high_quality_corpus.jsonl',
                                target_size: int = 1000) -> List[Dict]:
        """
        Build a high-quality corpus for RAG training.
        
        Args:
            news_file: Path to news chunks file
            financials_file: Path to financial chunks file
            output_file: Output file path
            target_size: Target corpus size
            
        Returns:
            List of high-quality chunks
        """
        print("[INFO] Building high-quality RAG corpus...")
        
        all_chunks = []
        
        # Process news data
        try:
            with open(news_file, 'r') as f:
                news_data = json.load(f)
            news_chunks = self.process_data_source(news_data, 'news')
            all_chunks.extend(news_chunks)
            print(f"[INFO] Processed {len(news_chunks)} news chunks")
        except FileNotFoundError:
            print(f"[WARNING] News file not found: {news_file}")
        
        # Process financials data
        try:
            with open(financials_file, 'r') as f:
                financials_data = json.load(f)
            financials_chunks = self.process_data_source(financials_data, 'financials')
            all_chunks.extend(financials_chunks)
            print(f"[INFO] Processed {len(financials_chunks)} financial chunks")
        except FileNotFoundError:
            print(f"[WARNING] Financials file not found: {financials_file}")
        
        if not all_chunks:
            print("[ERROR] No data sources found!")
            return []
        
        # Quality filtering
        filtered_chunks = self.filter_low_quality_chunks(all_chunks)
        
        # Remove duplicates
        unique_chunks = self.remove_duplicates(filtered_chunks)
        
        # Create balanced corpus
        balanced_chunks = self.create_balanced_corpus(unique_chunks, target_size)
        
        # Save to file
        with open(output_file, 'w') as f:
            for chunk in balanced_chunks:
                f.write(json.dumps(chunk) + '\n')
        
        print(f"[INFO] Saved {len(balanced_chunks)} high-quality chunks to {output_file}")
        
        # Print quality statistics
        self.print_corpus_statistics(balanced_chunks)
        
        return balanced_chunks
    
    def print_corpus_statistics(self, chunks: List[Dict]):
        """
        Print detailed statistics about the corpus.
        
        Args:
            chunks: List of chunks to analyze
        """
        if not chunks:
            print("[WARNING] No chunks to analyze")
            return
        
        # Basic statistics
        total_chunks = len(chunks)
        avg_quality = np.mean([c.get('quality_score', 0) for c in chunks])
        avg_length = np.mean([c.get('text_stats', {}).get('length', 0) for c in chunks])
        
        print(f"\n📊 Corpus Statistics:")
        print(f"  - Total chunks: {total_chunks}")
        print(f"  - Average quality score: {avg_quality:.3f}")
        print(f"  - Average length: {avg_length:.0f} characters")
        
        # Type distribution
        type_counts = {}
        for chunk in chunks:
            chunk_type = chunk.get('metadata', {}).get('type', 'unknown')
            type_counts[chunk_type] = type_counts.get(chunk_type, 0) + 1
        
        print(f"\n📈 Content Distribution:")
        for chunk_type, count in type_counts.items():
            percentage = (count / total_chunks) * 100
            print(f"  - {chunk_type}: {count} chunks ({percentage:.1f}%)")
        
        # Quality distribution
        quality_ranges = {
            'High (0.8+)': 0,
            'Good (0.6-0.8)': 0,
            'Medium (0.4-0.6)': 0,
            'Low (0.2-0.4)': 0,
            'Poor (<0.2)': 0
        }
        
        for chunk in chunks:
            score = chunk.get('quality_score', 0)
            if score >= 0.8:
                quality_ranges['High (0.8+)'] += 1
            elif score >= 0.6:
                quality_ranges['Good (0.6-0.8)'] += 1
            elif score >= 0.4:
                quality_ranges['Medium (0.4-0.6)'] += 1
            elif score >= 0.2:
                quality_ranges['Low (0.2-0.4)'] += 1
            else:
                quality_ranges['Poor (<0.2)'] += 1
        
        print(f"\n🎯 Quality Distribution:")
        for range_name, count in quality_ranges.items():
            percentage = (count / total_chunks) * 100
            print(f"  - {range_name}: {count} chunks ({percentage:.1f}%)")

def main():
    """
    Main function to run the RAG data quality pipeline.
    """
    pipeline = RAGDataQualityPipeline()
    
    # Build high-quality corpus
    chunks = pipeline.build_high_quality_corpus(
        target_size=1000  # Adjust based on your needs
    )
    
    if chunks:
        print(f"\n✅ Successfully created high-quality RAG corpus!")
        print(f"📁 Output saved to: data/chunks/high_quality_corpus.jsonl")
        print(f"🔧 Ready to use with your ChromaDB retriever!")

if __name__ == "__main__":
    main() 