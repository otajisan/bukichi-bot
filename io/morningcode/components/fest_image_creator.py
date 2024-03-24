from datetime import datetime as dt
from pprint import pprint
from PIL import Image, ImageDraw, ImageFont

from components.stage_image_creator import StageImageCreator


class FestStageImageCreator(StageImageCreator):
    def run(self):
        print('fetching stages...')
        stages = self.fetch_stages()

        print('filtering stages...')
        filtered = self.filter_recent(stages)

        print('creating image...')
        created_img = self.make_stages_image(filtered)

        if created_img is None:
            print('no image created. maybe all fest.')
            return None

        print('saving image...')
        current_time = dt.now().strftime('%Y%m%d%H')
        save_to = f'{current_time}.png'
        created_img.save(save_to)

        return save_to

    def append_tricolor_stage_image(self, background_img, draw, pos_x, pos_y, data):
        if data['tricolor_stage'] is None or data['rule'] is None:
            return

        delta_y = 780 * 2
        text_color = (255, 255, 255)
        rule_name = 'トリカラバトル'

        # add event time
        start_at = dt.strftime(dt.strptime(data['start_time'], '%Y-%m-%dT%H:%M:%S+09:00'), '%H')
        end_at = dt.strftime(dt.strptime(data['end_time'], '%Y-%m-%dT%H:%M:%S+09:00'), '%H')

        draw.text((pos_x + 8, pos_y - 60 + delta_y), f'{rule_name}({start_at}-{end_at})',
                  fill=text_color,
                  font=self.FONT_JAPANESE)

        stage = data['tricolor_stage']
        stage_name = stage['name']
        save_to = f"{stage_name}.png"
        stage_img = self.download_stage_image(f"{stage_name}.png", stage['image'], 0.76)

        # add stage image
        background_img.paste(stage_img, (pos_x, pos_y + delta_y))

        # add stage name
        stage_name_kana = self.PATTERN_KATAKANA.findall(stage_name)
        if len(stage_name_kana) == 0:
            stage_name_kana = ''
        else:
            stage_name_kana = ''.join(stage_name_kana).replace('ー', '-')
        draw.text((pos_x + 16, pos_y + 232 + delta_y), stage_name_kana, fill=text_color,
                  font=self.FONT_JAPANESE)
        return

    def make_stages_image(self, filtered):
        background_img = self.get_background_img(suffix='fest')
        draw = ImageDraw.Draw(background_img)

        pos_x = 100
        pos_y = 0

        cursor = ''
        for k, v in filtered.items():
            # print(k)
            if k != cursor:
                if k != 'fest' and k != 'fest_challenge':
                    continue
                print(f'processing stage info. current mode: {k}')
                cursor = k
                pos_x = 100
                # initial position
                if pos_y == 0:
                    pos_y = 200
                else:
                    pos_y += 780

            for d in v:
                # print(k)
                # pprint(d)
                self.append_stage_image(background_img, draw, pos_x, pos_y, d)
                if k == 'fest':
                    self.append_tricolor_stage_image(background_img, draw, pos_x, pos_y, d)
                pos_x += 730

        return background_img
