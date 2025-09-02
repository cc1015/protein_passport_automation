from abc import ABC, abstractmethod

class BaseClient(ABC):

    # returns database entry for given protein id
    @abstractmethod
    def fetch(self, protein_id, **kwargs):
        pass