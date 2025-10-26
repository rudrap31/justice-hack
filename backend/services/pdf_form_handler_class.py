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

    filler = PDFFormFiller("CLC Unjust Dismissal.pdf")
    template = filler.get_form_template()

    template = {"LAB1190_E[0]": "", "LAB1190_E[0].Page1[0]": "", "LAB1190_E[0].Page1[0].sf_Section_A[0]": "", "LAB1190_E[0].Page1[0].sf_Section_A[0].txtF_Last_Name[0]": "Islam", "LAB1190_E[0].Page1[0].sf_Section_A[0].txtF_Given_Names[0]": "Sudi Shahariah", "LAB1190_E[0].Page1[0].sf_Section_A[0].txtF_Initial[0]": "S", "LAB1190_E[0].Page1[0].sf_Section_A[0].txtF_Mailing_address[0]": "2690 west 21st avenue", "LAB1190_E[0].Page1[0].sf_Section_A[0].txtF_city[0]": "Vancouver", "LAB1190_E[0].Page1[0].sf_Section_A[0].txtF_province[0]": "BC", "LAB1190_E[0].Page1[0].sf_Section_A[0].txtF_Postal_code[0]": "V6L1K1", "LAB1190_E[0].Page1[0].sf_Section_A[0].txtF_Home_Number[0]": "+89123789236", "LAB1190_E[0].Page1[0].sf_Section_A[0].txtF_Other_Phone_Number[0]": "", "LAB1190_E[0].Page1[0].sf_Section_A[0].txtF_job_title[0]": "Junior Software Developer", "LAB1190_E[0].Page1[0].sf_Section_A[0].rb_TemP_Foreign[0]": "/Yes", "LAB1190_E[0].Page1[0].sf_Section_A[0].txtF_first_day_worked[0]": "June 2024", "LAB1190_E[0].Page1[0].sf_Section_A[0].txtF_Date_E[0]": "2024/12/12", "LAB1190_E[0].Page1[0].sf_Section_A[0].sf_Borders[0]": "", "LAB1190_E[0].Page1[0].sf_Section_A[0].sf_Borders[0].CheckBox1[0]": "/Yes", "LAB1190_E[0].Page1[0].sf_Section_A[0].rb_Did_you[0]": "/Off", "LAB1190_E[0].Page1[0].sf_Section_A[0].txtF_Date_start_intern[0]": "", "LAB1190_E[0].Page1[0].sf_Section_A[0].txtF_Date_fisnh_intern[0]": "", "LAB1190_E[0].Page1[0].sf_Section_B[0]": "", "LAB1190_E[0].Page1[0].sf_Section_B[0].txtF_Name_Employer[0]": "Amazon", "LAB1190_E[0].Page1[0].sf_Section_B[0].txtF_Business_type[0]": "Cloud computing", "LAB1190_E[0].Page1[0].sf_Section_B[0].sf_QuestionSecB[0]": "", "LAB1190_E[0].Page1[0].sf_Section_B[0].sf_QuestionSecB[0].rb_businessOtherName[0]": "/Off", "LAB1190_E[0].Page1[0].sf_Section_B[0].sf_QuestionSecB[0].txtF_Other_Name[0]": "", "LAB1190_E[0].Page1[0].sf_Section_B[0].txtF_work_address[0]": "745 thurlow st", "LAB1190_E[0].Page1[0].sf_Section_B[0].txtF_city[0]": "Vancouver", "LAB1190_E[0].Page1[0].sf_Section_B[0].txtF_province[0]": "BC", "LAB1190_E[0].Page1[0].sf_Section_B[0].txtF_Postal_code[0]": "V6T1Z4", "LAB1190_E[0].Page1[0].sf_Section_B[0].txtF_contact_person[0]": "Masha Basha", "LAB1190_E[0].Page1[0].sf_Section_B[0].txtF_title[0]": "Software Eng Manager", "LAB1190_E[0].Page1[0].sf_Section_B[0].txtF_telephone_Number[0]": "+27863466", "LAB1190_E[0].Page1[0].sf_Section_B[0].txtF_Office_address[0]": "", "LAB1190_E[0].Page1[0].sf_Section_B[0].sf_Question2[0]": "", "LAB1190_E[0].Page1[0].sf_Section_B[0].sf_Question2[0].rb_employer_business[0]": "/Yes", "LAB1190_E[0].Page1[0].sf_Section_B[0].sf_Question2[0].rb_ifno_Specify[0]": "", "LAB1190_E[0].Page1[0].sf_Section_B[0].sf_Question2[0].txtF_Date_Bank[0]": "", "LAB1190_E[0].Page1[0].sf_Section_B[0].sf_Question2[0].txtF_why_not[0]": "", "LAB1190_E[0].Page2[0]": "", "LAB1190_E[0].Page2[0].sf_SectionC[0]": "", "LAB1190_E[0].Page2[0].sf_SectionC[0].rb_name_remain[0]": "/Yes", "LAB1190_E[0].Page2[0].sf_SectionC[0].rb_reasons[0]": "coz i dont want to be looked down on", "LAB1190_E[0].Page2[0].sf_SectionD[0]": "", "LAB1190_E[0].Page2[0].sf_SectionD[0].rb_Covered[0]": "/Off", "LAB1190_E[0].Page2[0].sf_SectionD[0].txtF_Union[0]": "", "LAB1190_E[0].Page2[0].sf_SectionD[0].rb_Grievence[0]": "", "LAB1190_E[0].Page2[0].sf_SectionD[0].txtF_UnionRep[0]": "", "LAB1190_E[0].Page2[0].sf_SectionD[0].txtF_Telephone[0]": "", "LAB1190_E[0].Page2[0].sf_SectionE[0]": "", "LAB1190_E[0].Page2[0].sf_SectionE[0].rb_Represented[0]": "/Off", "LAB1190_E[0].Page2[0].sf_SectionE[0].sf_PartA[0]": "", "LAB1190_E[0].Page2[0].sf_SectionE[0].sf_PartA[0].txtF_Legal[0]": "", "LAB1190_E[0].Page2[0].sf_SectionE[0].sf_PartA[0].txtF_LawFirm[0]": "", "LAB1190_E[0].Page2[0].sf_SectionE[0].sf_PartA[0].txtF_LawFirmAddress[0]": "", "LAB1190_E[0].Page2[0].sf_SectionE[0].sf_PartB[0]": "", "LAB1190_E[0].Page2[0].sf_SectionE[0].sf_PartB[0].txtF_Last_Name[0]": "", "LAB1190_E[0].Page2[0].sf_SectionE[0].sf_PartB[0].txtF_Given_Names[0]": "", "LAB1190_E[0].Page2[0].sf_SectionE[0].sf_PartB[0].txtF_Mailing_address[0]": "", "LAB1190_E[0].Page2[0].sf_SectionE[0].sf_PartB[0].txtF_city[0]": "", "LAB1190_E[0].Page2[0].sf_SectionE[0].sf_PartB[0].txtF_province[0]": "", "LAB1190_E[0].Page2[0].sf_SectionE[0].sf_PartB[0].txtF_Postal_code[0]": "", "LAB1190_E[0].Page2[0].sf_SectionE[0].sf_PartB[0].txtF_Home_Number[0]": "", "LAB1190_E[0].Page3[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].rb_DidYouFile[0]": "/Off", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].txtF_GovOff[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].rb_90Days[0]": "/Off", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].sf_If_yes[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].sf_If_yes[0].txtF_Date_Filed[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].sf_Section_ii[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].sf_Section_ii[0].sf_Q1[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].sf_Section_ii[0].sf_Q1[0].rb_DidYouFile[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].sf_Section_ii[0].sf_Q2[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].sf_Section_ii[0].sf_Q2[0].rb_DidYouFile[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].sf_Section_ii[0].sf_Q3[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].sf_Section_ii[0].sf_Q3[0].txtF_Date_Bank[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].sf_Section_iii[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].sf_Section_iii[0].sf_Q1[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].sf_Section_iii[0].sf_Q1[0].rb_DidYouFile[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].sf_Section_iii[0].sf_Q2[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].sf_Section_iii[0].sf_Q2[0].rb_DidYouFile[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].sf_Section_iii[0].sf_Q3[0]": "", "LAB1190_E[0].Page3[0].sf_SectionF_cont[0].sf_Section_iii[0].sf_Q3[0].txtF_Date_Bank[0]": "", "LAB1190_E[0].Page4[0]": "", "LAB1190_E[0].Page4[0].sf_SectionI[0]": "", "LAB1190_E[0].Page4[0].sf_SectionI[0].txtF_Comp[0]": "", "LAB1190_E[0].Page4[0].sf_SectionI[0].txtF_Sig1[0]": "", "LAB1190_E[0].Page4[0].sf_SectionI[0].txtF_Signature_Date1_E[0]": "", "LAB1190_E[0].Page4[0].sf_SectionI[0].txtF_Auth[0]": "", "LAB1190_E[0].Page4[0].sf_SectionI[0].txtF_Sig2[0]": "", "LAB1190_E[0].Page4[0].sf_SectionI[0].txtF_Signature_Date2_E[0]": "", "LAB1190_E[0].Page4[0].sf_SectionJ[0]": "", "LAB1190_E[0].Page4[0].sf_SectionJ[0].CheckBox1[0]": "", "LAB1190_E[0].Page4[0].sf_SectionJ[0].CheckBox2[0]": "", "LAB1190_E[0].Page5[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse1[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse1[0].txtF_Received_Date[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse1[0].txtF_name_official[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse1[0].rb_received_by[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse1[0].txtF_Forwarded[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse1[0].txtF_LAS2000[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse1[0].txtF_Date_Ack[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse2[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse2[0].sf_Decision[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse2[0].sf_Decision[0].CheckBox1[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse2[0].sf_Decision[0].CheckBox2[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse2[0].sf_Decision[0].CheckBox3[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse2[0].sf_Decision[0].txtF_Date[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse2[0].sf_Decision[0].txtF_Auth[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse2[0].sf_Decision[0].txtF_Sig2[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse2[0].sf_Decision[0].txtF_Signature_Date2_E[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse2[0].sf_Decision[0].CheckBox4[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse2[0].sf_Decision[0].txtF_Auth3[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse2[0].sf_Decision[0].txtF_Sig3[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse2[0].sf_Decision[0].txtF_Signature_Date3_E[0]": "", "LAB1190_E[0].Page5[0].sf_ForOfficeUse2[0].sf_Decision[0].txtF_Comments[0]": ""}

    filler.fill_form(template, "filled_output.pdf")


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