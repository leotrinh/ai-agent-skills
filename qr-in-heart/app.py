"""Small local-only preview UI. Author: Leo."""
import base64
from html import escape
from pathlib import Path
from urllib.parse import urlencode
from flask import Flask, Response, request
from generator import DEFAULT_COLOR, generate_png_bytes, generate_image
from scripts.generate import decode_image

app=Flask(__name__)

def page(text='',color=DEFAULT_COLOR,image_data='',error=''):
    preview=(f'<img alt="Generated QR inside a heart" src="data:image/png;base64,{image_data}">'
             if image_data else '<div class="placeholder">Preview appears here</div>')
    link=f'<a class="download" href="/download?{urlencode(dict(text=text,color=color))}">Download verified PNG</a>' if image_data else ''
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>qr-in-heart</title><style>
    *{{box-sizing:border-box}}body{{margin:0;background:#fff8fc;color:#301b2b;font-family:system-ui,sans-serif}}main{{max-width:920px;margin:auto;padding:32px 18px}}h1{{margin:0}}p{{color:#74596d}}section{{display:grid;grid-template-columns:minmax(240px,1fr) minmax(280px,1.5fr);gap:20px;margin-top:24px}}article{{background:white;border:1px solid #ffd5e7;border-radius:18px;padding:20px;box-shadow:0 7px 28px #f0177712}}label{{display:block;font-weight:700;margin:12px 0 6px}}input[type=text]{{width:100%;padding:12px;border:1px solid #d8b9ca;border-radius:10px}}input[type=color]{{width:100%;height:48px}}button,.download{{display:inline-block;background:#ff1681;color:white;border:0;padding:12px 16px;border-radius:12px;font-weight:700;text-decoration:none;margin-top:16px}}img{{width:100%;border-radius:8px}}.error{{color:#b00020;font-weight:600}}.placeholder{{padding:60px 10px;text-align:center;color:#888}}@media(max-width:680px){{section{{grid-template-columns:1fr}}}}</style></head><body><main><h1>qr-in-heart 💗</h1><p>Author: Leo · URL/text + color (default pink) · verified scan</p><section><article><form method="post"><label>URL or text</label><input name="text" type="text" required value="{escape(text,quote=True)}" placeholder="https://phuong.tinhtd.info/"><label>Color</label><input name="color" type="color" value="{escape(color,quote=True)}"><button>Generate & validate</button></form><div class="error">{escape(error)}</div></article><article>{preview}{link}</article></section></main></body></html>"""

@app.route('/',methods=['GET','POST'])
def home():
    if request.method=='GET':return page()
    text=request.form.get('text','')
    color=request.form.get('color',DEFAULT_COLOR)
    try:
        image=generate_image(text,color)
        if decode_image(image)!=text:raise ValueError('QR did not decode to the exact input. Try shorter text or darker color.')
        import io
        data=io.BytesIO();image.save(data,format='PNG')
        return page(text,color,base64.b64encode(data.getvalue()).decode())
    except ValueError as e:return page(text,color,error=str(e)),400

@app.get('/download')
def download():
    text=request.args.get('text','')
    color=request.args.get('color',DEFAULT_COLOR)
    try:
        image=generate_image(text,color)
        if decode_image(image)!=text:raise ValueError('QR validation failed')
        import io
        data=io.BytesIO();image.save(data,format='PNG')
        return Response(data.getvalue(),mimetype='image/png',headers={'Content-Disposition':'attachment; filename="qr-in-heart.png"'})
    except ValueError as e:return Response(str(e),status=400)

if __name__=='__main__':app.run('127.0.0.1',7860)
