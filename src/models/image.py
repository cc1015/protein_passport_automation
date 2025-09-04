from PIL import Image

class Img():
    """
    Represents an image file.

    Attributes:
        path (str): Image file path.
        caption (str): Image caption.
        width (int): Image width.
        height (int): Image height.
    """
    path: str
    caption: str
    width: int
    height: int

    def __init__(self, path: str, caption=None):
        """
        Constructor for Img.

        Args:
            path (str): Image file path.
            caption (str): Image caption.
        """
        self.path = path
        self.caption = caption
        img = Image.open(path)
        self.width = img.width
        self.height = img.height

    
    def vertical(self):
        """
        Rotates this Image vertically if horizontal.
        """
        with Image.open(self.path) as img:
            if self.width > self.height:
                img = img.rotate(90, expand=True)
                img.save(self.path)
                self.width = img.width
                self.height = img.height

    def horizontal(self):
        """
        Rotates this Image horizontally if vertical.
        """
        with Image.open(self.path) as img:
            if self.width < self.height:
                img = img.rotate(90, expand=True)
                img.save(self.path)
                self.width = img.width
                self.height = img.height