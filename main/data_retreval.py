def retrieve_relevant_info(self, query, top_k=5):
    query_words = set(re.findall(r'\w+', query.lower()))
    scores = {}
        
    for word in query_words:
        if word in self.inverted_index:
            for idx in self.inverted_index[word]:
                scores[idx] = scores.get(idx, 0) + 1
        
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
    context = "Relevant information:\n\n"
    for idx, _ in sorted_scores:
        context += f"Row {idx}:\n"
        for col in self.df.columns:
            if col != 'combined_text':
                context += f"{col}: {self.df.iloc[idx][col]}\n"
        context += "\n"
        
        return context