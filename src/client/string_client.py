import requests, sys, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from client.base_client import BaseClient
from time import sleep
from pathlib import Path

class StringClient(BaseClient):
    """
    Represents STRING client.

    Attributes:
        BASE_URL (str): Base url.
    """
    BASE_URL = "https://string-db.org/api"
    
    def fetch(self, string_id, **kwargs) -> str:
        """
        Gets STRING network image file of given protein.

        Args:
            protein_id (str): Protein of interest.
        
        Returns:
            str: Image file path.
        """
        output_format = "image"
        method = "network"
        params = {
            "identifiers" : string_id, 
            "species" : 9606, 
            "network_flavor": "confidence",
            "network_type": "physical",
            "add_color_nodes": 20
            }

        url = "/".join([self.BASE_URL, output_format, method]) 
        r = requests.post(url, data=params, verify=False)

        if not r.ok:
            r.raise_for_status()
            sys.exit()

        project_root = Path(__file__).parent.parent.parent
        output_dir = project_root / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        file_name = output_dir / "string_network.png"

        with open(file_name, 'wb') as fh:
            fh.write(r.content)
        
        sleep(1)
        
        return str(file_name)
