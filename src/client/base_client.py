from abc import ABC, abstractmethod
from typing import Any

class BaseClient(ABC):
    """
        Abstract class for a client class.
    """

    @abstractmethod
    def fetch(self, protein_id, **kwargs) -> Any:
        """
        Constructor for HumanProtein.

        Args:
            protein_id (str): Protein of interest.

        Returns:
            dict: Reponse.
        """
        pass