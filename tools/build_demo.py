#!/usr/bin/env python3
"""Build a portable, offline HTML demo from the actual TV interface; no personal config is read."""
import base64
import json
import mimetypes
import re
from pathlib import Path
import webapp

ROOT = Path(__file__).resolve().parents[1]
config = dict(webapp.GENERIC)
config.update(language='pt', city='Cidade exemplo', latitude='-26.3', longitude='-48.8',
              currency='BRL', tmdbRegion='BR', temperature='C', theme='dark', showCrypto=False,
              shelfApps=['youtube', 'appletv', 'netflix', 'crunchyroll', 'hbo', 'disney', 'spotify', 'twitch'])
files = webapp.files(config, 'tools/build_demo.py')

def uri(name):
    mime = mimetypes.guess_type(name)[0] or 'application/octet-stream'
    return 'data:' + mime + ';base64,' + base64.b64encode(files[name]).decode()

assets = {name: uri(name) for name in files if name.startswith(('icons/', 'symbols/', 'fonts/')) and name.endswith(('.png', '.svg', '.ttf'))}
html = files['index.html'].decode()
html = html.replace('lang="en"', 'lang="pt-BR"').replace('<title>Free My TV</title>', '<title>Free My TV Tizen — demonstração interativa</title>')
for name in ['home.css', 'hdmi.css']:
    css = files[name].decode()
    for asset, data in assets.items():
        css = css.replace(asset, data)
    html = html.replace('<link rel="stylesheet" href="' + name + '">', '<style>' + css + '</style>')

# The demo always operates on sample devices and never contacts a TV or external data services.
mock = '''
var demoAssets = ASSETS;
var demoNativeCreate = document.createElement.bind(document);
document.createElement = function (tag) {
  var node = demoNativeCreate(tag);
  if (tag.toLowerCase() === 'img') {
    Object.defineProperty(node, 'src', {get: function () { return this.getAttribute('src'); },
      set: function (value) { this.setAttribute('src', demoAssets[value] || value); }});
  }
  return node;
};
var demoMask = document.createElement('style');
demoMask.textContent = Object.keys(demoAssets).filter(function (name) { return name.indexOf('symbols/') === 0; }).map(function (name) {
  return '.sym[style*="' + name + '"]{-webkit-mask-image:url("' + demoAssets[name] + '")!important;mask-image:url("' + demoAssets[name] + '")!important;}';
}).join('');
document.head.appendChild(demoMask);
TV.name = 'tizen';
TV.apps = function (done) { done([
  ['youtube','YouTube','youtube.png'], ['appletv','Apple TV','appletv.svg'], ['netflix','Netflix','netflix.svg'],
  ['crunchyroll','Crunchyroll',''], ['hbo','HBO Max','hbomax-vector.svg'], ['disney','Disney+','disneyplus-vector.svg'],
  ['spotify','Spotify','spotify.svg'], ['twitch','Twitch','']
].map(function (a) { return {id:a[0], title:a[1], icon:a[2] ? demoAssets['icons/'+a[2]] : ''}; })); };
TV.inputs = function (done) { done([{id:'source:TV:1',key:'live',label:null,symbol:'live_tv',connected:true}].concat([1,2,3,4].map(function(n){
  return {id:'source:HDMI:'+n,key:'hdmi'+n,label:'HDMI '+n,symbol:'hdmi',connected:n===4};
}))); };
TV.launch = function (id, params, done) { FreeMyTV.toast('Demonstração: '+(id==='com.samsung.tv.csfs'?'interface padrão Tizen':id==='source:TV:1'?'TV aberta':id)); if(done)done(true); };
TV.settings = function(done){FreeMyTV.toast('Demonstração: ajustes da TV');if(done)done(true);};
TV.back = function(){FreeMyTV.toast('Use as setas, Enter e Esc para navegar.');};
'''.replace('ASSETS', json.dumps(assets, separators=(',', ':')))

data_mock = '''
Data.refresh = function(){};
Data.settingsChanged = function(){};
var demoNow = Date.now();
var demoWeather = {temp:22,code:61,isDay:true,max:24,min:17,sunrise:demoNow-5*3600000,sunset:demoNow+6*3600000,
 hours:[0,1,2,3,4,5].map(function(i){return {at:demoNow+(i+1)*3600000,temp:22-i,code:61,day:true};}),
 days:[0,1,2,3,4].map(function(i){return {at:demoNow+(i+1)*86400000,max:24,min:17,code:61};})};
Object.defineProperty(Data,'weather',{get:function(){return demoWeather;}});
Object.defineProperty(Data,'weatherAt',{get:function(){return demoNow;}});
'''
def script(match):
    name = match.group(1)
    source = files[name].decode().replace('</script', '<\\/script')
    extra = mock if name == 'tv.js' else data_mock if name == 'data.js' else ''
    return '<script>' + source + extra + '</script>'
html = re.sub(r'<script src="([^"]+)"></script>', script, html)
toolbar = '''
<style>
#demo-bar{position:fixed;z-index:100;top:0;left:0;right:0;padding:9px 16px;background:#101823;color:white;font:14px system-ui;display:flex;gap:16px;align-items:center;justify-content:space-between}
#demo-bar button,#demo-bar a{color:white;background:#27384e;border:1px solid #5c6d81;border-radius:8px;padding:6px 12px;text-decoration:none;cursor:pointer}
@media(max-width:800px){#demo-bar{font-size:11px;padding:6px;gap:4px}#demo-bar .help{display:none}}
</style>
<div id="demo-bar"><strong>DEMO · Free My TV Tizen</strong><span class="help">Dados fictícios · Setas: navegar · Enter: abrir · Esc: voltar · Segure Enter no HDMI: editar</span><div><button id="demo-theme">Dia / Noite</button> <button id="demo-inputs">Entradas</button> <a href="https://github.com/gustavokrug/free-my-tv-tizen">Código e alterações</a></div></div>
<script>
document.getElementById('demo-theme').onclick=function(){Prefs.set('theme',Prefs.theme()==='dark'?'light':'dark');FreeMyTV.move(1,0);document.body.classList.toggle('night',Prefs.theme()==='dark');document.documentElement.style.background=Prefs.theme()==='dark'?'#0B0B0D':'';};
document.getElementById('demo-inputs').onclick=function(){FreeMyTV.state.zone='shelf';FreeMyTV.move(0,1);};
setTimeout(function(){FreeMyTV.move(0,1);},0);
</script>
'''
html = html.replace('</body>', toolbar + '</body>')
target = ROOT / 'docs/index.html'
target.write_text(html.replace('\r', ''), encoding='utf-8', newline='\n')
print('Built docs/index.html (%d KB), portable offline demo.' % (target.stat().st_size // 1024))
