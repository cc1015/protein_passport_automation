import requests, sys, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from client.base_client import BaseClient

class UniProtClient(BaseClient):
    """
    Represents UniProt client.

    Attributes:
        BASE_URL (str): Base url.
    """
    BASE_URL = "https://rest.uniprot.org"

    def fetch(self, protein_id, **kwargs) -> dict:
        """
        Gets UniProt information.

        Args:
            protein_id (str): Protein of interest.
        
        Returns:
            dict: Uniprot data.
        """
        if kwargs.get('kb'):
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
                        "xref_string",
                        "gene_names"]
                        }
            headers = {
                    "accept": "application/json"
                    }
        
            if kwargs.get('search'):
                params["query"] = f"protein_name:{protein_id} AND gene:{kwargs.get('gene')} AND taxonomy_id:{kwargs.get('organism')}"
                path = "search"
            else:
                path = protein_id

            url = '/'.join([self.BASE_URL, "uniprotkb", path])
        elif kwargs.get('ref'):
            params = {
                "id": f"UniRef50_{protein_id}",
                "facetFilter": "member_id_type:uniprotkb_id",
                "size": "500"
                }
            headers = {
                "accept": "application/json"
                }
            
            url = '/'.join([self.BASE_URL, "uniref/%7Bid%7D/members"])
        elif kwargs.get('fasta'):
            params = {}
            headers = {}
            url = '/'.join([self.BASE_URL, "uniprotkb", protein_id + ".fasta"])
            r = requests.get(url, verify=False)
            return r.text
        
        r = requests.get(url, headers=headers, params=params, verify=False)
        
        if not r.ok:
            return {}
        
        data = r.json()
        return data
            