import requests, sys
from client.base_client import BaseClient

class UniProtSearchClient(BaseClient):
    BASE_URL = "https://rest.uniprot.org/uniprotkb/search"

    # returns UniProt search results for given protein name and organism
    def fetch(self, protein_id, **kwargs):
        params = {
                "query": f"{protein_id} AND organism_name:{kwargs.get('organism')}",
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
                    "xref_string"],
                "size": "25"
                    }
        headers = {
                "accept": "application/json"
                }
        
        r = requests.get(self.BASE_URL, headers=headers, params=params)

        if not r.ok:
            r.raise_for_status()
            sys.exit()

        data = r.json()
        
        return data