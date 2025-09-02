from models.protein_model.protein import Protein
from models.organism import Organism
import subprocess

class HumanProtein(Protein):

    def __init__(self, id: str, organism: Organism, name: str, seq: str, annotations: str, pred_pdb: str, 
                 pred_pdb_content, length: int, mass: float, rec_name: str, target_type: str, 
                 known_activity: str, exp_pattern: str, string_id: str, aliases: list | None = None, exp_pdbs: list | None = None):
        super().__init__(id=id, organism=organism, name=name, seq=seq, annotations=annotations, pred_pdb=pred_pdb, 
                         pred_pdb_content=pred_pdb_content, string_id=string_id)
        self.length = length
        self.mass = mass
        self.rec_name = rec_name
        self.target_type = target_type
        self.aliases = aliases
        self.exp_pdbs = exp_pdbs
        self.known_activity = known_activity
        self.exp_pattern = exp_pattern
    
    # uses geneious prime to annotate and muscle align this protein's sequence with given, saves to .geneious file
    def annotate_align_seq_geneious(self, proteins):
        output_file = self.file_name / "output.geneious"

        annotate_command = ["geneious", "-i", self.seq, self.annotations_path, "-o", str(output_file)]
        result = subprocess.run(annotate_command, capture_output=True, text=True)

        protein_seq_paths = [p.file_name / f"{p.id}_seq.txt" for p in proteins]

        align_command = ["geneious", "-i", str(output_file), 
                         *map(str, protein_seq_paths), "-o", str(output_file),
                         "--operation", "muscle_alignment"]
        result = subprocess.run(align_command, capture_output=True, text=True)
        return result.stdout, result.stderr

        

