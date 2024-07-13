import re
import pandas as pd

def prepare_data_for_retrieval(df):
    # Combine all columns into a single text column
    df['combined_text'] = df.astype(str).agg(' '.join, axis=1)
        
    # Create a simple inverted index
    inverted_index = {}
    for idx, row in df['combined_text'].items():
        for word in set(re.findall(r'\w+', row.lower())):
            if word not in inverted_index:
                inverted_index[word] = []
            inverted_index[word].append(idx)
    
    return inverted_index

def retrieve_relevant_info(df, inverted_index, query, top_k=5):
    query_words = set(re.findall(r'\w+', query.lower()))
    scores = {}
        
    for word in query_words:
        if word in inverted_index:
            for idx in inverted_index[word]:
                scores[idx] = scores.get(idx, 0) + 1
        
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
    context = "Relevant information:\n\n"
    for idx, _ in sorted_scores:
        context += f"Row {idx}:\n"
        for col in df.columns:
            if col != 'combined_text':
                context += f"{col}: {df.iloc[idx][col]}\n"
        context += "\n"
        
    return context