"""Original, code-native PSP icon artwork. Pillow/numpy; no system icon assets."""
from __future__ import annotations

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 4
N = 48


def rgba(c):
    if isinstance(c, str):
        c = c.lstrip('#')
        return tuple(int(c[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    return tuple(c) + (255,) if len(c) == 3 else tuple(c)


class Canvas:
    def __init__(self, style):
        self.style = style
        self.im = Image.new('RGBA', (N*S, N*S))
        self.edge = '#323644' if style == 'platinum' else '#123557'

    def shape(self, kind, box=None, top='#dceaff', bottom=None, outline=None,
              width=0.9, radius=3, points=None):
        mask = Image.new('L', self.im.size)
        d = ImageDraw.Draw(mask)
        xy = tuple(round(v*S) for v in box) if box is not None else None
        pts = [(round(x*S), round(y*S)) for x, y in points] if points else None
        if kind == 'round': d.rounded_rectangle(xy, radius=round(radius*S), fill=255)
        elif kind == 'rect': d.rectangle(xy, fill=255)
        elif kind == 'ellipse': d.ellipse(xy, fill=255)
        elif kind == 'poly': d.polygon(pts, fill=255)
        else: raise ValueError(kind)
        a, b = np.array(rgba(top), dtype=float), np.array(rgba(bottom or top), dtype=float)
        lo = box[1] if box else min(y for _, y in points)
        hi = box[3] if box else max(y for _, y in points)
        t = np.clip((np.arange(N*S)/S-lo)/max(hi-lo, 1), 0, 1)
        arr = np.broadcast_to((a[None, :] * (1-t[:, None]) + b[None, :] * t[:, None])[:, None, :], (N*S, N*S, 4)).copy()
        arr[:, :, 3] *= np.asarray(mask)/255
        self.im.alpha_composite(Image.fromarray(np.uint8(np.clip(arr, 0, 255))))
        if outline:
            d = ImageDraw.Draw(self.im)
            kw = dict(outline=rgba(outline), width=max(1, round(width*S)))
            if kind == 'round': d.rounded_rectangle(xy, radius=round(radius*S), **kw)
            elif kind == 'rect': d.rectangle(xy, **kw)
            elif kind == 'ellipse': d.ellipse(xy, **kw)
            elif kind == 'poly': d.line(pts+[pts[0]], fill=rgba(outline), width=max(1, round(width*S)), joint='curve')

    def line(self, points, color='#f6fbff', width=1.3):
        d = ImageDraw.Draw(self.im)
        d.line([(round(x*S), round(y*S)) for x,y in points], fill=rgba(color), width=max(1,round(width*S)), joint='curve')

    def arc(self, box, start, end, color, width=1.3):
        ImageDraw.Draw(self.im).arc(tuple(round(v*S) for v in box), start, end, fill=rgba(color), width=max(1,round(width*S)))

    def gloss(self, box, amount=105):
        if self.style == 'platinum': return
        x0,y0,x1,y1 = box
        self.shape('ellipse', (x0+2,y0+1,x1-2,y0+(y1-y0)*.48), (255,255,255,amount), (255,255,255,0))

    def bevel(self, box):
        x0,y0,x1,y1=box
        self.line([(x0,y1),(x0,y0),(x1,y0)], '#ffffff', .8)
        self.line([(x1,y0),(x1,y1),(x0,y1)], '#737783', .8)

    def finish(self):
        return self.im.resize((48,48),Image.Resampling.LANCZOS)


def scheme(style):
    if style == 'xp':
        return dict(blue=('#87cbff','#1765c6'), silver=('#ffffff','#8cabc8'),
                    gold=('#ffe680','#e49419'), green=('#bbf56e','#41922d'),
                    violet=('#c5a3f8','#724eb5'), dark=('#52627b','#263249'),
                    red=('#ffa680','#d7442c'))
    if style == 'platinum':
        return dict(blue=('#a9b6ee','#7786bd'), silver=('#f9f9f0','#a1a2a7'),
                    gold=('#eeeab2','#bcb76d'), green=('#a7d5a0','#6f9e66'),
                    violet=('#c4a1df','#9774b3'), dark=('#898b97','#555762'),
                    red=('#e399a9','#bd6c81'))
    if style == 'osx':
        return dict(blue=('#bceeff','#2387da'), silver=('#f8fcff','#9aafbc'),
                    gold=('#ffe596','#e7a830'), green=('#c0f89a','#6aaf41'),
                    violet=('#d4b6ff','#7970c6'), dark=('#9aaabc','#384452'),
                    red=('#ffbcaf','#d76e60'))
    if style == 'winter':
        return dict(blue=('#e6faff','#66a9d6'), silver=('#ffffff','#b5d5e5'),
                    gold=('#e8f7ff','#89bdd4'), green=('#d4ffef','#67bfb4'),
                    violet=('#e4e7ff','#9faee3'), dark=('#6e9fb9','#234664'),
                    red=('#e2f3ff','#8fafd4'))
    return dict(blue=('#e0ffff','#20a7d7'), silver=('#f2ffff','#91d4db'),
                gold=('#fff999','#e4c519'), green=('#c8ff71','#50b929'),
                violet=('#adf7ff','#36b0c3'), dark=('#42adbd','#07637e'),
                red=('#ffcf84','#e09031'))


def gear(c, colors):
    pts=[]
    for i in range(48):
        a=-math.pi/2+i*math.tau/48
        r=18 if i%4 in (1,2) else 15
        pts.append((24+r*math.cos(a),24+r*math.sin(a)))
    c.shape('poly',points=pts,top=colors['silver'][0],bottom=colors['silver'][1],outline=c.edge)
    c.shape('ellipse',(15,15,33,33),*colors['dark'],outline='#f1f8ff',width=1)
    c.shape('ellipse',(19,19,29,29),*colors['blue'],outline=c.edge,width=.7)
    c.arc((9,9,39,39),195,305,'#ffffff',1)


def monitor(c, colors, happy=False, tv=False):
    c.shape('round',(5,9,43,35),*colors['silver'],outline=c.edge,radius=2)
    c.shape('rect',(9,13,39,30),*colors['blue'],outline=c.edge,width=.9)
    c.shape('poly',points=[(22,35),(27,35),(30,40),(18,40)],top=colors['silver'][0],bottom=colors['silver'][1],outline=c.edge)
    c.line([(16,41),(32,41)],c.edge,1.2)
    if c.style == 'platinum': c.bevel((6,10,42,34))
    if happy:
        c.line([(18,18),(18,22)],c.edge,1.4)
        c.line([(30,18),(30,22)],c.edge,1.4)
        c.line([(20,26),(24,28),(28,26)],c.edge,1.1)
    elif tv:
        c.line([(17,5),(23,9),(29,4)],c.edge,1.1)
        c.shape('poly',points=[(21,17),(29,22),(21,27)],top='#eefbff',outline=None)
    else:
        c.shape('poly',points=[(10,28),(19,18),(25,23),(29,19),(38,28)],top=colors['green'][0],bottom=colors['green'][1])
        c.shape('ellipse',(31,16,35,20),'#fff4b7')


def photo(c, colors):
    if c.style=='osx':
        c.shape('poly',points=[(6,13),(32,7),(42,33),(14,40)],top='#f8fcff',bottom='#bccede',outline=c.edge,width=.7)
    c.shape('rect',(7,10,40,37),*colors['silver'],outline=c.edge,width=1)
    c.shape('rect',(11,13,36,31),*colors['blue'],outline=c.edge,width=.6)
    c.shape('poly',points=[(11,31),(20,20),(26,25),(31,20),(36,31)],top=colors['green'][0],bottom=colors['green'][1])
    c.shape('ellipse',(28,16,32,20),*colors['gold'])
    c.line([(13,34),(25,34)],'#91a1b3',.7)
    if c.style=='platinum':c.bevel((8,11,39,36))


def note(c, colors):
    c.shape('ellipse',(7,29,21,39),*colors['blue'],outline=c.edge,width=.8)
    c.shape('ellipse',(27,24,41,34),*colors['blue'],outline=c.edge,width=.8)
    c.shape('poly',points=[(18,10),(38,6),(38,29),(34,29),(34,14),(22,17),(22,34),(18,34)],top=colors['blue'][0],bottom=colors['blue'][1],outline=c.edge,width=.7)
    c.line([(20,12),(36,9)],'#eefaff',1)
    c.gloss((9,29,20,39),90)


def film(c, colors):
    c.shape('round',(8,6,40,42),*colors['dark'],outline=c.edge,radius=1.8)
    c.shape('rect',(14,12,34,35),*colors['blue'],outline='#b7d5ee',width=.6)
    for x in (10,36):
        for y in (10,18,26,34):c.shape('rect',(x,y,x+2,y+3),'#f1faff')
    c.shape('poly',points=[(20,18),(29,24),(20,30)],top='#ffffff',bottom='#bdeaff')


def gamepad(c, colors):
    c.shape('poly',points=[(11,14),(18,11),(30,11),(37,14),(43,33),(38,37),(29,30),(19,30),(10,37),(5,33)],top=colors['silver'][0],bottom=colors['silver'][1],outline=c.edge,width=1.1)
    c.shape('round',(11,18,19,26),*colors['dark'],outline=c.edge,radius=.8)
    c.shape('rect',(13.7,16,16.3,28),*colors['dark'])
    for x,y,col in [(33,18,'green'),(37,22,'red'),(33,26,'blue'),(29,22,'gold')]:
        c.shape('ellipse',(x-1.8,y-1.8,x+1.8,y+1.8),*colors[col],outline=c.edge,width=.4)
    c.line([(21,24),(23,24)],c.edge,1)
    c.line([(25,24),(27,24)],c.edge,1)
    c.arc((7,10,41,34),195,330,'#ffffff',1.1)


def globe(c, colors):
    c.shape('ellipse',(7,6,41,40),*colors['blue'],outline=c.edge,width=1.1)
    if c.style!='platinum':
        c.shape('poly',points=[(13,10),(19,9),(24,13),(21,19),(16,19),(17,25),(13,23),(10,17)],top=colors['green'][0],bottom=colors['green'][1])
        c.shape('poly',points=[(25,25),(33,24),(35,29),(29,35),(25,33),(24,29)],top=colors['green'][0],bottom=colors['green'][1])
    c.arc((14,6,34,40),0,360,'#d7f4ff',.8)
    c.arc((7,15,41,30),0,360,'#d7f4ff',.8)
    c.line([(24,7),(24,39)],'#d7f4ff',.7)
    c.gloss((8,7,40,39),130)


def finder(c, colors):
    if c.style=='xp':
        panes=[([(7,9),(21,7),(21,21),(7,23)],'red'), ([(24,7),(39,10),(39,24),(24,21)],'green'),
               ([(7,26),(21,24),(21,38),(7,40)],'blue'), ([(24,24),(39,27),(39,41),(24,38)],'gold')]
        for pts,col in panes:c.shape('poly',points=pts,top=colors[col][0],bottom=colors[col][1],outline=c.edge,width=.6)
        return
    if c.style=='winter':
        for a in range(6):
            theta=a*math.tau/6
            v=(math.cos(theta),math.sin(theta))
            c.line([(24,24),(24+17*v[0],24+17*v[1])],'#eaffff',2)
            for sign in (-1,1):
                t=theta+sign*math.pi/3
                c.line([(24+10*v[0],24+10*v[1]),(24+10*v[0]-6*math.cos(t),24+10*v[1]-6*math.sin(t))],'#eaffff',1.5)
        return
    if c.style=='ocean':
        for box in [(7,13,29,35),(25,7,41,23),(29,29,41,41)]:
            c.shape('ellipse',box,*colors['blue'],outline='#edffff',width=1)
            c.gloss(box,150)
        return
    c.shape('round',(7,6,41,41),*colors['blue'],outline=c.edge,radius=2 if c.style=='platinum' else 4)
    c.shape('poly',points=[(24,7),(40,7),(40,40),(23,40),(23,27),(19,27),(24,7)],top='#f1f6fa',bottom='#b8cde2',outline=None)
    c.line([(24,8),(19,26),(24,26),(24,34)],c.edge,1.1)
    c.line([(15,16),(15,21)],c.edge,1.5)
    c.line([(32,16),(32,21)],c.edge,1.5)
    c.arc((13,21,35,33),5,175,c.edge,1.2)
    if c.style=='platinum':c.bevel((8,7,40,40))
    else:c.gloss((8,7,39,25),110)


def folder(c, colors):
    col=colors['gold'] if c.style=='xp' else colors['blue']
    c.shape('poly',points=[(7,12),(19,12),(23,16),(40,16),(40,37),(7,37)],top=col[0],bottom=col[1],outline=c.edge)
    c.shape('poly',points=[(7,21),(43,19),(38,39),(5,39)],top=col[0],bottom=col[1],outline=c.edge)
    c.line([(8,22),(40,20)],'#f4f8ff',.9)
    if c.style=='platinum':c.line([(7,13),(18,13),(22,17),(39,17)],'#ffffff',.7)


def disc(c, colors):
    c.shape('ellipse',(6,6,42,42),*colors['silver'],outline=c.edge,width=1)
    c.shape('poly',points=[(24,24),(10,11),(15,8)],top=colors['violet'][0],bottom=colors['violet'][1])
    c.shape('poly',points=[(24,24),(36,39),(40,34)],top=colors['green'][0],bottom=colors['green'][1])
    c.shape('poly',points=[(24,24),(8,34),(10,39)],top=colors['blue'][0],bottom=colors['blue'][1])
    c.shape('ellipse',(18,18,30,30),*colors['silver'],outline='#8797a9',width=.8)
    c.shape('ellipse',(21,21,27,27),*colors['dark'],outline='#faffff',width=.6)
    c.arc((9,9,39,39),195,310,'#ffffff',1.2)


def badge(c, col, glyph='gear'):
    c.shape('ellipse',(28,28,44,44),*col,outline=c.edge,width=.7)
    if glyph=='up':
        c.shape('poly',points=[(36,31),(31,36),(34,36),(34,40),(38,40),(38,36),(41,36)],top='#f8ffff')
    elif glyph=='gear':
        for a in range(8):
            t=a*math.tau/8;c.line([(36+3*math.cos(t),36+3*math.sin(t)),(36+5*math.cos(t),36+5*math.sin(t))],'#ffffff',1.7)
        c.shape('ellipse',(33,33,39,39),'#ffffff')
        c.shape('ellipse',(35,35,37,37),c.edge)
    elif glyph=='arrow':c.line([(33,34),(39,37),(33,40)],'#ffffff',1.5)


def draw_symbol(style, symbol):
    c=Canvas(style);p=scheme(style)
    if symbol=='gear':gear(c,p)
    elif symbol in ('monitor','tv','happy'):monitor(c,p,happy=symbol=='happy',tv=symbol=='tv')
    elif symbol=='photo':photo(c,p)
    elif symbol=='note':note(c,p)
    elif symbol=='film':film(c,p)
    elif symbol=='game':gamepad(c,p)
    elif symbol=='globe':globe(c,p)
    elif symbol=='finder':finder(c,p)
    elif symbol=='folder':folder(c,p)
    elif symbol in ('disc','disc_update'):
        disc(c,p)
        if symbol=='disc_update':badge(c,p['green'],'up')
    elif symbol=='itunes':
        disc(c,p)
        small=draw_symbol(style,'note').resize((28,28),Image.Resampling.LANCZOS)
        c.im.alpha_composite(small.resize((28*S,28*S),Image.Resampling.BICUBIC),(18*S,18*S))
    elif symbol=='quicktime':
        c.shape('ellipse',(7,5,40,38),*p['blue'],outline=c.edge,width=1)
        c.shape('ellipse',(15,13,32,30),*p['silver'],outline=c.edge,width=.7)
        c.shape('poly',points=[(29,29),(35,28),(42,40),(34,42)],top=p['blue'][0],bottom=p['blue'][1],outline=c.edge,width=.8)
        c.arc((10,8,37,35),195,310,'#e9faff',1.3)
        c.gloss((8,6,39,34),140)
    elif symbol=='prefs':
        c.shape('round',(5,8,43,39),*p['silver'],outline=c.edge,radius=3)
        c.shape('round',(6,9,42,16),'#f4faff','#adbdca',radius=2)
        for x,key in [(10,'red'),(15,'gold'),(20,'green')]:c.shape('ellipse',(x-1.5,10,x+1.5,13),*p[key],outline=c.edge,width=.3)
        for y in (20,29):
            for x,key in [(12,'blue'),(23,'violet'),(34,'green')]:
                c.shape('round',(x-3,y,x+3,y+5),*p[key],outline=c.edge,width=.4,radius=1)
                c.line([(x-3,y+7),(x+3,y+7)],'#607080',.55)
    elif symbol=='camera':
        c.shape('round',(6,14,42,36),*p['silver'],outline=c.edge,radius=2)
        c.shape('round',(14,10,27,17),*p['dark'],outline=c.edge,radius=1)
        c.shape('ellipse',(17,17,35,35),*p['dark'],outline='#f9feff')
        c.shape('ellipse',(21,21,31,31),*p['blue'],outline='#bcecff',width=.6)
        c.shape('ellipse',(23,22,26,25),'#f8ffff')
        c.shape('rect',(9,18,14,22),*p['gold'],outline=c.edge,width=.5)
        c.line([(8,16),(40,16)],'#ffffff',.7)
    elif symbol=='memory':
        c.shape('poly',points=[(13,5),(31,5),(36,10),(36,42),(12,42),(12,5)],top=p['blue'][0],bottom=p['blue'][1],outline=c.edge)
        c.shape('rect',(16,8,28,14),'#f3faff',outline=c.edge,width=.6)
        for x in (17,21,25,29):c.shape('rect',(x,34,x+2,39),*p['gold'],outline=c.edge,width=.3)
        c.line([(16,19),(31,19),(31,29),(16,29),(16,19)],'#d5eaff',.7)
    elif symbol=='save':
        c.shape('poly',points=[(9,6),(35,6),(40,11),(40,41),(8,41),(8,6)],top=p['blue'][0],bottom=p['blue'][1],outline=c.edge)
        c.shape('rect',(15,7,32,20),*p['silver'],outline=c.edge,width=.7)
        c.shape('rect',(26,9,29,18),*p['dark'])
        c.shape('rect',(14,26,34,38),'#f4f7ed',outline=c.edge,width=.6)
        for y in (29,32,35):c.line([(17,y),(30,y)],'#9bacb5',.6)
    elif symbol=='share':
        monitor(c,p)
        c.line([(13,6),(17,3),(23,3),(27,6)],p['green'][1],2)
        c.shape('poly',points=[(25,3),(29,6),(25,9)],top=p['green'][0],bottom=p['green'][1])
    elif symbol in ('network_update','network_settings','browser','search'):
        globe(c,p)
        if symbol=='network_update':badge(c,p['green'],'up')
        if symbol=='network_settings':badge(c,p['silver'],'gear')
        if symbol=='browser':
            c.shape('poly',points=[(30,26),(31,41),(35,37),(38,43),(41,41),(38,35),(43,34)],top='#ffffff',bottom='#c5e4f5',outline=c.edge,width=.7)
        if symbol=='search':
            c.line([(30,30),(41,41)],c.edge,5)
            c.line([(30,30),(41,41)],p['silver'][1],3)
            c.shape('ellipse',(18,18,35,35),*p['silver'],outline=c.edge,width=.9)
            c.shape('ellipse',(21,21,32,32),*p['blue'],outline=c.edge,width=.6)
    elif symbol=='usb':
        c.shape('round',(11,6,37,41),*p['blue'],outline=c.edge,radius=5)
        c.line([(24,35),(24,12)],'#ffffff',2)
        c.shape('poly',points=[(20,14),(24,8),(28,14)],top='#ffffff')
        c.line([(24,28),(17,23),(17,17)],'#ffffff',1.7)
        c.line([(24,25),(31,20),(31,15)],'#ffffff',1.7)
        c.shape('ellipse',(15,14,19,18),'#ffffff')
        c.shape('rect',(29,11,33,15),'#ffffff')
        c.shape('ellipse',(21,33,27,39),'#ffffff')
        c.gloss((12,7,36,40),80)
    elif symbol in ('film_settings','photo_settings','system','external','remote'):
        if symbol=='film_settings':film(c,p)
        elif symbol=='photo_settings':photo(c,p)
        else:monitor(c,p,happy=style=='platinum')
        if symbol in ('external','remote'):badge(c,p['blue'],'arrow')
        else:badge(c,p['silver'],'gear')
    elif symbol=='palette':
        c.shape('ellipse',(7,8,41,39),*p['silver'],outline=c.edge,width=1)
        for x,y,key in [(16,16,'red'),(25,13,'gold'),(33,18,'green'),(13,25,'blue')]:c.shape('ellipse',(x-3,y-3,x+3,y+3),*p[key],outline=c.edge,width=.5)
        c.line([(25,35),(37,12)],c.edge,4)
        c.line([(25,35),(37,12)],p['gold'][1],2)
        c.shape('ellipse',(22,30,28,37),*p['blue'],outline=c.edge,width=.5)
    elif symbol=='clock':
        c.shape('ellipse',(6,6,42,42),*p['silver'],outline=c.edge,width=1)
        c.shape('ellipse',(10,10,38,38),'#f7fcff',outline=c.edge,width=.8)
        for a in range(12):
            t=a*math.tau/12;c.line([(24+11*math.cos(t),24+11*math.sin(t)),(24+12.5*math.cos(t),24+12.5*math.sin(t))],c.edge,.8)
        c.line([(24,15),(24,24),(31,28)],c.edge,1.5)
        c.shape('ellipse',(22.5,22.5,25.5,25.5),*p['blue'])
    elif symbol=='battery':
        c.shape('round',(13,10,35,40),*p['silver'],outline=c.edge,radius=2)
        c.shape('rect',(20,6,28,10),*p['dark'],outline=c.edge,width=.7)
        c.shape('rect',(17,14,31,36),*p['green'],outline=c.edge,width=.6)
        c.shape('poly',points=[(25,16),(19,25),(24,25),(22,34),(30,23),(25,23)],top='#ffffff',bottom='#eaffc9',outline=None)
    elif symbol=='sound':
        c.shape('poly',points=[(8,19),(16,19),(25,11),(25,37),(16,29),(8,29)],top=p['silver'][0],bottom=p['silver'][1],outline=c.edge,width=1)
        c.shape('rect',(10,21,16,27),*p['dark'])
        c.arc((20,15,35,33),300,60,p['blue'][1],2)
        c.arc((20,8,44,40),300,60,p['blue'][1],2)
    elif symbol=='lock':
        c.shape('round',(14,6,34,29),*p['silver'],outline=c.edge,radius=9)
        c.shape('round',(18,10,30,27),*p['dark'],outline=c.edge,radius=5)
        c.shape('round',(10,21,38,41),*p['gold'],outline=c.edge,radius=2)
        c.shape('ellipse',(22,27,27,32),*p['dark'])
        c.shape('rect',(23,30,26,35),*p['dark'])
        c.line([(12,23),(36,23)],'#ffffe6',1)
    elif symbol in ('rss','rss_settings'):
        c.shape('round',(7,7,41,41),*p['gold' if style in ('xp','ocean') else 'blue'],outline=c.edge,radius=5)
        c.shape('ellipse',(13,30,18,35),'#ffffff')
        c.arc((3,19,28,44),270,0,'#ffffff',3)
        c.arc((-6,10,37,53),270,0,'#ffffff',3)
        if symbol=='rss_settings':badge(c,p['silver'],'gear')
    elif symbol=='book':
        c.shape('poly',points=[(6,10),(21,8),(24,12),(27,8),(42,10),(42,38),(28,36),(24,40),(20,36),(6,38)],top=p['silver'][0],bottom=p['silver'][1],outline=c.edge)
        c.line([(24,12),(24,38)],c.edge,.9)
        for y in (16,21,26,31):
            c.line([(10,y),(20,y-1)],'#8296ae',.6);c.line([(28,y-1),(38,y)],'#8296ae',.6)
    elif symbol=='radio':
        c.line([(15,11),(33,4)],c.edge,1.2)
        c.shape('round',(6,13,42,38),*p['silver'],outline=c.edge,radius=3)
        c.shape('round',(10,17,26,33),*p['dark'],outline=c.edge,radius=6)
        c.shape('ellipse',(13,20,23,30),*p['silver'],outline=c.edge,width=.6)
        c.shape('rect',(30,18,38,22),*p['blue'],outline=c.edge,width=.6)
        c.shape('ellipse',(31,26,37,32),*p['gold'],outline=c.edge,width=.7)
    elif symbol=='user':
        c.shape('round',(7,6,41,42),*p['silver'],outline=c.edge,radius=4)
        c.shape('ellipse',(18,10,31,23),*p['gold'],outline=c.edge,width=.7)
        c.shape('round',(13,24,36,38),*p['blue'],outline=c.edge,radius=8)
        c.gloss((14,25,35,38),85)
    elif symbol=='bluetooth':
        c.shape('ellipse',(8,5,40,43),*p['blue'],outline=c.edge,width=1)
        c.line([(18,14),(30,30),(24,36),(24,10),(30,16),(18,32)],'#ffffff',2)
        c.gloss((9,6,39,42),90)
    elif symbol=='sensme':
        note(c,p);c.shape('ellipse',(26,32,34,40),*p['red']);c.shape('ellipse',(32,32,40,40),*p['red'])
        c.shape('poly',points=[(26,37),(39,37),(33,44)],top=p['red'][0],bottom=p['red'][1])
    elif symbol in ('wrench','adjust'):
        if symbol=='wrench':
            c.line([(13,36),(30,19)],c.edge,8)
            c.line([(13,36),(30,19)],p['silver'][1],5.8)
            c.shape('poly',points=[(25,8),(25,17),(31,22),(40,17),(41,8),(35,14),(31,14)],top=p['silver'][0],bottom=p['silver'][1],outline=c.edge)
            c.shape('ellipse',(9,32,16,39),*p['silver'],outline=c.edge,width=.7)
            c.shape('ellipse',(11,34,14,37),*p['dark'])
        else:
            c.shape('round',(8,8,40,40),*p['silver'],outline=c.edge,radius=3)
            for x,cy in [(16,18),(24,30),(32,22)]:
                c.line([(x,13),(x,35)],c.edge,1)
                c.shape('round',(x-3,cy-3,x+3,cy+3),*p['blue'],outline=c.edge,radius=1)
    else:raise ValueError(symbol)
    return c.finish()


def icon(style, symbol, size=(48,48)):
    im=draw_symbol(style,symbol)
    if style in ('winter','ocean'):
        base=Canvas(style)
        if style=='winter':
            pts=[(14,4),(34,4),(44,14),(44,34),(34,44),(14,44),(4,34),(4,14)]
            base.shape('poly',points=pts,top='#d9f7ff',bottom='#39698f',outline='#e7fbff',width=1)
            base.line([(14,6),(33,6),(42,15)],'#ffffff',.8)
        else:
            base.shape('ellipse',(4,4,44,44),'#9decfc','#007baf',outline='#d8ffff',width=1)
            base.arc((7,7,41,41),35,140,'#74edfc',1.1)
        base.gloss((5,5,43,43),155)
        out=base.finish()
        inner=im.resize((33,33),Image.Resampling.LANCZOS)
        out.alpha_composite(inner,(7,7));im=out
    w,h=size
    if (w,h)==(64,48):
        out=Image.new('RGBA',(64,48));out.alpha_composite(im,(8,0));return out
    return im if size==(48,48) else im.resize(size,Image.Resampling.LANCZOS)


def focus(body, size):
    w,h=size
    a=Image.new('L',size)
    a.paste(body.getchannel('A'),((w-body.width)//2,(h-body.height)//2))
    broad=np.array(a.filter(ImageFilter.GaussianBlur(2.4)),float)
    edge=np.array(a.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(.7)),float)
    core=np.array(a,float)
    # Soft white halo and conservative bright edge. The body stays independently rendered.
    alpha=np.clip(.52*broad+.34*edge-.12*core,0,164)
    alpha=np.round(alpha/255*63)*255/63
    alpha[alpha<8]=0
    alpha[:2,:]=0;alpha[-2:,:]=0;alpha[:,:2]=0;alpha[:,-2:]=0
    arr=np.zeros((h,w,4),np.uint8)
    arr[alpha>0,:3]=255
    arr[:,:,3]=np.uint8(np.rint(alpha))
    return Image.fromarray(arr)


CATEGORIES={1:'gear',2:'photo',3:'note',4:'film',5:'tv',6:'game',7:'globe',8:'finder'}
FIRST={2:'memory',4:'disc',6:'camera',8:'share',10:'save',12:'disc_update',
       14:'network_update',16:'usb',18:'film_settings',20:'photo_settings',22:'system',
       24:'palette',26:'clock',28:'battery',30:'external',32:'sound',34:'lock',
       36:'rss_settings',38:'network_settings',40:'book',42:'remote',44:'radio',
       46:'rss',48:'browser',50:'search',52:'user',54:'finder',56:'bluetooth',58:'sensme'}
