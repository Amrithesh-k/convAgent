from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import os
import pandas as pd
import ollama
import re

class SalesReport:
    def __init__(self, df, report_path):
        self.df = df
        self.report_path = report_path

    def sanitize_text(self, text):
        # Remove non-breaking spaces and other potential problematic characters
        text = text.replace('\xa0', ' ')
        # Remove any other non-printable characters
        text = re.sub(r'[^\x20-\x7E\n]', '', text)
        return text

    def generate_report(self, start_date=None, end_date=None):
        report_file = os.path.join(self.report_path, f"daily_sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        doc = SimpleDocTemplate(report_file, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        model = "llama3"

        # Convert ORDERDATE to datetime and extract date
        self.df['ORDERDATE'] = pd.to_datetime(self.df['ORDERDATE'])
        self.df['DATE'] = self.df['ORDERDATE'].dt.date

        # Filter data based on date range if provided
        if start_date:
            self.df = self.df[self.df['DATE'] >= pd.to_datetime(start_date).date()]
        if end_date:
            self.df = self.df[self.df['DATE'] <= pd.to_datetime(end_date).date()]

        # Group by date and calculate daily sales
        daily_sales = self.df.groupby('DATE')['SALES'].sum().reset_index()
        daily_sales = daily_sales.sort_values('DATE')

        # Title (Ollama-generated)
        title_prompt = "Generate a creative title for a daily sales report. just give one title only and no other extra text should be generated"
        title = ollama.generate(model=model, prompt=title_prompt)
        title = self.sanitize_text(title['response'])
        elements.append(Paragraph(title, styles['Title']))
        
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))

        # Summary (Ollama-generated)
        summary_prompt = f"""
        Generate a brief summary for a daily sales report with the following key points:
        - Total Sales: ${daily_sales['SALES'].sum():.2f}
        - Number of Days with Sales: {len(daily_sales)}
        - Highest Daily Sales: ${daily_sales['SALES'].max():.2f} on {daily_sales.loc[daily_sales['SALES'].idxmax(), 'DATE'].strftime('%Y-%m-%d')}
        - Lowest Daily Sales: ${daily_sales['SALES'].min():.2f} on {daily_sales.loc[daily_sales['SALES'].idxmin(), 'DATE'].strftime('%Y-%m-%d')}
        - Average Daily Sales: ${daily_sales['SALES'].mean():.2f}
        """
        summary = ollama.generate(model=model, prompt=summary_prompt)
        summary = self.sanitize_text(summary['response'])
        elements.append(Paragraph("Summary", styles['Heading2']))
        elements.append(Paragraph(summary, styles['Normal']))

        # Summary Table
        summary_data = [
            ["Total Sales", f"${daily_sales['SALES'].sum():.2f}"],
            ["Number of Days with Sales", str(len(daily_sales))],
            ["Highest Daily Sales", f"${daily_sales['SALES'].max():.2f} on {daily_sales.loc[daily_sales['SALES'].idxmax(), 'DATE'].strftime('%Y-%m-%d')}"],
            ["Lowest Daily Sales", f"${daily_sales['SALES'].min():.2f} on {daily_sales.loc[daily_sales['SALES'].idxmin(), 'DATE'].strftime('%Y-%m-%d')}"],
            ["Average Daily Sales", f"${daily_sales['SALES'].mean():.2f}"]
        ]
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(summary_table)

        # Daily Sales Analysis (Ollama-generated)
        daily_sales_prompt = f"""
        Analyze the following daily sales data and provide insights:
        {daily_sales.to_string(index=False)}
        Focus on trends, patterns, and any notable fluctuations in daily sales.
        """
        daily_sales_analysis = ollama.generate(model=model, prompt=daily_sales_prompt)
        daily_sales_analysis = self.sanitize_text(daily_sales_analysis['response'])
        
        elements.append(Paragraph("Daily Sales Analysis", styles['Heading2']))
        elements.append(Paragraph(daily_sales_analysis, styles['Normal']))

        # Daily Sales Table
        daily_sales_data = [["Date", "Sales"]] + [[date.strftime('%Y-%m-%d'), f"${sales:.2f}"] for date, sales in zip(daily_sales['DATE'], daily_sales['SALES'])]
        daily_sales_table = Table(daily_sales_data)
        daily_sales_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(daily_sales_table)

        doc.build(elements)
        return f"The daily sales report has been saved: {report_file}"

# Example usage (you can keep this commented out if it's in a separate file)
"""
if __name__ == "__main__":
    # Assume you have a DataFrame 'sales_df' with columns 'ORDERDATE' and 'SALES'
    sales_df = pd.DataFrame({
        'ORDERDATE': pd.date_range(start='2024-01-01', end='2024-03-31', freq='D'),
        'SALES': np.random.randint(1000, 5000, size=91)  # Random sales data for 91 days
    })

    report_path = 'path/to/save/reports'  # Specify the directory where you want to save the reports
    sales_report = SalesReport(sales_df, report_path)
    result = sales_report.generate_report(start_date='2024-01-01', end_date='2024-03-31')
    print(result)
"""