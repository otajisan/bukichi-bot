import os

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont


class ImageCreator:
    ENGLISH_FONT_PATH = os.getenv('ENGLISH_FONT_PATH')
    JAPANESE_FONT_PATH = os.getenv('JAPANESE_FONT_PATH')

    def from_text(self, name, text):
        image_file_name = 'image.png'
        fontsize = 36

        canvasSize = (800, 150)
        backgroundRGB = (0, 0, 0)
        textRGB = (255, 255, 255)

        img = PIL.Image.new('RGB', canvasSize, backgroundRGB)
        draw = PIL.ImageDraw.Draw(img)

        font_japanese = PIL.ImageFont.truetype(self.JAPANESE_FONT_PATH, fontsize)
        font_english = PIL.ImageFont.truetype(self.ENGLISH_FONT_PATH, fontsize)


        draw.text((20, 20), name, fill=textRGB, font=font_english)
        draw.text((20, 70), text, fill=textRGB, font=font_japanese)

        img.save(image_file_name)

        return image_file_name
