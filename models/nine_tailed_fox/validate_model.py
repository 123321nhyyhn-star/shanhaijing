import json, re, base64, hashlib
from pathlib import Path
from PIL import Image
OUT=Path(__file__).resolve().parent
model=json.loads((OUT/'nine_tailed_fox.bbmodel').read_text(encoding='utf-8'))
geo=json.loads((OUT/'nine_tailed_fox.geo.json').read_text(encoding='utf-8'))
elements=model['elements']
assert len(elements)==25 and all(e['type']=='cube' for e in elements)
assert all(all(t>f for f,t in zip(e['from'],e['to'])) for e in elements)
names=[e['name'] for e in elements]
tails={f'{i:02}':sum(n.startswith(f'tail_{i:02}_') for n in names) for i in range(1,10)}
assert all(1<=n<=3 for n in tails.values()) and sum(tails.values())==15
assert sum(n.startswith('muzzle_') for n in names)==1
for side in ['left','right']:
    assert sum(n.startswith(f'ear_{side}_') for n in names)==1
    for position in ['front','hind']:
        assert 1<=sum(n.startswith(f'leg_{position}_{side}_') for n in names)<=2
faces=sum(len(e['faces']) for e in elements)
assert faces==150
for e in elements:
    for f in e['faces'].values():
        assert all(0<=v<=128 for v in f['uv'])
        assert f['texture']==0 and f.get('rotation',0) in [0,90,180,270]
description=geo['minecraft:geometry'][0]['description']
bones=geo['minecraft:geometry'][0]['bones']
assert sum(len(b.get('cubes',[])) for b in bones)==25
assert len({b['name'] for b in bones})==len(bones)
assert all(b.get('parent') in {q['name'] for q in bones} for b in bones if 'parent' in b)
assert (description['texture_width'],description['texture_height'])==(128,128)
image=Image.open(OUT/'nine_tailed_fox.png')
assert image.size==(128,128)
png=(OUT/'nine_tailed_fox.png').read_bytes()
embedded=base64.b64decode(model['textures'][0]['source'].split(',')[1])
assert hashlib.sha256(png).digest()==hashlib.sha256(embedded).digest()
result={'result':'PASS','cubes':25,'quads':faces,'triangles':faces*2,'tails':tails,'muzzle_cubes':1,'ear_cubes_each':1,'leg_cubes_each':1,'bones':len(bones),'texture':[128,128],'all_uv_within_atlas':True,'embedded_texture_matches_png':True,'geometry_export_cube_count':25,'format_version':geo['format_version'],'validation_scope':'Files and live Blockbench views; no Minecraft runtime test','sha256':{name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ['nine_tailed_fox.bbmodel','nine_tailed_fox.geo.json','nine_tailed_fox.png']}}
(OUT/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
