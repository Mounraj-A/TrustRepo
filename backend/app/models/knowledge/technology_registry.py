from typing import List


class TechnologyRegistry:
    @classmethod
    def get_all_technologies(cls) -> List[str]:
        return ["React", "Angular", "Vue", "Spring Boot", "FastAPI",
                "Django", "Flask", "Express", ".NET", "Go", "Rust"]
