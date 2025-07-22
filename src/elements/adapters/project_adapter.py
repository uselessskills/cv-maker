from reportlab.platypus import Paragraph
from constants.resume_constants import (
    COMPANY_HEADING_PARAGRAPH_STYLE,
    JOB_DETAILS_PARAGRAPH_STYLE
)
from models.resume_models import Project
from elements.base_element import ModelAdapter

class ProjectAdapter(ModelAdapter[Project]):
    """Adapter for Project models that implements the resume element interface."""
    
    def get_table_element(self, running_row_index: list, table_styles: list) -> list:
        project_table = []
        model = self.model
        
        # Project title
        project_table.append([
            Paragraph(model.title, COMPANY_HEADING_PARAGRAPH_STYLE),
            ""
        ])
        table_styles.append(('TOPPADDING', (0, running_row_index[0]), (1, running_row_index[0]), 5))
        table_styles.append(('SPAN', (0, running_row_index[0]), (1, running_row_index[0])))
        running_row_index[0] += 1
        
        # Project description
        project_table.append([
            Paragraph(model.description, JOB_DETAILS_PARAGRAPH_STYLE),
            ""
        ])
        table_styles.append(('TOPPADDING', (0, running_row_index[0]), (1, running_row_index[0]), 1))
        table_styles.append(('BOTTOMPADDING', (0, running_row_index[0]), (1, running_row_index[0]), 0))
        table_styles.append(('SPAN', (0, running_row_index[0]), (1, running_row_index[0])))
        running_row_index[0] += 1
        
        # Project link if available
        if model.link:
            project_table.append([
                Paragraph(f"Link: {model.link}", JOB_DETAILS_PARAGRAPH_STYLE),
                ""
            ])
            table_styles.append(('TOPPADDING', (0, running_row_index[0]), (1, running_row_index[0]), 1))
            table_styles.append(('BOTTOMPADDING', (0, running_row_index[0]), (1, running_row_index[0]), 0))
            table_styles.append(('SPAN', (0, running_row_index[0]), (1, running_row_index[0])))
            running_row_index[0] += 1
        
        return project_table
