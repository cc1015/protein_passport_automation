from models.protein_model.protein import Protein
from models.organism import Organism

class Ortholog(Protein):
    """
    Represents a non-human ortholog with sequence and structure information.

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
        similarity (float): % similarity to human protein.
        rmsd (float): RMSD of against human protein.
    """

    def __init__(self, id: str, organism: Organism, name: str, seq: str, annotations: str, pred_pdb: str, 
                 pred_pdb_content, string_id: str):
        """
        Constructor for Ortholog.

        Args:
            id (str): UniProt ID.
            organism (Organism): Organism of protein.
            name (str): Name of protein.
            seq (str): Path to .txt containing amino acid sequence.
            annotations (str): Protein annotations.
            pred_pdb (str): Path to predicted structure PDB.
            pred_pdb_content: 3d coordinates of protein.
            string_id (str): STRING database ID.
        """
        super().__init__(id=id, organism=organism, name=name, seq=seq, annotations=annotations, pred_pdb=pred_pdb, 
                         pred_pdb_content=pred_pdb_content, string_id=string_id)
        self.similarity = None
    
    def set_similarity(self, similarity: float):
        '''
        Sets similarity field.

        Args:
            similarity (float): the similarity value to set to.
        '''
        self.similarity = similarity
    
    def set_rmsd(self, rmsd: float):
        '''
        Sets rmsd field.

        Args:
            rmsd (float): the RMSD value to set to.
        '''
        self.rmsd = rmsd