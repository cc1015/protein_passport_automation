from enum import Enum

class Organism(Enum):
    HUMAN = 'Homo sapiens'
    MOUSE = 'Mus musculus'
    RAT = 'Rattus norvegicus'
    ALPACA = 'Vicugna pacos'
    LLAMA = 'Lama glama'
    CYNO = 'Macaca fascicularis'

    def get_search_name(self):
        if self == Organism.CYNO:
            return 'cynomolgus'
        return self.name.lower()