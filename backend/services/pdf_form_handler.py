"""
PDF Form Filler Script
Fills PDF form fields with custom values
"""

from pypdf import PdfReader, PdfWriter

def list_form_fields(pdf_path):
    """
    List all form fields in a PDF to see what fields are available
    """
    reader = PdfReader(pdf_path)
    fields = reader.get_fields()
    
    if not fields:
        print("❌ No form fields found in this PDF")
        return False
    
    print(f"\n✓ Found {len(fields)} form fields:\n")
    for field_name, field_info in fields.items():
        field_type = field_info.get('/FT', 'Unknown')
        field_value = field_info.get('/V', '')
        print(f"  Field: {field_name}")
        print(f"    Type: {field_type}")
        print(f"    Current Value: {field_value}")
        print()
    return True

def fill_pdf_form(input_pdf, output_pdf, field_values, page_num=None):
    """
    Fill PDF form fields with provided values
    
    Args:
        input_pdf: Path to input PDF file
        output_pdf: Path to output PDF file
        field_values: Dictionary mapping field names to values
        page_num: Page number to update (0-indexed), list of page numbers, or None for all pages
                 Examples: page_num=1, page_num=[1,3,5], page_num=None
    """
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    
    # Clone reader to writer (this preserves form structure better)
    writer.clone_reader_document_root(reader)
    
    # Determine which pages to update
    if page_num is None:
        # Update all pages
        pages_to_update = list(range(len(writer.pages)))
    elif isinstance(page_num, list):
        # Update specific list of pages
        pages_to_update = page_num
    else:
        # Update single page
        pages_to_update = [page_num]
    
    # Update form fields on specified pages
    updated_count = 0
    for idx in pages_to_update:
        try:
            writer.update_page_form_field_values(writer.pages[idx], field_values)
            print(f"✓ Updated fields on page {idx + 1} (index {idx})")
            updated_count += 1
        except Exception as e:
            print(f"⚠ Skipped page {idx + 1} (index {idx}): {e}")
    
    # Write to output file
    with open(output_pdf, 'wb') as output_file:
        writer.write(output_file)
    
    print(f"\n✓ PDF form filled successfully!")
    print(f"  Updated {updated_count} page(s)")
    print(f"  Output saved to: {output_pdf}")

# Example usage
if __name__ == "__main__":
    # Configuration
    INPUT_PDF = "input_form.pdf"
    OUTPUT_PDF = "filled_form.pdf"
    
    # Your custom values - modify these to match your needs
    form_data = {
        # Part 1 - Personal Information
        "Part 1 - Given name": "John",
        "Part 1 - Middle name (optional)": "Michael",
        "Part 1 - Family name": "Doe",
        "Part 1 - Preferred name(s) (optional)": "Johnny",
        "Part 1 - Preference for being addressed (optional)": "Mr.",
        "Part 1 - Email address": "john.doe@example.com",
        "Part 1 - No email": "/Off",  # Checkbox - use "/Yes" to check, "/Off" to uncheck
        "Part 1 - Telephone number": "604-555-0123",
        "Part 1 - No telephone": "/Off",
        "Part 1 - Alternate telephone number": "778-555-0456",
        "Part 1 - Street address": "123 Main Street",
        "Part 1 - No address": "/Off",
        "Part 1 - Apartment, suite, unit, floor etc": "Apt 4B",
        "Part 1 - City": "Vancouver",
        "Part 1 - Province/Territory/State": "British Columbia",
        "Part 1 - Country": "Canada",
        "Part 1 - Postal Code": "V6B 1A1",
        "Part 1 - Are you under 19 years of age?": "/Off",
        "Part 1 - Do you consent to share your contact information with the employer?": "/Yes",
        "Part 1 - Do you identify as First Nations, Métis or Inuit?": "/Off",
        "Part 1 - Trouble understanding English": "/Off",
        "Part 1 - Visual impairment": "/Off",
        "Part 1 - Hearing impairment": "/Off",
        "Part 1 - Other special accommodations (Please describe below)": "/Off",
        "Part 1 - Other special accommodations": "",
        
        # Part 2 - Representative Information
        "Part 2 - Given name": "Jane",
        "Part 2 - Middle name (optional)": "Elizabeth",
        "Part 2 - Family name": "Smith",
        "Part 2 - Preferred name(s) (optional)": "",
        "Part 2 - Preference for being addressed (optional)": "Ms.",
        "Part 2 - Email address": "jane.smith@example.com",
        "Part 2 - Telephone number": "604-555-7890",
        "Part 2 - Alternate telephone number": "",
        "Part 2 - Street address": "456 Oak Avenue",
        "Part 2 - Apartment, suite, unit, floor etc": "Suite 200",
        "Part 2 - City": "Vancouver",
        "Part 2 - Province/Territory/State_2": "British Columbia",
        "Part 2 - Country": "Canada",
        "Part 2 - Postal Code": "V6C 2B2",
        "Part 2 - Describe the nature of the representative or third party's relationship": "Legal representative",
        
        # Part 3 - Employer Information
        "Part 3 - Business name": "ABC Company Ltd.",
        "Part 3 - Other names used by this employer": "ABC Corp, ABC Enterprises",
        "Part 3 - What does this business do": "Retail and wholesale distribution",
        "Part 3 - The business is closed": "/Off",
        "Part 3 - The business is for sale or sold": "/Off",
        "Part 3 - The employer has financial difficulties": "/Off",
        "Part 3 - You worked for, or were paid by more than 1 business": "/Off",
        "Part 3 - You were treated like an independent contractor": "/Off",
        "Part 3 - Were you provided with accommodation or housing by the employer?": "/Off",
        
        # Part 3 - Work Location
        "Part 3 - Work Location - Street address": "789 Industrial Way",
        "Part 3 - Work Location - Apartment, suite, unit, floor etc": "Unit 5",
        "Part 3 - Work Location - City": "Burnaby",
        "Part 3 - Work Location - Province/Territory/State": "British Columbia",
        "Part 3 - Work Location - Country": "Canada",
        "Part 3 - Work Location - Postal Code": "V5A 1B3",
        
        # Part 3 - Contact Information
        "Part 3 - Contact Information - Email address": "info@abccompany.com",
        "Part 3 - Contact Information - Telephone number": "604-555-1000",
        "Part 3 - Contact Information - Street address": "789 Industrial Way",
        "Part 3 - Contact Information - Apartment, suite, unit, floor etc": "Unit 5",
        "Part 3 - Contact Information - City": "Burnaby",
        "Part 3 - Contact Information - Province/Territory/State": "British Columbia",
        "Part 3 - Contact Information - Country": "Canada",
        "Part 3 - Contact Information - Postal Code": "V5A 1B3",
        
        # Part 3 - Contact Person
        "Part 3 - Contact Person - Given name": "Robert",
        "Part 3 - Contact Person - Family name": "Johnson",
        "Part 3 - Contact Person - Role": "HR Manager",
        "Part 3 - Contact Person - Email address": "robert.johnson@abccompany.com",
        "Part 3 - Contact Person - Telephone number": "604-555-1001",
        
        # Part 4 - Employment Details
        "Part 4 - Start date": "2024-01-15",
        "Part 4 - Are you still working for the employer?": "/Off",
        "Part 4 - Last day worked": "2024-10-01",
        "Part 4 - Job title": "Sales Associate",
        "Part 4 - Are you a foreign worker?": "/Off",
        "Part 4 - Which foreign worker program was used to hire you?": "",
        "Part 4 - Did you belong to a union when working for the employer?": "/Off",
        "Part 4 - Which union?": "",
        "Part 4 - Rate of pay": "$18.50 per hour",
        "Part 4 - How many hours a week did you work on average?": "/Off",
        "Part 4 - Describe your work schedule": "Monday to Friday, 9am to 5pm with one hour lunch",
        "Part 4 - Were you paid less than minimum wage?": "/Off",
        "Part 4 - Did you receive wage statements (pay stubs) from the employer?": "/Yes",
        "Part 4 - How were you paid? - Cash": "/Off",
        "Part 4 - How were you paid? - Cheque": "/Off",
        "Part 4 - How were you paid? - Direct deposit": "/Yes",
        "Part 4 - How were you paid? - E-transfer": "/Off",
        "Part 4 - How were you paid? - Other": "/Off",
        "Part 4 - If you're no longer working for the employer, why did you leave?": "/Yes",
        "Part 4 - Why did you leave? - Please describe what happened": "Position was terminated without proper notice",
        
        # Part 5 - Issues/Complaints
        "Part 5 - Regular wages": "/Yes",
        "Part 5 - Commissions": "/Off",
        "Part 5 - Overtime wages": "/Yes",
        "Part 5 - Statutory holiday pay": "/Off",
        "Part 5 - Vacation pay": "/Yes",
        "Part 5 - Business expenses or unauthorized deductions": "/Off",
        "Part 5 - Other (Please describe below)": "/Off",
        "Part 5 - Taking or returning from a leave": "/Off",
        "Part 5 - Employment ending (getting fired, laid off, quitting)": "/Yes",
        "Part 5 - Bonuses": "/Off",
        "Part 5 - Passport or other official documents withheld": "/Off",
        "Part 5 - Fees for employment or work": "/Off",
        "Part 5 - Threatened with deportation": "/Off",
        "Part 5 - Fees or expenses for recruitment services": "/Off",
        "Part 5 - Please describe below": "",
        "Part 5 - In your own words describe the situation": "I was not paid for overtime hours worked and did not receive proper termination pay.",
        
        # Part 6 - Amounts Owed
        "Part 6 - Regular wages": "$500.00",
        "Part 6 - Employment ending (getting fired, laid off, quitting)": "$1850.00",
        "Part 6 - Commissions": "$0.00",
        "Part 6 - Bonuses": "$0.00",
        "Part 6 - Overtime wages": "$750.00",
        "Part 6 - Fees for employment or work": "$0.00",
        "Part 6 - Statutory holiday pay": "$0.00",
        "Part 6 - Fees or expenses for recruitment services": "$0.00",
        "Part 6 - Vacation pay": "$400.00",
        "Part 6 - Other": "$0.00",
        "Part 6 - Business expenses or unauthorized deductions": "$0.00",
        "Part 6 - Total estimated amount owing": "$3500.00",
        "Part 6 - To help us understand your concerns, tell us anything else you think we should know about your situation": "I have documentation of all hours worked and communication regarding my termination.",
    }
    
    print("PDF Form Filler")
    print("=" * 50)
    
    try:
        # Step 1: List all fields (optional - comment out after first run)
        print("\nStep 1: Discovering form fields...")
        list_form_fields(INPUT_PDF)
        
        # Step 2: Fill the form (uncomment to use)
        print("\nStep 2: Filling the form...")
        # Option 1: Fill all pages
        fill_pdf_form(INPUT_PDF, OUTPUT_PDF, form_data, page_num=None)
        
        # Option 2: Fill specific pages only
        # fill_pdf_form(INPUT_PDF, OUTPUT_PDF, form_data, page_num=[1, 2, 3])
        
    except FileNotFoundError:
        print(f"\n❌ Error: Could not find '{INPUT_PDF}'")
        print("Please update INPUT_PDF to point to your PDF file")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()