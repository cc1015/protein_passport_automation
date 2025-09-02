from PIL import Image

class Img():
    path: str
    caption: str
    width: int
    height: int

    def __init__(self, path: str, caption=None):
        self.path = path
        self.caption = caption
        img = Image.open(path)
        self.width = img.width
        self.height = img.height

    
    def vertical(self):
        with Image.open(self.path) as img:
            if self.width > self.height:
                img = img.rotate(90, expand=True)
                img.save(self.path)
                self.width = img.width
                self.height = img.height

    def horizontal(self):
        with Image.open(self.path) as img:
            if self.width < self.height:
                img = img.rotate(90, expand=True)
                img.save(self.path)
                self.width = img.width
                self.height = img.height