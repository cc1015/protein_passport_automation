from collections import defaultdict
from pathlib import Path
from abc import ABC
from models.organism import Organism
from pymol import cmd

class Protein(ABC):

    def __init__(self, id: str, organism: Organism, name: str, seq: str, annotations: str, pred_pdb: str, pred_pdb_content, string_id: str):
        self.id = id
        self.organism = organism
        self.name = name
        self.string_id = string_id

        project_root = Path(__file__).parent.parent.parent.parent
        self.file_name = project_root / "output" / f"{self.organism.value.replace(' ', '_')}_{self.name}"
        self.file_name.mkdir(parents=True, exist_ok=True)

        self._set_save_seq(seq)
        self._set_save_annotations(annotations)
        self._set_save_af_pdb(pred_pdb, pred_pdb_content)
    
    # colors 3d structure and saves snapshot
    def annotate_3d_structure(self):
        cmd.load(self.pred_pdb)

        for annotation, regions in self.annotations.items():
            for start, end in regions:
                if annotation == "ECD":
                    color = "green"
                elif annotation == "TM":
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
    
    # structure align with this protein as target and return rmsd
    def structure_align(self, mobile_proteins):
        target_path = self.pred_pdb
        target = self.organism.name

        cmd.load(target_path, target)

        rmsd_dict = {}

        for mobile_protein in mobile_proteins:
            if ((mp_ecd := mobile_protein.annotations.get('ECD')) 
                and len(mp_ecd) == 1
                and (self_ecd := self.annotations.get('ECD')) 
                and len(self_ecd) == 1):
                mobile_path = mobile_protein.pred_pdb
                mobile = mobile_protein.organism.name
                cmd.load(mobile_path, mobile)

                (mobile_start, mobile_end) = mobile_protein.annotations.get('ECD')[0]
                (target_start, target_end) = self.annotations.get('ECD')[0]

                cmd.select(f"{mobile}_sele", f"{mobile} and resi {mobile_start}-{mobile_end}")
                cmd.create(f"{mobile}_ecd", f"{mobile}_sele")

                cmd.select(f"{target}_sele", f"{target} and resi {target_start}-{target_end}")
                cmd.create(f"{target}_ecd", f"{target}_sele")

                mobile = f"{mobile}_ecd"
                target = f"{target}_ecd"
        
                result = cmd.align(f"polymer and name CA and {mobile}", f"polymer and name CA and {target}")
                mobile_protein.set_ecd_rmsd(round(result[0], 2))

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

    # sets and saves seq .txt file
    def _set_save_seq(self, seq):
        seq_path = self.file_name / f"{self.organism.name}_{self.id}_seq.txt"
        seq_path.write_text(seq)
        self.seq = str(seq_path)

    # sets annotation field and saves .gff file
    def _set_save_annotations(self, annotations):
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
    
            annotations_dict[parts[2]].append((parts[3], parts[4]))
            renamed.append("\t".join(parts))
        
        gff_path = self.file_name / f"{self.id}_annotations.gff"
        gff_path.write_text("\n".join(renamed))
        self.annotations_path = str(gff_path)
        self.annotations = annotations_dict

    # saves af .pdb
    def _set_save_af_pdb(self, pdb_name, pdb_content):
        pdb_path = self.file_name / pdb_name
        pdb_path.write_bytes(pdb_content)
        self.pred_pdb_id = pdb_name
        self.pred_pdb = str(pdb_path)

    