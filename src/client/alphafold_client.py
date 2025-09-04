import requests, sys
from client.base_client import BaseClient

class AlphaFoldClient(BaseClient):
    """
    Represents AlphaFold client.

    Attributes:
        BASE_URL (str): Base url.
    """
    BASE_URL = "https://alphafold.ebi.ac.uk"

    def fetch(self, protein_id: str, **kwargs) -> dict:
        """
        Gets AlphaFold PDB file of given protein.

        Args:
            protein_id (str): Protein of interest.
        
        Returns:
            dict: File name and content
        """
        url = f"{self.BASE_URL}/api/prediction/{protein_id}"
            
        r = requests.get(url)

        if not r.ok:
            r.raise_for_status()
            sys.exit()

        response_dict = r.json()[0]
        pdb_url = response_dict['pdbUrl']

        pdb_file_name = pdb_url.rsplit("/",1)[-1]

        pdb_r = requests.get(pdb_url)

        return {'file_name': pdb_file_name,
                'content': pdb_r.content}
