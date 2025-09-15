import argparse
import csv
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

def _uniprot_query(protein_name, protein_id) -> dict:
    uniprot_data = {o: None for o in Organism}

    uniprot_client = UniProtClient()
    human_data =  uniprot_client.fetch(protein_id, kb=True)
    uniprot_data[Organism.HUMAN] = human_data
    uniref_data = uniprot_client.fetch(protein_id, ref=True)
    
    protein_name = human_data['genes'][0]['geneName']['value']
    rec_name=human_data['proteinDescription']['recommendedName']['fullName']['value']

    orthologs = list(Organism)

    if uniref_data.get('results'):
        for result in uniref_data['results']:
            match = next((o for o in orthologs if result['organismTaxId'] == o.value[1] and result['proteinName'] == rec_name), None)

            if match:
                match_id = result['accessions'][0]
                uniref_r = uniprot_client.fetch(protein_id=match_id, kb=True)
                search_r = uniprot_client.fetch(protein_id=rec_name, gene=protein_name, organism=match.value[1], kb=True, search=True)
                if uniref_r['primaryAccession'] == search_r['results'][0]['primaryAccession']:
                    uniprot_data[match] = uniref_r
                else:
                    chosen_ortholog = _choose_ortholog_selection(organism_str=match.name, uniref_accessions=result['accessions'], search=search_r['results'])
                    uniprot_data[match] = uniprot_client.fetch(chosen_ortholog, kb=True)
                orthologs.remove(match)
            if not orthologs: break

    for organism in orthologs:
        r = uniprot_client.fetch(protein_id=rec_name, gene=protein_name, organism=organism.value[1], kb=True, search=True)
        if r['results']:
            uniprot_data[organism] = r['results'][0]
    
    return uniprot_data

def _get_fasta_content(protein_id) -> str:
    uniprot_client = UniProtClient()
    return uniprot_client.fetch(protein_id=protein_id, fasta=True)
    
def _get_annotations_text(protein_id) -> str:
    annotations_client = ProteinsClient()
    return annotations_client.fetch(protein_id=protein_id)

def _get_af_pdb(protein_id) -> dict:
    af_client = AlphaFoldClient()
    return af_client.fetch(protein_id=protein_id)

def _get_string_db_interactions(protein_name, string_id):
    string_client = StringClient()
    return string_client.fetch(protein_name, string_id=string_id)

def _create_proteins(uniprot_data, protein_name) -> dict[Organism, Protein]:
    proteins = {}

    for organism, results in uniprot_data.items():
        if results is not None:
            fasta = _get_fasta_content(results['primaryAccession'])
            annotations_text = _get_annotations_text(results['primaryAccession'])
            af_pdb = _get_af_pdb(results['primaryAccession'])
            
            if af_pdb:
                if organism == Organism.HUMAN:
                    protein = HumanProtein.from_uniprot_result(protein_name=protein_name, uniprot_results=results, af_results=af_pdb, annotations_text=annotations_text, fasta=fasta)
                else:
                    protein = Ortholog.from_uniprot_result(protein_name=protein_name, uniprot_results=results, af_results=af_pdb, annotations_text=annotations_text, organism=organism, fasta=fasta)
        
            proteins[organism] = protein
    
    return proteins

def _choose_ortholog_selection(organism_str, uniref_accessions, search):
    prompt = f"Found multiple {organism_str} orthologs. Please select the desired ortholog from the following:\n"
    for uniref_accession in uniref_accessions:
        prompt += f"{uniref_accession}\n"
    for entry in search:
        prompt += f"{entry['primaryAccession']}\n"
    return input(prompt+"Chosen ortholog: ").strip().lower()

def _confirm_ortholog_selection(orthologs):
    while True:
        prompt = f"Using the following orthologs to create Protein Passport:\n"
    
        for organism, data in orthologs.items():
            prompt += f"{organism.name}: {data['primaryAccession']}\n"
    
        prompt += "Press \'y\' if you would like to continue with these orthologs. If incorrect orthologs are present, press \'c\' to enter orthologs manually: "
    
        response = input(prompt).strip().lower()
    
        if response == 'y':
            return orthologs
        elif response == 'c':
            orthologs = _custom_orthologs()
        
def _custom_orthologs():
    uniprot_data = {o: None for o in Organism}
    for organism in Organism:
        protein_id = input(f"Please enter desired {organism.name} UniProt Accession (enter nothing for no ortholog): ").strip()
        uniprot_client = UniProtClient()
        data =  uniprot_client.fetch(protein_id, kb=True)
        if data:
            uniprot_data[organism] = data
    return uniprot_data
        

def _run(protein_id, protein_name, first_name, last_name):
    print(f"Retrieving information for {protein_name}...")
    uniprot_data = _uniprot_query(protein_name=protein_name, protein_id=protein_id)
    
    #confirmed_orthologs = _confirm_ortholog_selection(uniprot_data)
    
    proteins = _create_proteins(uniprot_data=uniprot_data, protein_name=protein_name)
    human = proteins.get(Organism.HUMAN)
    orthologs = [protein for organism, protein in proteins.items() if organism != Organism.HUMAN]

    print("Annotating and aligning sequences...")
    human.annotate_align_seq_geneious(orthologs)

    print("Performing structural alignment...")
    annotated_img_path = human.annotate_3d_structure()
    slide_1_img = Img(annotated_img_path, caption=human.pred_pdb_id)

    rmsd_map = human.structure_align(orthologs)
    slide_3_imgs = []
    for ortholog, (img_path, rmsd) in rmsd_map.items():
        slide_3_imgs.append(Img(img_path, caption="Human:" + ortholog.organism.name.capitalize() + "\nRMSD: " + str(rmsd) + "Å"))
    
    
    slide_4_img = _get_string_db_interactions(protein_name, human.string_id)

    print("Creating powerpoint...")
    template_path = Path(__file__).parent.parent / "assets" / "template.pptx"
    entry = Entry(template_path=template_path, human=human, orthologs=orthologs, user_name=f"{first_name} {last_name}")
    entry.populate_info_table_slide(slide_1_img)
    entry.populate_str_align_slide(slide_3_imgs)
    entry.populate_string_db_slide(slide_4_img)

    print("Completed")
    
def main():
    parser = argparse.ArgumentParser(description="Protein passport automation")
    
    parser.add_argument("first_name", help="Your first name")
    parser.add_argument("last_name", help="Your last name")

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--csv",
        help="Path to CSV file with columns: protein_name, protein_id"
    )

    group.add_argument(
        "--manual",
        nargs=2,
        metavar=("protein_name", "protein_id"),
        help="Provide protein_name and protein_id directly"
    )

    args = parser.parse_args()

    proteins = []

    if args.csv:
        with open(args.csv, newline="") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) >= 2:  
                    proteins.append((row[0].strip(), row[1].strip()))
    elif args.manual:
        protein_name, protein_id = args.manual
        proteins.append((protein_name, protein_id))

    for protein_name, protein_id in proteins:
        _run(protein_id, protein_name, args.first_name, args.last_name)
    

if __name__ == "__main__":
    main()