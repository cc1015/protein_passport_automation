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
        seq (str): Path to .fasta containing amino acid sequence.
        annotations (dict): Protein annotations.
        annotations_path (str): Path to .gff containing annotations.
        pred_pdb (str): Path to predicted structure PDB.
        pred_pdb_id (str): AlphaFold ID.
        structure_file (str): Path to PDB file.
        passport_table_data (dict): Data to fill the info table for protein passport.
        fasta (str): FASTA sequence.
    """

    def __init__(self, id: str, name: str, seq: str, annotations: str, pred_pdb: str, 
                 pred_pdb_content, length: int, mass: float, rec_name: str, target_type: str, 
                 known_activity: str, exp_pattern: str, string_id: str, fasta: str, aliases: list | None = None, exp_pdbs: list | None = None):
        """
        Constructor for HumanProtein.

        Args:
            id (str): UniProt ID.
            name (str): Name of protein.
            seq (str): Path to .fasta containing amino acid sequence.
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
            fasta (str): FASTA sequence.
        """
        super().__init__(id=id, organism=Organism.HUMAN, name=name, seq=seq, annotations=annotations, pred_pdb=pred_pdb, 
                         pred_pdb_content=pred_pdb_content, string_id=string_id, fasta=fasta)
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
    
    @classmethod
    def from_uniprot_result(cls, protein_name, uniprot_results, af_results, annotations_text, fasta):
        id=uniprot_results['primaryAccession']
        name=protein_name
        seq=uniprot_results['sequence']['value']
        pred_pdb = af_results['file_name']
        pred_pdb_content = af_results['content']

        rec_name=uniprot_results['proteinDescription']['recommendedName']['fullName']['value']
        aliases = [item["fullName"]["value"] for item in uniprot_results.get("proteinDescription", {}).get("alternativeNames", [])] or ""
        length=uniprot_results['sequence']['length']
        mass=round(uniprot_results['sequence']['molWeight'] * 10**-3, 1)
        exp_pdbs=[entry["id"] for entry in uniprot_results['uniProtKBCrossReferences'] if entry["database"] == "PDB"]
        string_id=[entry["id"] for entry in uniprot_results['uniProtKBCrossReferences'] if entry["database"] == "STRING"]
                
        comments=uniprot_results['comments']
                
        subcellular_location = next((d for d in comments if d.get('commentType') == 'SUBCELLULAR LOCATION'), None)
        if subcellular_location:
            locations = subcellular_location.get('subcellularLocations', [])
            if locations[0].get('topology'):
                subcellular_location = locations[0].get('topology').get('value')
            else:
                subcellular_location = ""
                            
        function = next((d for d in comments if d.get('commentType') == 'FUNCTION'), None)
        if function:
            texts = function.get('texts', [])
            if texts:
                function = texts[0].get('value')
                
        tissue_specificity = next((d for d in comments if d.get('commentType') == 'TISSUE SPECIFICITY'), None)
        if tissue_specificity:
            texts = tissue_specificity.get('texts', [])
            if texts:
                tissue_specificity = texts[0].get('value')

        return cls(id=id,
                   name=name,
                   rec_name=rec_name,
                   aliases=aliases,
                   length=length,
                   mass=mass,
                   target_type=subcellular_location,
                   exp_pdbs=exp_pdbs,
                   pred_pdb=pred_pdb,
                   pred_pdb_content=pred_pdb_content,
                   seq=seq,
                   annotations=annotations_text,
                   known_activity=function,
                   exp_pattern=tissue_specificity,
                   string_id=string_id,
                   fasta=fasta)
    
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

        protein_seq_paths = [p.file_name / f"{p.organism.name}_{p.id}_seq.fasta" for p in proteins]

        align_command = ["geneious", "-i", str(seq_output_file), 
                         *map(str, protein_seq_paths), "-o", str(align_output_file),
                         "--operation", "muscle_alignment"]
        subprocess.run(align_command, capture_output=True, text=True)

        

