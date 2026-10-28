import sys, re, html
from html.parser import HTMLParser
src=open(sys.argv[1],encoding='utf-8').read()
# find input code cells: jp-InputArea ... <pre>...</pre>
cells=re.findall(r'<div class="jp-Cell jp-(CodeCell|MarkdownCell)[^"]*"(.*?)(?=<div class="jp-Cell jp-|\Z)', src, re.S)
out=[]
for kind,body in cells:
    if kind=='CodeCell':
        m=re.search(r'<div class="highlight[^"]*"><pre>(.*?)</pre>',body,re.S)
        code=re.sub(r'<[^>]+>','',m.group(1)) if m else ''
        code=html.unescape(code)
        # outputs text
        outs=re.findall(r'<pre>(.*?)</pre>',body,re.S)[1:]
        outs=[html.unescape(re.sub(r'<[^>]+>','',o)) for o in outs]
        imgs=len(re.findall(r'<img ',body))
        out.append(('code',code,outs,imgs))
    else:
        txt=html.unescape(re.sub(r'<[^>]+>','',body))
        out.append(('md',txt.strip(),[],0))
import pickle;pickle.dump(out,open(sys.argv[2],'wb'))
for i,(k,c,o,im) in enumerate(out):
    print(f"#### CELL {i} [{k}] lines={c.count(chr(10))} outs={len(o)} imgs={im}")
