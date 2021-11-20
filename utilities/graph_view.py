from dataclasses import dataclass


@dataclass
class GraphView:
    type: str
    keywords: dict

    def __str__(self):
        return f"GraphView[type: {self.type}, keywords: {self.keywords}]"

