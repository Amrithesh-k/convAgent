import pandas as pd
import ollama
import os
from datetime import datetime
from report_generator import SalesReport
from email_sender import send_email
from data_retreval import prepare_data_for_retrieval ,retrieve_relevant_info  
import re

class SalesReportAgent:
    def __init__(self):
        self.model = "llama3"
        self.sales_data_path = r"D:\intern\convAgent\files\data.xlsx"
        self.report_path = r"D:\intern\convAgent\report"
        self.df = pd.read_excel(self.sales_data_path)
        
        # Convert SALES column to float
        self.df['SALES'] = pd.to_numeric(self.df['SALES'], errors='coerce')
        
        os.makedirs(self.report_path, exist_ok=True)
        
        # Prepare data for retrieval
        prepare_data_for_retrieval(self)

    def process_input(self, user_input):
        user_input_lower = user_input.lower()
        
        if 'generate' in user_input_lower or "save" in user_input_lower:
            return SalesReport.generate_report(self)
        elif 'send' in user_input_lower:
            match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_input)
            email = match.group(0) if match else "example@email.com"
            return send_email(email, "Sales Report", "Please find attached the sales report.")
        else:
            return self.generate_ai_response(user_input)

    def generate_ai_response(self, query):
        context = self.retrieve_relevant_info(query)
        sales_summary = self.get_sales_summary()
        
        prompt = f"""You are an AI assistant for a sales report system. Use the following information to answer the user's question:

Sales Summary:
{sales_summary}

Relevant Data:
{context}

User question: {query}

Please provide a detailed and helpful response based on the given information."""

        try:
            response = ollama.generate(model=self.model, prompt=prompt)
            return response['response']
        except Exception as e:
            return f"An error occurred while generating the AI response: {str(e)}\n\nHere's the relevant information I found:\n{context}"

    def get_sales_summary(self):
        summary = f"""
Total Sales: ${self.df['SALES'].sum():.2f}
Average Sales: ${self.df['SALES'].mean():.2f}
Number of Orders: {self.df['ORDERNUMBER'].nunique()}
Top Selling Product Line: {self.df.groupby('PRODUCTLINE')['SALES'].sum().idxmax()}
Top Customer: {self.df.groupby('CUSTOMERNAME')['SALES'].sum().idxmax()}
Top Country: {self.df.groupby('COUNTRY')['SALES'].sum().idxmax()}
"""
        return summary