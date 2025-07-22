from reportlab.platypus import Paragraph
from constants.resume_constants import (
    COMPANY_HEADING_PARAGRAPH_STYLE, 
    COMPANY_DURATION_PARAGRAPH_STYLE, 
    COMPANY_TITLE_PARAGRAPH_STYLE, 
    COMPANY_LOCATION_PARAGRAPH_STYLE, 
    JOB_DETAILS_PARAGRAPH_STYLE
)
from models.resume_models import Experience
from elements.base_element import ModelAdapter

class ExperienceAdapter(ModelAdapter[Experience]):
    """Adapter for Experience models that implements the resume element interface."""
    
    def get_table_element(self, running_row_index: list, table_styles: list) -> list:
        experience_table = []
        model = self.model
        
        # First row: Company name and location
        experience_table.append([
            Paragraph(model.company, COMPANY_HEADING_PARAGRAPH_STYLE),
            Paragraph(model.location, COMPANY_LOCATION_PARAGRAPH_STYLE)
        ])
        table_styles.append(('TOPPADDING', (0, running_row_index[0]), (1, running_row_index[0]), 5))
        running_row_index[0] += 1
        
        # Add each position as a separate row
        for position in model.positions:
            experience_table.append([
                Paragraph(position.title, COMPANY_TITLE_PARAGRAPH_STYLE),
                Paragraph(f"{position.start_date} - {position.end_date}", COMPANY_DURATION_PARAGRAPH_STYLE)
            ])
            table_styles.append(('TOPPADDING', (0, running_row_index[0]), (1, running_row_index[0]), 1))
            running_row_index[0] += 1
        
        # Add all descriptions/achievements
        for line in model.description:
            experience_table.append([
                Paragraph(line, bulletText='•', style=JOB_DETAILS_PARAGRAPH_STYLE)
            ])
            table_styles.append(('TOPPADDING', (0, running_row_index[0]), (1, running_row_index[0]), 1))
            table_styles.append(('BOTTOMPADDING', (0, running_row_index[0]), (1, running_row_index[0]), 0))
            table_styles.append(('SPAN', (0, running_row_index[0]), (1, running_row_index[0])))
            running_row_index[0] += 1
        
        return experience_table
