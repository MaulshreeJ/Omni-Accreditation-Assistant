"""
Table Extractor - Phase 4 Milestone 2
Converts raw pdfplumber tables into structured table objects.
"""

from typing import List, Dict, Any


class TableExtractor:
    """Extract and normalize tables from raw PDF data."""
    
    def extract(self, raw_table: List[List[str]], table_id: str) -> Dict[str, Any]:
        """
        Convert raw table data into structured format.
        
        Args:
            raw_table: Raw table data from pdfplumber
            table_id: Unique identifier for the table
            
        Returns:
            Structured table with headers and rows
        """
        if not raw_table or len(raw_table) == 0:
            return None
        
        # Normalize cells
        normalized_table = []
        for row in raw_table:
            normalized_row = []
            for cell in row:
                # Handle None cells
                if cell is None:
                    normalized_row.append('')
                else:
                    # Normalize whitespace
                    normalized_cell = ' '.join(str(cell).split())
                    normalized_row.append(normalized_cell)
            normalized_table.append(normalized_row)
        
        # Extract headers (first row)
        headers = normalized_table[0] if normalized_table else []
        
        # Extract data rows (remaining rows)
        rows = normalized_table[1:] if len(normalized_table) > 1 else []
        
        # Filter out empty rows
        rows = [row for row in rows if any(cell.strip() for cell in row)]
        
        return {
            'table_id': table_id,
            'headers': headers,
            'rows': rows,
            'num_rows': len(rows),
            'num_cols': len(headers)
        }
    
    def extract_all(self, page_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract all tables from a page.
        
        Args:
            page_data: Page data with raw tables
            
        Returns:
            List of structured tables
        """
        structured_tables = []
        
        for table_data in page_data.get('tables', []):
            structured = self.extract(
                table_data['raw_data'],
                table_data['table_id']
            )
            
            if structured and structured['num_rows'] > 0:
                structured_tables.append(structured)
        
        return structured_tables


# Test function
if __name__ == '__main__':
    extractor = TableExtractor()
    
    # Test with sample data
    raw_table = [
        ['S.No', 'Year', 'Project Title', 'Agency', 'Amount (Lakhs)'],
        ['1', '2022', 'AI in Education', 'DST', '24.5'],
        ['2', '2023', 'ML for Healthcare', 'SERB', '18.2'],
        ['3', '2024', 'Data Science Research', 'DBT', '32.0']
    ]
    
    structured = extractor.extract(raw_table, 'test_table_1')
    
    print("Structured Table:")
    print(f"  Table ID: {structured['table_id']}")
    print(f"  Headers: {structured['headers']}")
    print(f"  Rows: {structured['num_rows']}")
    print(f"  Columns: {structured['num_cols']}")
    print(f"\n  Sample row: {structured['rows'][0]}")
