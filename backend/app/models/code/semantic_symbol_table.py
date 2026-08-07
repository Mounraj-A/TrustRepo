from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class SymbolEntry(BaseModel):
    name: str
    qualname: str
    type: str # e.g., 'class', 'function', 'variable'
    file_path: str
    line_number: Optional[int] = None
    references: List[str] = Field(default_factory=list) # List of qualnames that reference this symbol

class SemanticSymbolTable(BaseModel):
    """
    Explicit symbol table generation between AST and Canonical UIR.
    Maps fully qualified names (qualnames) to their symbol definitions.
    """
    symbols: Dict[str, SymbolEntry] = Field(default_factory=dict)
    
    def add_symbol(self, entry: SymbolEntry) -> None:
        self.symbols[entry.qualname] = entry
        
    def get_symbol(self, qualname: str) -> Optional[SymbolEntry]:
        return self.symbols.get(qualname)
        
    def find_by_name(self, name: str) -> List[SymbolEntry]:
        """Find symbols that match a short name."""
        return [sym for sym in self.symbols.values() if sym.name == name]
        
    def add_reference(self, target_qualname: str, source_qualname: str) -> bool:
        """Record that source_qualname references target_qualname."""
        if target_qualname in self.symbols:
            if source_qualname not in self.symbols[target_qualname].references:
                self.symbols[target_qualname].references.append(source_qualname)
            return True
        return False
        
    def resolve_reference(self, name: str, context_file: str) -> Optional[str]:
        """
        Attempt to resolve a short name to a qualname based on the file context.
        This is a simplified resolver; a real one would handle imports.
        """
        matches = self.find_by_name(name)
        if not matches:
            return None
            
        # Prefer matches in the same file
        for match in matches:
            if match.file_path == context_file:
                return match.qualname
                
        # Fallback to the first match
        return matches[0].qualname
