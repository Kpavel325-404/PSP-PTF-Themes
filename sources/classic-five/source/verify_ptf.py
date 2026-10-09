"""Strict container checks plus independent LibPSPThemes PTF/GIM extraction.

The external extractor is used unmodified, fetched locally from its upstream.
It is not redistributed in the source bundle (the upstream has no licence file).
"""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import re
import shutil
import struct
import sys
from types import SimpleNamespace
import zlib
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'vendor/libpspthemes'))
import ptf as independent

EXPECTED={0:[0,1,2],1:[0],2:list(range(1,9)),3:list(range(2,60)),4:list(range(4))}


def unpack_resource(packed,comp,uc):
    if comp==2 and len(packed)<uc:
        d=zlib.decompressobj();raw=d.decompress(packed)+d.flush()
        assert d.eof and not d.unconsumed_tail
        assert len(d.unused_data)<=3 and not any(d.unused_data)
    else:
        assert comp==0 or (comp==2 and len(packed)==uc)
        raw=packed[:uc]
        assert not any(packed[uc:])
    assert len(raw)==uc
    return raw


def gim_schema(raw,size,focus=False):
    assert raw[:16]==b'MIG.00.1PSP\0\0\0\0\0'
    pos=16; blocks=[];image=None;palette=None
    while pos<len(raw):
        assert pos%4==0 and pos+16<=len(raw)
        type,reserved,length,next_offset,data_offset=struct.unpack_from('<HHIII',raw,pos)
        assert reserved==0 and length>=16 and pos+length<=len(raw) and data_offset==16
        assert next_offset>=16 and pos+next_offset<=len(raw)
        blocks.append(type)
        if type in (4,5):
            c=pos+16
            structure,zero,fmt,order,w,h,bpp,pitch,height_align,reserved2=struct.unpack_from('<10H',raw,c)
            assert structure==48 and zero==0 and pitch==16 and height_align==8
            index,start,end=struct.unpack_from('<3I',raw,c+24)
            assert index==48 and start==64 and struct.unpack_from('<I',raw,c+index)[0]==start
            assert c+end==pos+length
            if type==5:
                assert (fmt,order,w,h,bpp)==(3,0,256,1,32)
                assert end-start==1024
                palette=raw[c+start:c+end]
            else:
                assert (fmt,order,bpp)==(5,1,8) and (w,h)==size
                assert end-start==((w+15)//16*16)*((h+7)//8*8)
                image=raw[c+start:c+end]
        pos+=next_offset
    assert pos==len(raw) and blocks==[2,3,5,4,255]
    assert palette is not None and image is not None
    if focus:
        visible=[]
        for i in set(image):
            r,g,b,a=palette[i*4:i*4+4]
            assert (r,g,b)==((255,255,255) if a else (0,0,0))
            visible.append((r,g,b,a))
        assert len(set(visible))<=64
    return len(set(image))


def main():
    themes=json.loads((ROOT/'build/themes.json').read_text())
    report=[]
    extract=ROOT/'checks/independent_extract';extract.mkdir(exist_ok=True)
    args=SimpleNamespace(verbose=False,convert_to_png=True)
    for t in themes:
        src=ROOT/'deliverables'/t['filename'];b=src.read_bytes()
        assert len(b)<=768*1024 and len(b)%4==0 and b[:8]==b'\x00PTF\x00\x01\x00\x00'
        assert b[8:136].split(b'\0')[0].decode('utf-8')==t['title']
        assert b[136:184].split(b'\0')[0].decode()==t['product_id']
        assert b[184:192].split(b'\0')[0]==b'6.20'
        assert b[192:200].split(b'\0')[0]==b'1.0'
        assert struct.unpack_from('<I',b,200)[0]==8 and not any(b[204:256])
        offsets=struct.unpack_from('<8I',b,256)
        assert all(offsets[:5]) and not any(offsets[5:])
        end=288;records=[]; graphics=0
        for group,off in enumerate(offsets[:5]):
            assert off==end and off%4==0
            obj,count,length,start=struct.unpack_from('<HHII',b,off)
            assert obj==group and count==len(EXPECTED[group]) and start==off+32
            assert not any(b[off+12:off+32])
            end=start+length;assert end<=len(b)
            p=start
            for sub_expected in EXPECTED[group]:
                assert p+32<=end
                sub,zero,tp,comp,packed_size,uc_size=struct.unpack_from('<4H2I',b,p)
                assert sub==sub_expected and zero==0 and not any(b[p+16:p+32])
                assert comp in (0,2) and packed_size%4==0 and p+32+packed_size<=end
                raw=unpack_resource(b[p+32:p+32+packed_size],comp,uc_size)
                if (group,sub)==(0,2):
                    assert (tp,comp,packed_size,uc_size)==(5,2,4,4)
                    assert struct.unpack('<I',raw)[0]==t['color']
                elif group==1 or (group,sub)==(0,1):
                    assert tp==4 and raw[:2]==b'BM'
                    size=(480,272) if group==1 else (300,170)
                    assert struct.unpack_from('<I',raw,10)[0]==54
                    assert struct.unpack_from('<I',raw,14)[0]==40
                    assert struct.unpack_from('<H',raw,28)[0]==24 and struct.unpack_from('<I',raw,30)[0]==0
                    im=Image.open(io.BytesIO(raw));assert im.mode=='RGB' and im.size==size
                    graphics+=1
                else:
                    assert tp==5
                    size=(16,16) if group==0 else (64,48) if group==2 else ((64,64) if sub%2 else (48,48)) if group==3 else ((48,48) if sub%2 else (32,32))
                    colors=gim_schema(raw,size,group in (3,4) and sub%2==1)
                    assert colors<=256
                    graphics+=1
                records.append((group,sub,tp,comp,packed_size,uc_size))
                p+=32+packed_size
            assert p==end
        assert end==len(b) and len(records)==74 and graphics==73
        # Independently parse, decompress, unswizzle and decode all saved pictures.
        target=extract/t['filename'];shutil.copy2(src,target)
        errors=io.StringIO()
        with contextlib.redirect_stderr(errors):independent.ptf_extract(str(target),args)
        assert not errors.getvalue(),errors.getvalue()
        folder=target.with_suffix('')
        index=json.loads((folder/'index.json').read_text())
        assert index['name']==t['title'] and index['file_name']==t['product_id'] and index['background_mode']==t['color']
        compared=0
        for group,subs in EXPECTED.items():
            assert sorted(map(int,index['categories'][str(group)]))==subs
            for sub in subs:
                if (group,sub)==(0,2):continue
                stem=f'{group}_{sub:04d}'
                original=ROOT/'assets'/t['key']
                expected=original/('wallpaper.png' if group==1 else '0_0001.bmp' if (group,sub)==(0,1) else stem+'_decoded.png')
                im=Image.open(folder/(stem+'.png')).convert('RGBA')
                canonical=Image.open(expected).convert('RGBA')
                assert im.size==canonical.size and im.tobytes()==canonical.tobytes(),(t['filename'],stem,'independent image mismatch')
                # Guard transparent borders and detect blank/corrupt icons.
                if group in (2,3,4) or (group,sub)==(0,0):
                    a=im.getchannel('A');assert a.getextrema()[1]>40
                    if group in (3,4) and sub%2:
                        assert a.crop((0,0,im.width,2)).getextrema()[1]==0
                        assert a.crop((0,im.height-2,im.width,im.height)).getextrema()[1]==0
                compared+=1
        assert compared==73
        row=dict(filename=t['filename'],status='PASS',bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),
                 records=len(records),graphics=graphics,independent_pixel_matches=compared,
                 target='PSP-3000 / FW 6.61',hardware_test='NOT_RUN')
        report.append(row);print('PASS',t['filename'],f'{compared} independently decoded graphics',flush=True)
    (ROOT/'checks/verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('PASS: 5 PTF, 370 records, 365 decoded picture comparisons. PSP hardware testing remains pending.')


if __name__=='__main__':main()
