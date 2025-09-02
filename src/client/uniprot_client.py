import requests, sys
from client.base_client import BaseClient

class UniProtClient(BaseClient):
    BASE_URL = "https://www.ebi.ac.uk/proteins/api"

    # returns UniProt data for given protein id
    def fetch(self, protein_id, **kwargs):
        url = f"{self.BASE_URL}/features/{protein_id}?categories=TOPOLOGY"
        headers = { "Accept" : "text/x-gff"}

        r = requests.get(url, headers=headers)

        if not r.ok:
            r.raise_for_status()
            sys.exit()
        
        return r.text