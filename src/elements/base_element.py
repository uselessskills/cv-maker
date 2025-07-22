from pydantic import BaseModel
from typing import Protocol, TypeVar, Generic, Any

T = TypeVar('T', bound=BaseModel)

class ResumeElement(Protocol):
    """Protocol defining the interface for all resume elements."""
    def get_table_element(self, running_row_index: list, table_styles: list) -> list:
        """Generate a table representation of this element."""
        ...

class ModelAdapter(Generic[T]):
    """
    Base adapter class that wraps a Pydantic model and provides
    the interface needed for rendering resume elements.
    """
    def __init__(self, model: T):
        self.model = model
    
    def get_model(self) -> T:
        return self.model
    
    def model_dict(self) -> dict[str, Any]:
        """Get the model data as a dictionary."""
        return self.model.model_dump()
