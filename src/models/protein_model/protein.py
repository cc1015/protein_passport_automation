from collections import defaultdict
from pathlib import Path
from abc import ABC
from models.organism import Organism
from pymol import cmd

class Protein(ABC):
    """
    Represents an abstract Protein object with sequence and structure information.

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
    """

    def __init__(self, id: str, organism: Organism, name: str, seq: str, annotations: str, pred_pdb: str, pred_pdb_content, string_id: str):
        """
        Constructor for Protein.

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
        self.id = id
        self.organism = organism
        self.name = name
        self.string_id = string_id

        project_root = Path(__file__).parent.parent.parent.parent
        self.file_name = project_root / "output" / f"{self.organism.name.lower()}_{self.name}"
        self.file_name.mkdir(parents=True, exist_ok=True)

        self._set_save_seq(seq)
        self._set_save_annotations(annotations)
        self._set_save_af_pdb(pred_pdb, pred_pdb_content)
    
    def annotate_3d_structure(self) -> str:
        """
        Annotates 3d structure of this Protein using Pymol and takes snapshot.

        Returns:
            str: Path to snapshot of annotated 3d structure.
        """
        cmd.load(self.pred_pdb)

        for annotation, regions in self.annotations.items():
            for start, end in regions:
                if annotation == "ECD" or annotation == "CHAIN":
                    color = "green"
                elif annotation == "TM" or annotation == "SIGNAL":
                    color = "red"
                elif annotation == "Cyto":
                    color = "magenta"

                cmd.color(color, f"resi {start}-{end}")
        
        cmd.orient()
        png_path = self.file_name / f"{self.name}_structure_ss.png"
        pse_path = self.file_name / f"{self.name}_annotated_structure.pse"
        cmd.png(str(png_path), width=2000, ray=1)
        cmd.save(str(pse_path))
        cmd.delete("all")
        return str(png_path)
    
    def structure_align(self, mobile_proteins) -> dict:
        """
        Aligns 3d structure of given protein against this Protein. Prioritizes aligning domains of interest with corresponding annotations. 
        If none exist, aligns according to this Protein's annotations.

        Args:
            mobile_proteins (list): the mobile proteins to align.

        Returns:
            dict: calculated RMSDs after alignment.
        """
        target_path = self.pred_pdb
        target = self.organism.name

        cmd.load(target_path, target)

        rmsd_dict = {}

        for mobile_protein in mobile_proteins:
            mobile_path = mobile_protein.pred_pdb
            mobile = mobile_protein.organism.name
            cmd.load(mobile_path, mobile)

            if ((mp_domain := mobile_protein.annotations.get('CHAIN')) 
                and len(mp_domain) == 1):
                (mobile_start, mobile_end) = mobile_protein.annotations.get('CHAIN')[0]
                (target_start, target_end) = self.annotations.get('CHAIN')[0]
            else:
                (mobile_start, mobile_end) = (target_start, target_end)

            cmd.select(f"{mobile}_sele", f"{mobile} and resi {mobile_start}-{mobile_end}")
            cmd.create(f"{mobile}_chain", f"{mobile}_sele")

            cmd.select(f"{target}_sele", f"{target} and resi {target_start}-{target_end}")
            cmd.create(f"{target}_chain", f"{target}_sele")

            mobile = f"{mobile}_chain"
            target = f"{target}_chain"
        
            result = cmd.align(f"polymer and name CA and {mobile}", f"polymer and name CA and {target}")
            mobile_protein.set_rmsd(round(result[0], 2))

            cmd.disable("all")
            cmd.enable(mobile)
            cmd.enable(target)
            cmd.color("green", target)

            png_path = mobile_protein.file_name / f"{mobile}_human_aligned_ss.png"
            pse_path = mobile_protein.file_name / f"{mobile}_human_aligned_structure.pse"
            cmd.png(str(png_path), width=2000, ray=1)
            cmd.save(str(pse_path))
            cmd.delete(f"{mobile}*")

            rmsd_dict[mobile_protein] = (str(png_path), round(result[0], 2))
        
        return rmsd_dict

    def _set_save_seq(self, seq):
        '''
        Saves sequence to .txt file and sets seq field to the path of the file.

        Args:
            seq (str): Sequence.
        '''
        seq_path = self.file_name / f"{self.organism.name}_{self.id}_seq.txt"
        seq_path.write_text(seq)
        self.seq = str(seq_path)

    def _set_save_annotations(self, annotations):
        '''
        Saves annotations to .gff file and sets annotations_path and annotations field.

        Args:
            annotations (str): Annotations.
        '''
        gff_text = annotations.splitlines()

        annotations_dict = defaultdict(list)
        renamed = []

        for line in gff_text:
            if line.startswith("#"):
                renamed.append(line)
                continue
            parts = line.split("\t")
            if len(parts) < 9:
                continue
            feature_type = parts[2]
            attributes = parts[8]

            if "Extracellular" in attributes:
                parts[2] = "ECD"
            elif "Cytoplasmic" in attributes:
                parts[2] = "Cyto"
            elif feature_type == "TRANSMEM":
                parts[2] = "TM"
            elif "signal" in feature_type.lower():
                parts[2] = "SIGNAL"
            elif "chain" in feature_type.lower():
                parts[2] = "CHAIN"
    
            annotations_dict[parts[2]].append((parts[3], parts[4]))
            renamed.append("\t".join(parts))
        
        gff_path = self.file_name / f"{self.id}_annotations.gff"
        gff_path.write_text("\n".join(renamed))
        self.annotations_path = str(gff_path)
        self.annotations = annotations_dict

    def _set_save_af_pdb(self, pdb_name, pdb_content):
        '''
        Saves PDB content to PDB file and sets pred_pdb_id and pred_pdb field.

        Args:
            pdb_name (str): PDB file name.
            pdb_content: 3d coordinates of protein.
        '''
        pdb_path = self.file_name / pdb_name
        pdb_path.write_bytes(pdb_content)
        self.pred_pdb_id = pdb_name[:-4]
        self.pred_pdb = str(pdb_path)

    