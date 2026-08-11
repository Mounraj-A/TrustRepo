from typing import List


class FeatureRegistry:
    @classmethod
    def get_all_features(cls) -> List[str]:
        return ["Authentication", "Authorization", "Data Persistence",
                "Caching", "Logging", "Monitoring", "Routing", "Templating"]
