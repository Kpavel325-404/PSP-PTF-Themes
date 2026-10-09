"""Prepare Sony-sized theme assets and illustrative XMB previews."""
from pathlib import Path
import io
import json
import math
import shutil

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from icons import icon, focus, CATEGORIES, FIRST

ROOT=Path(__file__).resolve().parents[1]
THEMES=[
    dict(key='xp_autumn',style='xp',title='Windows XP - Autumn',filename='Windows_XP_Autumn.ptf',color=10,
         source='upload/Windows XP Autumn.jpg',caption='Windows XP · Autumn',accent='#eeb85c'),
    dict(key='winter_moscow',style='winter',title='Зимняя Москва',filename='Winter_Moscow.ptf',color=8,
         source='upload/Зимняя Москва.jpg',caption='Зимняя Москва',accent='#8ccde5'),
    dict(key='ocean_frutiger_aqua',style='ocean',title='Ocean - Frutiger Aqua',filename='Ocean_Frutiger_Aqua.ptf',color=7,
         source='generated_images/exec-6a2da4ca-32e5-4c10-ab27-86d6c348a6b7.png',caption='Океан · Frutiger Aqua',accent='#90dc79'),
    dict(key='mac_os9_platinum',style='platinum',title='Mac OS 9 - Platinum',filename='Mac_OS_9_Platinum.ptf',color=9,
         source=None,caption='Mac OS 9 · Platinum',accent='#aaa5d4'),
    dict(key='mac_osx_aqua',style='osx',title='Mac OS X 10 - Aqua',filename='Mac_OS_X_10_Aqua.ptf',color=8,
         source='generated_images/exec-c46eafba-91a7-44b4-8a6f-c28e92375777.png',caption='Mac OS X 10 · Aqua',accent='#77bafa'),
]
FONT=str(ROOT/'vendor/fonts/DejaVuSans.ttf')
FONT_BOLD=str(ROOT/'vendor/fonts/DejaVuSans-Bold.ttf')


def platinum_wallpaper():
    # The user's reference has a lilac desktop with embossed Finder outlines.
    w,h=480,272
    y,x=np.mgrid[0:h,0:w]
    soft=np.clip(.10*x/w+.045*np.cos(y/h*math.pi),0,1)
    colors=np.stack([96+21*soft,96+18*soft,145+21*soft],axis=2)
    im=Image.fromarray(np.uint8(colors)).convert('RGBA')
    pattern=Image.new('RGBA',(64,64))
    d=ImageDraw.Draw(pattern)
    for offset,col in [(1,(236,232,255,24)),(0,(33,33,86,28))]:
        dx=offset;dy=offset
        d.rounded_rectangle((13+dx,11+dy,47+dx,46+dy),radius=2,outline=col,width=1)
        d.line([(31+dx,13+dy),(27+dx,31+dy),(32+dx,31+dy),(32+dx,40+dy)],fill=col,width=1)
        d.line([(21+dx,21+dy),(21+dx,25+dy)],fill=col,width=1)
        d.line([(40+dx,21+dy),(40+dx,25+dy)],fill=col,width=1)
        d.arc((20+dx,25+dy,43+dx,38+dy),10,170,fill=col,width=1)
    pattern=pattern.rotate(12,resample=Image.Resampling.BICUBIC)
    for row,yy in enumerate(range(-15,h,72)):
        for xx in range(-24+(row%2)*35,w,72):im.alpha_composite(pattern,(xx,yy))
    return im.convert('RGB')


def shadow_text(im,xy,text,size=11,alpha=255,anchor=None):
    font=ImageFont.truetype(FONT,size)
    layer=Image.new('RGBA',im.size)
    d=ImageDraw.Draw(layer)
    x,y=xy
    d.text((x+1,y+1),text,font=font,fill=(0,0,0,round(alpha*.70)),anchor=anchor)
    blurred=layer.filter(ImageFilter.GaussianBlur(.75))
    im.alpha_composite(blurred)
    ImageDraw.Draw(im).text(xy,text,font=font,fill=(250,250,248,alpha),anchor=anchor)


def preview(theme, decoded=False):
    root=ROOT/'assets'/theme['key']
    def load(group,sub):
        stem=f'{group}_{sub:04d}'
        p=root/((stem+'_decoded.png') if decoded else (stem+'.png'))
        return Image.open(p).convert('RGBA')
    im=Image.open(root/'wallpaper.png').convert('RGBA')
    # Illustrative XMB recreation: native 480x272 layout, standard PSP text.
    # Category Game is selected. Firmware renders the actual live interface.
    xs={4:-54,5:28,6:110,7:192,8:274}
    for sub,cx in xs.items():
        asset=load(2,sub)
        if sub!=6:asset.putalpha(asset.getchannel('A').point(lambda a:round(a*.55)))
        im.alpha_composite(asset,(cx-32,72-24))
    shadow_text(im,(110,104),'Игра',11,anchor='mt')
    for sub,yy,opacity in [(2,201,.50),(4,12,.36)]:
        asset=load(3,sub)
        asset.putalpha(asset.getchannel('A').point(lambda a:round(a*opacity)))
        im.alpha_composite(asset,(86,yy-24))
    active=load(3,10)
    halo=load(3,11)
    im.alpha_composite(halo,(78,105))
    im.alpha_composite(active,(86,113))
    shadow_text(im,(146,131),'Сохранённые данные',12)
    shadow_text(im,(146,195),'Memory Stick™',10,alpha=160)
    shadow_text(im,(403,13),'9/10  12:45',10,anchor='rt')
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((418,13,439,22),radius=1,outline=(0,0,0,110),width=2)
    d.rounded_rectangle((418,12,439,21),radius=1,outline=(248,250,250,230),width=1)
    d.rectangle((440,15,441,18),fill=(248,250,250,220))
    d.rectangle((421,15,434,18),fill=(248,250,250,215))
    return im.convert('RGB')


def save_asset(theme,group,sub,im,manifest,role):
    path=ROOT/'assets'/theme['key']
    stem=f'{group}_{sub:04d}'
    im=im.convert('RGBA');im.save(path/(stem+'.png'))
    (path/(stem+'.rgba')).write_bytes(im.tobytes())
    manifest.append(dict(theme=theme['key'],group=group,sub=sub,width=im.width,height=im.height,
                         input=str(path/(stem+'.rgba')),output=str(path/(stem+'.gim')),
                         decoded=str(path/(stem+'_decoded.rgba')),png=str(path/(stem+'.png')),role=role))


def build():
    (ROOT/'build').mkdir(exist_ok=True)
    (ROOT/'deliverables').mkdir(exist_ok=True)
    manifest=[]
    for t in THEMES:
        path=ROOT/'assets'/t['key'];path.mkdir(parents=True,exist_ok=True)
        if t['source']:
            external=ROOT.parent/t['source']
            target=path/('wallpaper_source'+external.suffix.lower())
            src=target if target.is_file() else external
            if not src.is_file():raise FileNotFoundError(src)
            # Only fit/crop and encode for the fixed PSP wallpaper canvas.
            # No creative edits to the user's photographic sources.
            image=ImageOps.exif_transpose(Image.open(src)).convert('RGB')
            if src.resolve()!=target.resolve():shutil.copy2(src,target)
            image=ImageOps.fit(image,(480,272),Image.Resampling.LANCZOS,centering=(.5,.5))
        else:image=platinum_wallpaper()
        image.save(path/'wallpaper.png');image.save(path/'1_0000.bmp')
        style=t['style']
        category_symbols=CATEGORIES.copy()
        if style=='platinum':category_symbols.update({1:'happy',3:'itunes',4:'quicktime'})
        if style=='osx':category_symbols.update({1:'prefs',3:'itunes',4:'quicktime'})
        for sub,symbol in category_symbols.items():save_asset(t,2,sub,icon(style,symbol,(64,48)),manifest,'category')
        for sub,symbol in FIRST.items():
            body=icon(style,symbol)
            save_asset(t,3,sub,body,manifest,'first_body')
            save_asset(t,3,sub+1,focus(body,(64,64)),manifest,'first_focus')
        for sub,symbol in [(0,'wrench'),(2,'adjust')]:
            body=icon(style,symbol,(32,32))
            save_asset(t,4,sub,body,manifest,'second_body')
            save_asset(t,4,sub+1,focus(body,(48,48)),manifest,'second_focus')
        save_asset(t,0,0,icon(style,'finder',(16,16)),manifest,'preview_icon')
        im=preview(t)
        im.save(path/'xmb_preview.png')
        im.resize((300,170),Image.Resampling.LANCZOS).save(path/'0_0001.bmp')
        t['product_id']=Path(t['filename']).stem
        print('Prepared',t['filename'],flush=True)
    (ROOT/'build'/'assets_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'build'/'themes.json').write_text(json.dumps(THEMES,ensure_ascii=False,indent=2),encoding='utf-8')


if __name__=='__main__':build()
