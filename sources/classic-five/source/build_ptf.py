"""Build standard Sony PTF v1 containers from already encoded GIM and BMP assets."""
from pathlib import Path
import hashlib
import json
import re
import struct
import zlib
from PIL import Image
from build_assets import preview

ROOT=Path(__file__).resolve().parents[1]
MAGIC=b'\x00PTF\x00\x01\x00\x00'
LIMIT=768*1024


def fixed(b,off,n,s):
    v=s.encode('utf-8')
    if len(v)>=n:raise ValueError('Metadata exceeds field or omits NUL terminator')
    b[off:off+len(v)]=v


def record(sub,file_type,raw,color=False):
    if color:comp=2;packed=raw
    else:
        z=zlib.compress(raw,9)
        if len(z)+(-len(z)%4)<len(raw):comp=2;packed=z
        else:comp=0;packed=raw
    packed+=bytes(-len(packed)%4)
    head=struct.pack('<HHHHII',sub,0,file_type,comp,len(packed),len(raw))+bytes(16)
    return head+packed


def build():
    themes=json.loads((ROOT/'build/themes.json').read_text())
    assets=json.loads((ROOT/'build/encoded_manifest.json').read_text())
    stats=[]
    for a in assets:
        im=Image.frombytes('RGBA',(a['width'],a['height']),Path(a['decoded']).read_bytes())
        Path(a['output']).with_name(Path(a['output']).stem+'_decoded.png').parent.mkdir(exist_ok=True)
        im.save(Path(a['output']).with_name(Path(a['output']).stem+'_decoded.png'))
    for t in themes:
        p=ROOT/'assets'/t['key']
        # The PTF's selection preview uses the exact palette-decoded icons.
        pv=preview(t,decoded=True)
        pv.save(p/'xmb_preview_decoded.png')
        pv.resize((300,170),Image.Resampling.LANCZOS).save(p/'0_0001.bmp')
        groups={0:[],1:[],2:[],3:[],4:[]}
        groups[0].append((0,5,(p/'0_0000.gim').read_bytes(),False))
        groups[0].append((1,4,(p/'0_0001.bmp').read_bytes(),False))
        groups[0].append((2,5,struct.pack('<I',t['color']),True))
        groups[1].append((0,4,(p/'1_0000.bmp').read_bytes(),False))
        for a in assets:
            if a['theme']==t['key'] and a['group']>=2:
                groups[a['group']].append((a['sub'],5,Path(a['output']).read_bytes(),False))
        out=bytearray(0x120)
        out[:8]=MAGIC
        fixed(out,8,128,t['title']);fixed(out,136,48,t['product_id'])
        fixed(out,184,8,'6.20');fixed(out,192,8,'1.0')
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,47}',t['product_id']):raise ValueError('Invalid product ID')
        struct.pack_into('<I',out,200,8)
        for group,items in groups.items():
            off=len(out);struct.pack_into('<I',out,0x100+group*4,off)
            items.sort(key=lambda x:x[0])
            body=b''.join(record(*item) for item in items)
            out+=struct.pack('<HHII',group,len(items),len(body),off+32)+bytes(20)+body
        if len(out)>LIMIT:raise ValueError(t['filename']+' exceeds 768 KiB')
        target=ROOT/'deliverables'/t['filename'];target.write_bytes(out)
        st=dict(filename=t['filename'],title=t['title'],bytes=len(out),sha256=hashlib.sha256(out).hexdigest(),
                records=sum(len(a) for a in groups.values()),version='1.0',theme_color=t['color'])
        stats.append(st);print(t['filename'],len(out),'bytes',flush=True)
    (ROOT/'build/ptf_manifest.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':build()
