from pydantic import BaseModel
from typing import List, Optional
import json
from pathlib import Path

class Position(BaseModel):
    title: str
    start_date: str
    end_date: str
    
    def format_duration(self) -> str:
        """Format the position duration for display"""
        return f"{self.start_date} - {self.end_date}"

class Header(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    linkedin: Optional[str] = ""
    
    def format_contact_info(self) -> str:
        """Format the contact info for display"""
        contact_parts = [self.email, self.phone, self.address]
        if self.linkedin:
            contact_parts.append(self.linkedin)
        return " • ".join(contact_parts)

class Education(BaseModel):
    institution: str
    course: str
    location: str
    start_date: str
    end_date: str

class Experience(BaseModel):
    company: str
    location: str
    description: List[str]
    positions: List[Position]

class Project(BaseModel):
    title: str
    description: str
    link: Optional[str] = ""

class SkillElement(BaseModel):
    title: str
    elements: List[str]

class ResumeData(BaseModel):
    header: Header
    education: List[Education]
    experience: List[Experience]
    projects: Optional[List[Project]] = []
    skills: List[SkillElement]
    
    @classmethod
    def from_file(cls, filepath: str) -> 'ResumeData':
        """Load a ResumeData object from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls(**data)
    
    def save_to_file(self, filepath: str) -> None:
        """Save this resume data to a JSON file."""
        with open(filepath, 'w') as f:
            f.write(self.model_dump_json(indent=4))
            
    def get_output_filename(self) -> str:
        """Generate an output filename based on the person's name."""
        return f"{self.header.name.lower().replace(' ', '_')}_resume.pdf"
    skills: List[SkillElement]
