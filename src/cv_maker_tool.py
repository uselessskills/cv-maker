import json
import sys
import os
import asyncio

from sections.resume_section import Section
from constants.resume_constants import RESUME_ELEMENTS_ORDER
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from constants.resume_constants import NAME_PARAGRAPH_STYLE, CONTACT_PARAGRAPH_STYLE
from constants import FULL_COLUMN_WIDTH
from models.resume_models import ResumeData
from elements import (
    EducationAdapter,
    ExperienceAdapter, 
    ProjectAdapter,
    SkillAdapter
)


# These functions are no longer needed with the adapter approach
# We use Pydantic models directly instead of converting between formats

async def generate_resume(output_file_path, author, elements, table_styles) -> None:
    resume_doc = SimpleDocTemplate(output_file_path, pagesize=A4, showBoundary=0, leftMargin = 0.5 * inch, rightMargin= 0.5 * inch, topMargin = 0.2 * inch, bottomMargin = 0.1 * inch, title = f"Resume of {author}", author = author)
    table = Table(elements, colWidths=[FULL_COLUMN_WIDTH * 0.7, FULL_COLUMN_WIDTH * 0.3], spaceBefore=0, spaceAfter=0)
    table.setStyle(TableStyle(table_styles))
    resume_elements = [table]
    resume_doc.build(resume_elements)

async def create_resume_pdf(data, output_filename: str = None) -> str:
    """
    Create a resume PDF from provided data.
    
    Args:
        data: Either a dict with resume data or a ResumeData Pydantic model
        output_filename: Optional filename for the output PDF. If None, will generate one.
        
    Returns:
        str: Path to the generated PDF file, or None if an error occurred
    """
    # Convert raw data to Pydantic model
    try:
        if isinstance(data, dict):
            resume_data = ResumeData(**data)
        else:
            # If already a Pydantic model
            resume_data = data
    except Exception as e:
        print(f"Error validating resume data: {e}")
        return None

    # Ensure the output directory exists
    # output_dir = os.path.dirname('../output/')
    # os.makedirs(output_dir, exist_ok=True)

    # Save the input data object as JSON
    output_json_path = output_filename if output_filename else resume_data.get_output_filename()
    output_json_path = f'../output/{output_json_path}.json'
    with open(output_json_path, 'w') as json_file:
        json.dump(data if isinstance(data, dict) else data.dict(), json_file, indent=4)
        
    # Extract header information from Pydantic model
    header = resume_data.header
    author = header.name
    
    # Use the helper method to generate the output path
    output_pdf_path = output_filename if output_filename else resume_data.get_output_filename()
    output_pdf_path = f'../output/{output_pdf_path}.pdf'
    
    # print(f"Processing resume for: {author}")
    # print(f"Output file: {output_pdf_path}")
    
    # Initialize all the data elements
    resume_sections = {}
    table = []
    running_row_index = [0]
    table_styles = []
    table_styles.append(('ALIGN', (0, 0), (0, -1), 'LEFT'))
    table_styles.append(('ALIGN', (1, 0), (1, -1), 'RIGHT'))
    table_styles.append(('LEFTPADDING', (0, 0), (-1, -1), 0))
    table_styles.append(('RIGHTPADDING', (0, 0), (-1, -1), 0))
    table_styles.append(('BOTTOMPADDING', (0, running_row_index[0]), (1, running_row_index[0]), 6))
    
    # Create adapters for each Pydantic model
    education_elements = [EducationAdapter(edu) for edu in resume_data.education]
    experience_elements = [ExperienceAdapter(exp) for exp in resume_data.experience]
    project_elements = [ProjectAdapter(proj) for proj in resume_data.projects] if resume_data.projects else []
    skill_elements = [SkillAdapter(skill) for skill in resume_data.skills]
    
    # Create section objects
    resume_sections['education'] = Section('Education', education_elements)
    resume_sections['experience'] = Section('Work Experience', experience_elements)
    if project_elements:
        resume_sections['projects'] = Section('Projects', project_elements)
    resume_sections['skills'] = Section('Skills', skill_elements)
    
    # Prepare a table
    # Append the name and contact
    table.append([
        Paragraph(author, NAME_PARAGRAPH_STYLE), ""
    ])
    # Span the name row across both columns
    table_styles.append(('SPAN', (0, running_row_index[0]), (1, running_row_index[0])))
    running_row_index[0] += 1
    
    # Build contact info string with LinkedIn if available
    contact_info = header.format_contact_info()
    
    table.append([
        Paragraph(contact_info, CONTACT_PARAGRAPH_STYLE), ""
    ])
    # Span the contact info row across both columns
    table_styles.append(('SPAN', (0, running_row_index[0]), (1, running_row_index[0])))
    table_styles.append(('BOTTOMPADDING', (0, running_row_index[0]), (1, running_row_index[0]), 1))
    running_row_index[0] += 1
    
    for element in RESUME_ELEMENTS_ORDER:
        if element in resume_sections:
            section_table = resume_sections[element].get_section_table(running_row_index, table_styles)
            for entry in section_table:
                table.append(entry)
    
    # Build the resume
    await generate_resume(output_pdf_path, author, table, table_styles)
    print(f"Resume generated successfully: {output_pdf_path}")
    return output_pdf_path

async def main():
    # Check for command line arguments
    if len(sys.argv) < 2:
        print("Usage: python cv_maker_tool.py <path_to_input.json>")
        print("Example: python cv_maker_tool.py ../data/input.json")
        return
    
    # Get input file path from command line argument
    file_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return
    
    # Load data from input.json and validate with Pydantic
    try:
        resume_data = ResumeData.from_file(file_path)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{file_path}': {e}")
        return
    except Exception as e:
        print(f"Error: Could not parse or validate resume data: {e}")
        return
    
    print(f"Input file: {file_path}")
    
    # Create the resume PDF
    try:
        output_path = await create_resume_pdf(resume_data)
        return output_path
    except TypeError as e:
        print(f"TypeError occurred: {e}")
        print("This may be due to data structure mismatch between Pydantic models and expected formats.")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"Error creating resume: {e}")
        import traceback
        traceback.print_exc()
    
    return None

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())