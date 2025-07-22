from reportlab.platypus import Paragraph
from constants.resume_constants import JOB_DETAILS_PARAGRAPH_STYLE
from models.resume_models import SkillElement
from elements.base_element import ModelAdapter

class SkillAdapter(ModelAdapter[SkillElement]):
    """Adapter for Skill models that implements the resume element interface."""
    
    def get_table_element(self, running_row_index: list, table_styles: list) -> list:
        skill_table = []
        model = self.model
        
        # Format the same way as the original Skill class - title in bold followed by comma-separated elements
        skill_table.append([
            Paragraph(f"<font face='Garamond_Semibold'>{model.title}:</font> {', '.join(word for word in model.elements if word)}", bulletText='•', style=JOB_DETAILS_PARAGRAPH_STYLE)
        ])
        table_styles.append(('TOPPADDING', (0, running_row_index[0]), (1, running_row_index[0]), 1))
        table_styles.append(('BOTTOMPADDING', (0, running_row_index[0]), (1, running_row_index[0]), 0))
        table_styles.append(('SPAN', (0, running_row_index[0]), (1, running_row_index[0])))
        running_row_index[0] += 1
        
        return skill_table
