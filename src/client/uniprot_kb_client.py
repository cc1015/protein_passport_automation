import requests, sys
from client.base_client import BaseClient

class UniProtKBClient(BaseClient):
    BASE_URL = "https://rest.uniprot.org/uniprotkb"

    # returns UniProt data for give accession
    def fetch(self, protein_id, **kwargs):
        params = {
                "fields": [
                    "accession",
                    "protein_name",
                    "organism_name",
                    "sequence",
                    "mass",
                    "cc_subcellular_location",
                    "xref_pdb",
                    "cc_function",
                    "cc_tissue_specificity",
                    "xref_string"]
                    }
        headers = {
                "accept": "application/json"
                }
        
        r = requests.get('/'.join([self.BASE_URL, protein_id]), headers=headers, params=params)

        if not r.ok:
            r.raise_for_status()
            sys.exit()

        data = r.json()
        
        return data