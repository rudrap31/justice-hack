"""
PDF Form Filler Class
A reusable class for filling PDF forms with custom values
"""

from pypdf import PdfReader, PdfWriter
from typing import Dict, List, Optional
import json

class PDFFormFiller:
    """
    A class to handle PDF form filling operations.
    
    Usage:
        # Create instance with PDF
        filler = PDFFormFiller("my_form.pdf")
        
        # Get empty template
        template = filler.get_form_template()
        
        # Fill in your values
        template["Field Name"] = "Your Value"
        
        # Generate filled PDF
        filler.fill_form(template, "output.pdf")
    """
    
    def __init__(self, pdf_path: str):
        """
        Initialize with a PDF file path.
        
        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.fields = {}
        self._load_fields()
    
    def _load_fields(self):
        """Load all form fields from the PDF"""
        try:
            reader = PdfReader(self.pdf_path)
            fields = reader.get_fields()
            
            if not fields:
                print(f"Warning: No form fields found in {self.pdf_path}")
                return
            
            # Store field information
            for field_name, field_info in fields.items():
                field_type = field_info.get('/FT', 'Unknown')
                self.fields[field_name] = {
                    'type': field_type,
                    'value': ''
                }
            
            print(f"✓ Loaded {len(self.fields)} fields from PDF")
            
        except Exception as e:
            print(f"Error loading PDF: {e}")
            raise
    
    def get_form_template(self, include_metadata: bool = False) -> Dict[str, str]:
        """
        Get a dictionary template with all field names and empty values.
        
        Args:
            include_metadata: If True, includes field type info. If False, just field names with empty strings.
        
        Returns:
            Dictionary with field names as keys and empty strings as values
        """
        if include_metadata:
            return self.fields.copy()
        else:
            return {field_name: '' for field_name in self.fields.keys()}
    
    def get_field_names(self) -> List[str]:
        """
        Get a list of all field names in the PDF.
        
        Returns:
            List of field names
        """
        return list(self.fields.keys())
    
    def get_field_info(self, field_name: str) -> Optional[Dict]:
        """
        Get information about a specific field.
        
        Args:
            field_name: Name of the field
            
        Returns:
            Dictionary with field info or None if field doesn't exist
        """
        return self.fields.get(field_name)
    
    def print_fields(self, detailed: bool = False):
        """
        Print all form fields to console.
        
        Args:
            detailed: If True, shows field types. If False, just names.
        """
        print(f"\nForm Fields in {self.pdf_path}")
        print("=" * 70)
        
        if detailed:
            for field_name, field_info in self.fields.items():
                print(f"  {field_name}")
                print(f"    Type: {field_info['type']}")
                print()
        else:
            for i, field_name in enumerate(self.fields.keys(), 1):
                print(f"  {i}. {field_name}")
    
    def export_template_json(self, output_path: str):
        """
        Export the empty form template as a JSON file.
        
        Args:
            output_path: Path where to save the JSON file
        """
        template = self.get_form_template()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        print(f"✓ Template exported to {output_path}")
    
    def import_data_json(self, json_path: str) -> Dict[str, str]:
        """
        Import form data from a JSON file.
        
        Args:
            json_path: Path to the JSON file
            
        Returns:
            Dictionary with form data
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ Data imported from {json_path}")
        return data
    
    def fill_form(self, 
                  form_data: Dict[str, str], 
                  output_pdf: str, 
                  page_num: Optional[int] = None) -> bool:
        """
        Fill the PDF form with provided data and save to a new file.
        
        Args:
            form_data: Dictionary mapping field names to values
            output_pdf: Path where to save the filled PDF
            page_num: Specific page number (0-indexed), list of pages, or None for all pages
            
        Returns:
            True if successful, False otherwise
        """
        try:
            reader = PdfReader(self.pdf_path)
            writer = PdfWriter()
            
            # Clone reader to writer
            writer.clone_reader_document_root(reader)
            
            # Determine which pages to update
            if page_num is None:
                pages_to_update = list(range(len(writer.pages)))
            elif isinstance(page_num, list):
                pages_to_update = page_num
            else:
                pages_to_update = [page_num]
            
            # Update form fields on specified pages
            updated_count = 0
            for idx in pages_to_update:
                try:
                    writer.update_page_form_field_values(writer.pages[idx], form_data)
                    updated_count += 1
                except Exception as e:
                    print(f"⚠ Could not update page {idx + 1}: {e}")
            
            # Write to output file
            with open(output_pdf, 'wb') as output_file:
                writer.write(output_file)
            
            print(f"✓ PDF filled successfully!")
            print(f"  Updated {updated_count} page(s)")
            print(f"  Output saved to: {output_pdf}")
            return True
            
        except Exception as e:
            print(f"❌ Error filling form: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def validate_data(self, form_data: Dict[str, str]) -> tuple[bool, List[str]]:
        """
        Check if the provided data has valid field names.
        
        Args:
            form_data: Dictionary with form data to validate
            
        Returns:
            Tuple of (is_valid, list_of_invalid_fields)
        """
        invalid_fields = []
        for field_name in form_data.keys():
            if field_name not in self.fields:
                invalid_fields.append(field_name)
        
        is_valid = len(invalid_fields) == 0
        return is_valid, invalid_fields


# Example usage
if __name__ == "__main__":

    filler = PDFFormFiller("input_form.pdf")
    template = filler.get_form_template()
    print(template)

    template["Part 1 - Given name"] = "Sudi"

    filler.fill_form(template, "out/filled_output.pdf")


    # # Example 1: Basic usage
    # print("EXAMPLE 1: Basic Usage")
    # print("-" * 70)
    
    # # Step 1: Create instance
    # filler = PDFFormFiller("input_form.pdf")
    
    # # Step 2: Get empty template
    # template = filler.get_form_template()
    # print(f"\nGot template with {len(template)} fields")
    
    # # Step 3: Fill in your values
    # template["Part 1 - Given name"] = "John"
    # template["Part 1 - Family name"] = "Doe"
    # template["Part 1 - Email address"] = "john.doe@example.com"
    # # ... fill in more fields
    
    # # Step 4: Generate filled PDF
    # filler.fill_form(template, "filled_output.pdf")
    
    
    # # Example 2: Export/Import with JSON
    # print("\n\nEXAMPLE 2: Using JSON Files")
    # print("-" * 70)
    
    # filler2 = PDFFormFiller("input_form.pdf")
    
    # # Export empty template
    # filler2.export_template_json("form_template.json")
    
    # # Now you can edit form_template.json in a text editor
    # # Then import it back and fill the PDF
    # # data = filler2.import_data_json("form_template.json")
    # # filler2.fill_form(data, "output.pdf")
    
    
    # # Example 3: Print all field names
    # print("\n\nEXAMPLE 3: View All Fields")
    # print("-" * 70)
    # filler2.print_fields(detailed=False)
    
    
    # # Example 4: Validate data before filling
    # print("\n\nEXAMPLE 4: Validate Data")
    # print("-" * 70)
    
    # test_data = {
    #     "Part 1 - Given name": "John",
    #     "Invalid Field Name": "This will fail",
    # }
    
    # is_valid, invalid = filler2.validate_data(test_data)
    # if not is_valid:
    #     print(f"⚠ Found {len(invalid)} invalid field(s):")
    #     for field in invalid:
    #         print(f"  - {field}")