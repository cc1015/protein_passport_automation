from models.protein_model.protein import Protein
from models.organism import Organism
import subprocess

class HumanProtein(Protein):
    """
    Represents a human protein with sequence and structure information.

    Attributes:
        id (str): UniProt ID.
        organism (Organism): Organism of protein (human).
        name (str): Name of protein.
        string_id (str): STRING database ID.
        file_name (Path): Path to this protein's directory.
        seq (str): Path to .txt containing amino acid sequence.
        annotations (dict): Protein annotations.
        annotations_path (str): Path to .gff containing annotations.
        pred_pdb (str): Path to predicted structure PDB.
        pred_pdb_id (str): AlphaFold ID.
        structure_file (str): Path to PDB file.
        passport_table_data (dict): Data to fill the info table for protein passport.
    """

    def __init__(self, id: str, name: str, seq: str, annotations: str, pred_pdb: str, 
                 pred_pdb_content, length: int, mass: float, rec_name: str, target_type: str, 
                 known_activity: str, exp_pattern: str, string_id: str, aliases: list | None = None, exp_pdbs: list | None = None):
        """
        Constructor for HumanProtein.

        Args:
            id (str): UniProt ID.
            name (str): Name of protein.
            seq (str): Path to .txt containing amino acid sequence.
            annotations (str): Protein annotations.
            pred_pdb (str): Path to predicted structure PDB.
            pred_pdb_content: 3d coordinates of protein.
            length (int): Length of protein (#aa).
            mass (float): Mass of protein (kDa).
            rec_name (str): Recommended name.
            target_type (str): Protein target type.
            known_activity (str): Known activity of protein.
            exp_pattern (str): Expression pattern of protein.
            string_id (str): STRING database ID.
            aliases (list): Aliases for protein.
            exp_pdbs (list): Experimental PDBs.
        """
        super().__init__(id=id, organism=Organism.HUMAN, name=name, seq=seq, annotations=annotations, pred_pdb=pred_pdb, 
                         pred_pdb_content=pred_pdb_content, string_id=string_id)
        self.passport_table_data = {
            "rec_name": rec_name,
            "aliases": aliases,
            "gene_id": name,
            "length": length,
            "mass": mass,
            "target_type": target_type,
            "exp_pdbs": exp_pdbs,
            "known_activity": known_activity,
            "exp_pattern": exp_pattern
        }
    
    def annotate_align_seq_geneious(self, proteins: list):
        """
        Annotates and aligns the given proteins against this HumanProtein using GeneiousPrime. 
        Creates output .geneious files containing annotations and alignment.

        Args:
            proteins (list): Proteins to be annotated and aligned against this HumanProtein.
        """
        seq_output_file = self.file_name.parent / "annotated_seq_human.geneious"
        align_output_file = self.file_name.parent / "alignment.geneious"

        annotate_command = ["geneious", "-i", self.seq, self.annotations_path, "-o", str(seq_output_file)]
        subprocess.run(annotate_command, capture_output=True, text=True)

        protein_seq_paths = [p.file_name / f"{p.organism.name}_{p.id}_seq.txt" for p in proteins]

        align_command = ["geneious", "-i", str(seq_output_file), 
                         *map(str, protein_seq_paths), "-o", str(align_output_file),
                         "--operation", "muscle_alignment"]
        subprocess.run(align_command, capture_output=True, text=True)

        

