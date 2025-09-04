import requests, sys
from client.base_client import BaseClient

class ProteinsClient(BaseClient):
    """
    Represents AlphaFold client.

    Attributes:
        BASE_URL (str): Base url.
    """
    BASE_URL = "https://www.ebi.ac.uk/proteins/api"

    def fetch(self, protein_id, **kwargs) -> str:
        """
        Gets topology annotations of given protein.

        Args:
            protein_id (str): Protein of interest.
        
        Returns:
            str: Annotations.
        """
        url = f"{self.BASE_URL}/features/{protein_id}?categories=TOPOLOGY"
        headers = { "Accept" : "text/x-gff"}

        r = requests.get(url, headers=headers)

        if not r.ok:
            r.raise_for_status()
            sys.exit()
        
        return r.text