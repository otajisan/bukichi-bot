import os
import re
import requests

from datetime import datetime as dt
from PIL import Image, ImageDraw, ImageFont


class StageImageCreator:
    ENGLISH_FONT_PATH = os.getenv('ENGLISH_FONT_PATH')
    JAPANESE_FONT_PATH = os.getenv('JAPANESE_FONT_PATH')

    PATTERN_KATAKANA = re.compile('[ア-ンー]+')

    def __init__(self):
        self.FONT_JAPANESE = self.load_font()

    def run(self):
        print('fetching stages...')
        stages = self.fetch_stages()

        print('filtering stages...')
        filtered = self.filter_recent(stages)

        print('creating image...')
        created_img = self.make_stages_image(filtered)

        print('saving image...')
        current_time = dt.now().strftime('%Y%m%d%H')
        save_to = f'{current_time}.png'
        created_img.save(save_to)

        return save_to

    @staticmethod
    def fetch_stages():
        url = 'https://spla3.yuu26.com/api/schedule'
        response = requests.get(url)

        return response.json()

    @staticmethod
    def filter_recent(stages):
        current = dt.now()
        filtered = {}
        for k, v in stages['result'].items():
            filtered[k] = []
            for i, d in enumerate(v):
                if i > 3:
                    break
                start = dt.strptime(d['start_time'], '%Y-%m-%dT%H:%M:%S+09:00')
                if start.date() != current.date():
                    continue
                filtered[k].append(d)

        return filtered

    def load_font(self):
        font_size = 32
        return ImageFont.truetype(self.JAPANESE_FONT_PATH, font_size)

    @staticmethod
    def get_background_img():
        background_img = 'io/morningcode/assets/img/discord_bg.png'
        try:
            return Image.open(background_img)
        except FileNotFoundError:
            print(f'file not found. {background_img}')
            return None

    @staticmethod
    def resize_image(img):
        size_delta = 0.85
        return img.resize((round(img.width // size_delta), round(img.height // size_delta)))

    def download_stage_image(self, save_to, image_url):
        response = requests.get(image_url, stream=True)
        with open(save_to, 'wb') as f:
            f.write(response.content)

        return self.resize_image(Image.open(save_to))

    def append_stage_image(self, background_img, draw, pos_x, pos_y, data):
        if data['stages'] is None:
            return

        text_color = (255, 255, 255)

        # add event time
        start_at = dt.strftime(dt.strptime(data['start_time'], '%Y-%m-%dT%H:%M:%S+09:00'), '%H')
        end_at = dt.strftime(dt.strptime(data['end_time'], '%Y-%m-%dT%H:%M:%S+09:00'), '%H')

        draw.text((pos_x + 8, pos_y - 50), f'{start_at}-{end_at}', fill=text_color,
                  font=self.FONT_JAPANESE)

        for number, stage in enumerate(data['stages']):
            delta_y = 245 * number
            stage_name = stage['name']
            save_to = f"{stage_name}.png"

            stage_img = self.download_stage_image(f"{stage['name']}.png", stage['image'])

            # add stage image
            background_img.paste(stage_img, (pos_x, pos_y + delta_y))

            # add stage name
            stage_name_kana = self.PATTERN_KATAKANA.findall(stage_name)
            if len(stage_name_kana) == 0:
                stage_name_kana = ''
            else:
                stage_name_kana = ''.join(stage_name_kana).replace('ー', '-')
            draw.text((pos_x + 8, pos_y + 190 + delta_y), stage_name_kana, fill=text_color,
                      font=self.FONT_JAPANESE)

            # delete image file
            os.remove(f"{stage['name']}.png")

    def append_rule_name(self, draw, pos_x, pos_y, data):
        if data is None or data['rule'] is None:
            return

        text_color = (255, 255, 255)

        rule = data['rule']['name']
        print(rule)
        draw.text((pos_x + 8, pos_y - 100), rule, fill=text_color, font=self.FONT_JAPANESE)

    def make_stages_image(self, filtered):
        background_img = self.get_background_img()
        draw = ImageDraw.Draw(background_img)

        pos_x = 50
        pos_y = 0

        cursor = ''
        for k, v in filtered.items():
            print(k)
            if k != cursor:
                print(f'processing stage info. current rule: {k}')
                cursor = k
                pos_x = 50
                # initial position
                if pos_y == 0:
                    pos_y = 300
                else:
                    pos_y += 700

            for d in v:
                self.append_rule_name(background_img, draw, pos_x, pos_y, d)
                self.append_stage_image(background_img, draw, pos_x, pos_y, d)
                pos_x += 480

        return background_img
