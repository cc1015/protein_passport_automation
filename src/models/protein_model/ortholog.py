from models.protein_model.protein import Protein
from models.organism import Organism

class Ortholog(Protein):
    def __init__(self, id: str, organism: Organism, name: str, seq: str, annotations: str, pred_pdb: str, 
                 pred_pdb_content, string_id: str):
        super().__init__(id=id, organism=organism, name=name, seq=seq, annotations=annotations, pred_pdb=pred_pdb, 
                         pred_pdb_content=pred_pdb_content, string_id=string_id)
        self.ecd_similarity = None
    
    def set_similarity(self, ecd_similarity: float):
        self.ecd_similarity = ecd_similarity
    
    def set_ecd_rmsd(self, ecd_rmsd: float):
        self.ecd_rmsd = ecd_rmsd