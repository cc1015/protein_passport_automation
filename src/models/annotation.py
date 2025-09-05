from enum import Enum

class Annotation(Enum):
    """
    Represents an annotation type.
    """
    ECD = ("TOPO_DOM", "green", "Extracellular")
    CHAIN = ("CHAIN", "cyan")
    TM = ("TRANSMEM", "red")
    SIGNAL = ("SIGNAL", "yellow")
    CYTO = ("TOPO_DOM", "magenta", "Cytoplasmic")

    def __init__(self, feature, color, attr=None):
        self.feature = feature
        self.color = color
        self.attr = attr