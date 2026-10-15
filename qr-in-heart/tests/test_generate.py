import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from generator import generate_image
from scripts.generate import decode_image

class TestQrHeart(unittest.TestCase):
    def test_url_default_pink(self):
        text='https://phuong.tinhtd.info/'
        self.assertEqual(decode_image(generate_image(text)),text)
    def test_plain_text_and_custom_color(self):
        text='Leo loves Phuong <3'
        self.assertEqual(decode_image(generate_image(text,'#c2185b')),text)
    def test_non_ascii(self):
        text='Chúc mừng sinh nhật Phương!'
        self.assertEqual(decode_image(generate_image(text)),text)
    def test_bad_color(self):
        with self.assertRaises(ValueError):generate_image('abc','#ffffff')
if __name__=='__main__':unittest.main()
