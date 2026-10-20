import io, re
from urllib.parse import urlparse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, send_file
from playwright.sync_api import sync_playwright

app=Flask(__name__)
HEADERS={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"}

def clean(s):
    return re.sub(r'\s+',' ',s or '').strip()

def extract(url):
    r=requests.get(url,headers=HEADERS,timeout=25)
    r.raise_for_status()
    soup=BeautifulSoup(r.text,'html.parser')
    for x in soup(['script','style','nav','footer','aside','form','noscript']): x.decompose()
    title=clean((soup.find('meta',property='og:title') or {}).get('content'))
    if not title: title=clean(soup.title.get_text()) if soup.title else ''
    author=''
    for key,attr in [('meta',{'name':'author'}),('meta',{'property':'article:author'})]:
        n=soup.find(key,attr)
        if n and n.get('content'): author=clean(n.get('content')); break
    date=''
    for attrs in ({'property':'article:published_time'},{'name':'date'},{'name':'pubdate'}):
        n=soup.find('meta',attrs)
        if n and n.get('content'): date=clean(n['content'][:10]); break
    article=soup.find('article') or soup.find('main') or soup.body
    paras=[]
    if article:
        for p in article.find_all(['p','h2','h3']):
            t=clean(p.get_text(' ',strip=True))
            if len(t)>35 and t not in paras: paras.append(t)
    image=''
    im=soup.find('meta',property='og:image')
    if im: image=im.get('content','')
    medium=urlparse(url).netloc.lower().removeprefix('www.').upper()
    return {'medium':medium,'title':title,'author':author,'date':date,'body':'\n\n'.join(paras),'image':image,'url':url}

def safe_filename(name):
    return re.sub(r'[^A-Za-z0-9.()_-]+','_',name).strip('_') or 'CLIPPING'

@app.get('/')
def home(): return render_template('index.html')

@app.post('/api/extract')
def api_extract():
    try: return jsonify({'ok':True,'data':extract(request.json.get('url',''))})
    except Exception as e: return jsonify({'ok':False,'error':str(e)}),400

@app.post('/api/pdf')
def api_pdf():
    d=request.form.to_dict()
    number=int(d.get('number') or 1)
    base=d.get('medium','CLIPPING')+(f' ({number})' if number>1 else '')
    html=render_template('pdf.html',**d)
    with sync_playwright() as p:
        browser=p.chromium.launch(args=['--no-sandbox'])
        page=browser.new_page()
        page.set_content(html,wait_until='networkidle')
        pdf=page.pdf(format='A4',margin={'top':'20mm','right':'18mm','bottom':'20mm','left':'18mm'},print_background=True)
        browser.close()
    return send_file(io.BytesIO(pdf),mimetype='application/pdf',as_attachment=True,download_name=safe_filename(base)+'.pdf')
