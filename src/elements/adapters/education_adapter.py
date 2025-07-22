from reportlab.platypus import Paragraph
from constants.resume_constants import (
    COMPANY_HEADING_PARAGRAPH_STYLE, 
    COMPANY_DURATION_PARAGRAPH_STYLE, 
    COMPANY_TITLE_PARAGRAPH_STYLE, 
    COMPANY_LOCATION_PARAGRAPH_STYLE
)
from models.resume_models import Education
from elements.base_element import ModelAdapter

class EducationAdapter(ModelAdapter[Education]):
    """Adapter for Education models that implements the resume element interface."""
    
    def get_table_element(self, running_row_index: list, table_styles: list) -> list:
        education_table = []
        model = self.model
        
        education_table.append([
            Paragraph(model.institution, COMPANY_HEADING_PARAGRAPH_STYLE),
            Paragraph(model.location, COMPANY_LOCATION_PARAGRAPH_STYLE)
        ])
        table_styles.append(('TOPPADDING', (0, running_row_index[0]), (1, running_row_index[0]), 5))
        running_row_index[0] += 1
        
        education_table.append([
            Paragraph(model.course, COMPANY_TITLE_PARAGRAPH_STYLE),
            Paragraph(f"{model.start_date} - {model.end_date}", COMPANY_DURATION_PARAGRAPH_STYLE)
        ])
        table_styles.append(('TOPPADDING', (0, running_row_index[0]), (1, running_row_index[0]), 1))
        running_row_index[0] += 1
        
        return education_table
