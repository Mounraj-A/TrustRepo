from typing import List


class CapabilityRegistry:
    @classmethod
    def get_all_capabilities(cls) -> List[str]:
        return ["Payment Processing", "User Management", "Reporting",
                "Notifications", "Search", "Data Export", "Analytics"]
