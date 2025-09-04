import argparse
from pathlib import Path
from client.uniprot_client import UniProtClient
from client.proteins_client import ProteinsClient
from client.alphafold_client import AlphaFoldClient
from client.string_client import StringClient
from models.protein_model.human_protein import HumanProtein
from models.protein_model.ortholog import Ortholog
from models.protein_model.protein import Protein
from models.organism import Organism
from models.entry import Entry
from models.image import Img

def _uniprot_input(protein_name, protein_id) -> dict:
    uniprot_data = {o: None for o in Organism}

    uniprot_client = UniProtClient()
    human_data =  uniprot_client.fetch(protein_id, kb=True)
    uniprot_data[Organism.HUMAN] = human_data
    uniref_data = uniprot_client.fetch(protein_id, ref=True)
    
    protein_name = human_data['genes'][0]['geneName']['value']

    orthologs = list(Organism)

    for result in uniref_data['results']:
        match = next((o for o in orthologs if result['organismTaxId'] == o.value[1]), None)

        if match:
            match_id = result['accessions'][0]
            r = uniprot_client.fetch(protein_id=match_id, kb=True)
            if r and (match in uniprot_data):
                uniprot_data[match] = r
                orthologs.remove(match)

    for organism in orthologs:
        r = uniprot_client.fetch(protein_id=protein_name, organism=organism.value[1], kb=True, search=True)
        if r['results'] and uniprot_data[organism] == None:
            uniprot_data[organism] = r['results'][0]
    return uniprot_data

def _get_annotations_text(protein_id) -> str:
    annotations_client = ProteinsClient()
    return annotations_client.fetch(protein_id=protein_id)

def _get_af_pdb(protein_id) -> dict:
    af_client = AlphaFoldClient()
    return af_client.fetch(protein_id=protein_id)

def _create_proteins(protein_name, protein_id) -> dict[Organism, Protein]:
    uniprot_data = _uniprot_input(protein_name, protein_id)
    
    proteins = {}

    for organism, results in uniprot_data.items():
        if results is not None:
            id=results['primaryAccession']
            name=protein_name
            seq=results['sequence']['value']
            annotations_text = _get_annotations_text(results['primaryAccession'])

            af_pdb = _get_af_pdb(results['primaryAccession'])
            pred_pdb = af_pdb['file_name']
            pred_pdb_content = af_pdb['content']

            if organism == Organism.HUMAN:
                rec_name=results['proteinDescription']['recommendedName']['fullName']['value']
                aliases=[item["fullName"]["value"] for item in results['proteinDescription']['alternativeNames']]
                length=results['sequence']['length']
                mass=round(results['sequence']['molWeight'] * 10**-3, 1)
                target_type="NA"#results['comments'][1]['subcellularLocations'][0]['topology']['value']
                exp_pdbs=[entry["id"] for entry in results['uniProtKBCrossReferences'] if entry["database"] == "PDB"]
                known_activity=results['comments'][0]['texts'][0]['value']
                exp_pattern=results['comments'][2]['texts'][0]['value']
                string_id=[entry["id"] for entry in results['uniProtKBCrossReferences'] if entry["database"] == "STRING"]

                protein = HumanProtein(id=id, 
                          name=name, 
                          rec_name=rec_name,
                          aliases=aliases,
                          length=length,
                          mass=mass,
                          target_type=target_type,
                          exp_pdbs=exp_pdbs,
                          pred_pdb=pred_pdb,
                          pred_pdb_content=pred_pdb_content,
                          seq=seq,
                          annotations=annotations_text,
                          known_activity=known_activity,
                          exp_pattern=exp_pattern,
                          string_id=string_id)
        
            else:
                protein = Ortholog(id=id, 
                          organism=organism, 
                          name=name, 
                          pred_pdb=pred_pdb,
                          pred_pdb_content=pred_pdb_content,
                          seq=seq,
                          annotations=annotations_text,
                          string_id=string_id)
        
            proteins[organism] = protein
    
    return proteins

def _get_string_db_interactions(protein_id):
    string_client = StringClient()
    return string_client.fetch(protein_id)
    
def main():
    parser = argparse.ArgumentParser(description="Protein passport automation")

    parser.add_argument("protein_name", help="Name of protein")
    parser.add_argument("protein_id", help="UnitProt ID of protein")
    parser.add_argument("first_name", help="Your first name")
    parser.add_argument("last_name", help="Your last name")

    args = parser.parse_args()
    protein_name = args.protein_name
    protein_id = args.protein_id
    first_name = args.first_name
    last_name = args.last_name

    print(f"Retrieving information for {protein_name}...")
    proteins = _create_proteins(protein_name, protein_id)
    human = proteins.get(Organism.HUMAN)
    orthologs = [protein for organism, protein in proteins.items() if organism != Organism.HUMAN]

    print("Annotating and aligning sequences...")
    human.annotate_align_seq_geneious(orthologs)

    print("Performing structural alignment...")
    annotated_img_path = human.annotate_3d_structure()
    slide_1_img = Img(annotated_img_path, caption=human.pred_pdb_id)

    rmsd_map = human.structure_align(orthologs)
    import pdb; pdb.set_trace();
    top_two = sorted(rmsd_map.items(), key=lambda x: x[1][1])[:2]
    slide_3_imgs = []
    for ortholog, (img_path, rmsd) in top_two:
        slide_3_imgs.append(Img(img_path, caption="Human:" + ortholog.organism.name.capitalize() + "\nRMSD: " + str(rmsd) + "Å"))
    
    slide_4_img = _get_string_db_interactions(human.string_id)

    print("Creating powerpoint...")
    template_path = Path(__file__).parent.parent / "assets" / "template.pptx"
    entry = Entry(template_path=template_path, human=human, orthologs=orthologs, user_name=f"{first_name} {last_name}")
    entry.populate_info_table_slide(slide_1_img)
    entry.populate_str_align_slide(slide_3_imgs)
    entry.populate_string_db_slide(slide_4_img)

    print("Completed")
    

if __name__ == "__main__":
    main()