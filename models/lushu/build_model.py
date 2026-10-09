"""Original Lushu: 19 cuboids, three-piece red horse tail, pixel atlas."""
import base64
import json
import math
import uuid
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
SIZE = 128
atlas = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
cursor = [1, 1, 0]
patches = {}
elements = []
groups = []

def uid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'shanhaijing:lushu:' + name))

def tint(color, delta):
    return tuple(max(0, min(255, c + delta)) for c in color) + (255,)

def paint(kind, face, w, h, start, size):
    key = (kind, face, w, h, tuple(start) if kind in ('body', 'chest') else ())
    if key in patches:
        return patches[key]['uv']
    x, y, row = cursor
    if x + w + 1 > SIZE:
        x, y, row = 1, y + row + 1, 0
    assert y + h + 1 <= SIZE, (kind, y, h)
    cursor[:] = [x + w + 1, y, max(row, h)]
    tile = Image.new('RGBA', (w, h))
    p = tile.load()
    for v in range(h):
        for u in range(w):
            shade = 10 if face == 'up' else -12 if face == 'down' else 0
            fleck = -5 if (u * 11 + v * 7) % 31 == 0 else 0
            if kind in ('body', 'chest'):
                if face in ('east', 'west'):
                    z = start[2] + (u if face == 'west' else w - 1 - u)
                    height = start[1] + h - 1 - v
                    # Shared world coordinates keep shoulder and back stripes aligned.
                    depth = 26 - height
                    band = (z + 12) / 4.1
                    k = round(band)
                    drift = round(math.sin(depth * .55 + k * 1.7) * 1.15)
                    width = 1.4 if depth < 5 else .7
                    length = 5 + (k * 3) % 5
                    stripe = abs(z + 12 - k * 4.1 - drift) <= width and depth < length
                    cream = height < 18 + ((int(z) + 25) % 5 == 0)
                elif face in ('up', 'down'):
                    z = start[2] + v
                    k = round((z + 12) / 4.1)
                    drift = round(math.sin((u - w / 2) * .55 + k * 1.7) * 1.15)
                    stripe = abs(z + 12 - k * 4.1 - drift) <= 1.4
                    cream = face == 'down'
                else:
                    stripe = (u + v // 3) % 6 < 2 and v < h - 2
                    cream = v >= h - 2
                col = (44, 32, 25) if stripe and not cream else (232, 215, 179) if cream else (205, 129, 49)
            elif kind == 'neck':
                stripe = (v + u // 3) % 5 < 2 and face != 'down'
                col = (46, 32, 25) if stripe else (211, 141, 64)
            elif kind.startswith('upper'):
                stripe = (v + u // 2) % 5 == 1
                col = (49, 35, 28) if stripe else (196, 122, 47)
            elif kind.startswith('lower'):
                if v >= h - 2 or face == 'down':
                    col = (43, 38, 34)
                elif v >= h - 4:
                    col = (219, 196, 156)
                else:
                    col = (46, 33, 26) if (v + u // 2) % 5 == 1 else (200, 131, 56)
            elif kind.startswith('tail'):
                col = [(166, 40, 34), (199, 56, 43), (216, 75, 50)][u % 3]
                if v >= h - 2:
                    col = (149, 31, 31)
            elif kind == 'mane':
                col = (49, 35, 30) if u % 2 else (68, 43, 31)
            else:
                col = (245, 242, 226)
            p[u, v] = tint(col, shade + fleck)
    d = ImageDraw.Draw(tile)
    if kind == 'head' and face in ('east', 'west'):
        ex = w - 3 if face == 'east' else 1
        d.rectangle((ex, 2, ex + 1, 3), fill='#342a26')
        d.point((ex, 2), fill='#ce943b')
        d.point((ex + 1, 2), fill='#fff8e7')
        d.line((0, h - 1, w - 1, h - 1), fill='#c8c3b1')
    if kind == 'muzzle':
        if face == 'north':
            d.point((0, 1), fill='#63584c')
            d.point((w - 1, 1), fill='#63584c')
            d.line((0, h - 1, w - 1, h - 1), fill='#c2baaa')
        if face in ('east', 'west'):
            ex = w - 2 if face == 'east' else 1
            d.point((ex, 1), fill='#63584c')
            d.line((0, h - 1, w - 1, h - 1), fill='#c8c1b1')
    if kind == 'ear' and face == 'north':
        d.line((0, 1, 0, h - 2), fill='#bfa59a')
        d.line((1, 1, 1, h - 2), fill='#ddc1b0')
    atlas.paste(tile, (x, y))
    uv = [x, y, x + w, y + h]
    patches[key] = {'kind': kind, 'face': face, 'uv': uv, 'size': [w, h]}
    return uv

def bone(name, origin, parent=None, rotation=None):
    g = dict(name=name, uuid=uid(name), origin=origin, rotation=rotation or [0, 0, 0], children=[], export=True, isOpen=True)
    (groups if parent is None else parent['children']).append(g)
    return g

def cube(name, kind, start, size, group, rotation=None, origin=None):
    w, h, z = size
    dims = dict(north=(w, h), south=(w, h), east=(z, h), west=(z, h), up=(w, z), down=(w, z))
    faces = {f: dict(uv=paint(kind, f, a, b, start, size), texture=0) for f, (a, b) in dims.items()}
    c = dict(name=name, uuid=uid(name), type='cube', **{'from': start}, to=[a+b for a,b in zip(start,size)], origin=origin or group['origin'], rotation=rotation or [0, 0, 0], box_uv=False, autouv=0, faces=faces, visibility=True, export=True)
    elements.append(c)
    group['children'].append(c['uuid'])

root = bone('root', [0, 0, 0])
body = bone('body', [0, 21, 0], root)
cube('body_block', 'body', [-5, 16, -11], [10, 10, 22], body)
cube('chest_block', 'chest', [-4, 15, -12], [8, 11, 7], body)
neck = bone('neck', [0, 23, -8], body)
cube('neck_block', 'neck', [-3, 22, -12], [6, 12, 7], neck, [-25, 0, 0])
cube('mane_block', 'mane', [-.5, 23, -5.8], [1, 12, 2], neck, [-25, 0, 0])
head = bone('head', [0, 33, -13], neck, [-15, 0, 0])
cube('head_white', 'head', [-2.5, 30, -17], [5, 7, 7], head)
cube('muzzle_white', 'muzzle', [-2, 30, -22], [4, 4, 6], head)
for side, sign in [('left', 1), ('right', -1)]:
    ear = bone('ear_' + side, [sign * 1.7, 36.5, -11.5], head, [0, 0, -sign * 9])
    cube('ear_' + side + '_white', 'ear', [sign * 1.7 - 1, 36.5, -12.5], [2, 4, 2], ear)
    for pos, z in [('front', -8), ('hind', 8)]:
        thigh = bone('leg_' + pos + '_' + side, [sign * 3.4, 18, z], body)
        width = 3 if pos == 'front' else 4
        cube('upper_' + pos + '_' + side, 'upper_' + pos, [sign * 3.4 - width / 2, 8, z - 2], [width, 10, 4], thigh)
        shin = bone('lower_' + pos + '_' + side, [sign * 3.4, 8, z], thigh)
        cube('lower_' + pos + '_' + side + '_with_hoof', 'lower_' + pos, [sign * 3.4 - 1.5, 0, z - 1.5], [3, 8, 3], shin)
tail = bone('tail_base', [0, 24, 10.5], body, [-25, 0, 0])
cube('tail_red_base', 'tail_base', [-1, 18, 10.5], [2, 6, 2], tail)
mid = bone('tail_mid', [0, 18.5, 11.5], tail, [12, 0, 0])
cube('tail_red_mid', 'tail_mid', [-1.5, 12, 10], [3, 7, 3], mid)
tip = bone('tail_tip', [0, 12.5, 11.5], mid, [8, 0, 0])
cube('tail_red_tip', 'tail_tip', [-1, 6, 10.5], [2, 7, 2], tip)

assert len(elements) == 19
assert sum(c['name'].startswith('tail_red') for c in elements) == 3
atlas.save(OUT / 'lushu.png')
atlas.resize((768, 768), Image.Resampling.NEAREST).save(OUT / 'lushu_texture_preview.png')
model = dict(meta=dict(format_version='5.0', model_format='bedrock', box_uv=False), name='鹿蜀 · 19方块 · 三段红尾', model_identifier='shanhaijing.lushu', visible_box=[4, 4, 1.25], resolution=dict(width=SIZE, height=SIZE), elements=elements, outliner=groups, textures=[dict(name='lushu.png', id='0', uuid=uid('texture'), width=SIZE, height=SIZE, uv_width=SIZE, uv_height=SIZE, path=str(OUT / 'lushu.png'), source='data:image/png;base64,'+base64.b64encode((OUT / 'lushu.png').read_bytes()).decode())])
(OUT / 'lushu.bbmodel').write_text(json.dumps(model, ensure_ascii=False, indent=2), encoding='utf-8')
(OUT / 'uv-layout.json').write_text(json.dumps(list(patches.values()), indent=2), encoding='utf-8')
print(json.dumps({'cubes':len(elements),'tail_cubes':3,'texture':[SIZE,SIZE],'atlas_used_height':cursor[1]+cursor[2],'path':str(OUT / 'lushu.bbmodel')}, ensure_ascii=False))
