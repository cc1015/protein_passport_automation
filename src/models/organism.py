from enum import Enum

class Organism(Enum):
    """
    Represents an organism.
    """
    HUMAN = ('Homo sapiens', 9606)
    MOUSE = ('Mus musculus', 10090)
    RAT = ('Rattus norvegicus', 10116)
    ALPACA = ('Vicugna pacos', 30538)
    LLAMA = ('Lama glama', 9844)
    CYNO = ('Macaca fascicularis', 9541)