from typing import Dict, List, Set
from pydantic import BaseModel, Field

class FileIndexEntry(BaseModel):
    file_path: str
    file_type: str # e.g., 'source_code', 'documentation', 'configuration'
    language: str = "Unknown"
    hash: str = "" # For detecting changes
    symbols: List[str] = Field(default_factory=list) # List of qualnames defined in this file

class RepositoryIndex(BaseModel):
    """
    Central index of the repository to prevent redundant scanning of files
    and provide quick lookups.
    """
    files: Dict[str, FileIndexEntry] = Field(default_factory=dict)
    directories: Set[str] = Field(default_factory=set)
    
    def add_file(self, entry: FileIndexEntry) -> None:
        self.files[entry.file_path] = entry
        
        # Add parent directories to the directory set
        parts = entry.file_path.split('/')
        for i in range(1, len(parts)):
            self.directories.add('/'.join(parts[:i]))
            
    def get_file(self, file_path: str) -> FileIndexEntry | None:
        return self.files.get(file_path)
        
    def has_file(self, file_path: str) -> bool:
        return file_path in self.files
        
    def get_files_by_type(self, file_type: str) -> List[FileIndexEntry]:
        return [f for f in self.files.values() if f.file_type == file_type]
