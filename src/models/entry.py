from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor
from pathlib import Path
from typing import List
from models.protein_model.human_protein import HumanProtein
from models.protein_model.ortholog import Ortholog
from dataclasses import dataclass, field
from models.image import Img

@dataclass
class Entry:
    template_path: str
    human: HumanProtein
    orthologs: List[Ortholog]
    user_name: str
    powerpoint: Presentation = field(init=False)
    slides: list = field(init=False)
    table_cells: list = field(init=False)
    output_path: Path = field(init=False)

    def __post_init__(self):
        self.powerpoint = Presentation(self.template_path)
        self.slides = self.powerpoint.slides
        self.output_path = Path(__file__).parent.parent.parent / "output" / f"{self.human.name}_protein_passport.pptx"
        self.table_cells = self._build_table_cells()
        self._set_footer()

    # creates table cell info list
    def _build_table_cells(self):
        return [
            [
                "Target Name: " + self.human.rec_name,
                "Aliases: " + ", ".join(self.human.aliases),
                f"(Gene id: {self.human.name}, UniProtKB - {self.human.id})"
            ],
            [self.human.target_type],
            ["interactions"],
            [
                f"{self.human.length} aa {self.human.mass} kDa",
                'self.human.nature_info'
            ],
            [f"{o.organism.value}: {o.ecd_similarity}" for o in self.orthologs if o.ecd_similarity is not None],
            [
                f"Experimental PDBs: {', '.join(self.human.exp_pdbs)}",
                f"Predicted: {self.human.pred_pdb_id}"
            ],
            [f"{self.human.exp_pattern}."],
            [f"{self.human.known_activity}."]
        ]

    # writes name in footer
    def _set_footer(self):
        for slide in self.slides:
            for shape in slide.shapes:
                if 'Footer' in shape.name:
                    shape.text=self.user_name
                    break

    # populates table in first slide
    def populate_info_table_slide(self, img: Img):
        slide = self.slides[0]

        for shape in slide.shapes:
            if 'Title' in shape.name:
                title = shape
            if 'Picture' in shape.name:
                picture = shape
            if 'Text' in shape.name:
                pbd_id_caption = shape
            if shape.has_table:
                table = shape.table
        
        if title:
            title.text = "Protein Passport - " + self.human.name

        if picture:
            img.vertical()
            picture.insert_picture(img.path)
        
        if pbd_id_caption:
            pbd_id_caption.text = img.caption
            pbd_id_caption.text_frame.paragraphs[0].runs[0].font.size = Pt(14)
        
        if table:
            for i, cell_text in enumerate(self.table_cells):
                cell = table.cell(i, 1)
                cell.text = "\n".join(cell_text)

                for paragraph in cell.text_frame.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(14)
                        run.font.bold = False
                        run.font.color.rbg = RGBColor(0, 0, 0)

        self.powerpoint.save(self.output_path)
    
    def populate_str_align_slide(self, align_imgs, seq_img: Img=None):
        slide = self.slides[2]
        img_1 = align_imgs[0]
        img_2 = align_imgs[1]

        #seq_img.horizontal()
        img_1.vertical()
        img_2.vertical()

        pictures = [img_1.path, img_2.path]
        placeholders = []
        captions = [img_1.caption, img_2.caption]
        textboxes = []

        for shape in slide.shapes:
            if 'Picture' in shape.name:
                placeholders.append(shape)
            if 'Table' in shape.name:
                table = shape.table
            if 'TextBox' in shape.name and len(textboxes) < 2:
                textboxes.append(shape)
        
        zipped = zip(placeholders[1:], pictures)
        for z in zipped:
            z[0].insert_picture(z[1])

        zipped = zip(textboxes, captions)
        for z in zipped:
            z[0].text = z[1]
            for paragraph in z[0].text_frame.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(14)

        if table:
            cell = table.cell(1, 1)
            cell.text = self.human.id
            cell.text_frame.paragraphs[0].runs[0].font.size = Pt(14)

            for i, ortholog in enumerate(self.orthologs, start=1):
                species_cell = table.cell(i, 0)
                species_cell.text = ortholog.organism.name.capitalize()
                species_cell.text_frame.paragraphs[0].runs[0].font.size = Pt(14)

                id_cell = table.cell(i, 1)
                id_cell.text = ortholog.id
                id_cell.text_frame.paragraphs[0].runs[0].font.size = Pt(14)

                similarity_cell = table.cell(i, 2)
                similarity_cell.text = str(ortholog.ecd_similarity) + "%"
                similarity_cell.text_frame.paragraphs[0].runs[0].font.size = Pt(14)

        self.powerpoint.save(self.output_path)
    
    def populate_string_db_slide(self, network_img, pred_partners_img=None):
        slide = self.slides[3]
        placeholders = []

        for shape in slide.shapes:
            if 'Picture' in shape.name:
                placeholders.append(shape)
        
        placeholders[0].insert_picture(network_img)
        # placeholders[1].insert_picture(pred_partners_img)

        self.powerpoint.save(self.output_path)
    
    