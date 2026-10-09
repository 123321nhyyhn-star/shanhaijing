"""Original nine-tailed fox geometry and an exact UV paint guide. No mod assets reused."""
import base64, json, math, uuid
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
SIZE = 128
def uid(): return str(uuid.uuid4())
atlas = Image.new('RGBA', (SIZE, SIZE), (44, 39, 51, 255))
draw = ImageDraw.Draw(atlas)
patches = {}
cursor = [2, 2, 0]
palette = {'white':'#f8f2e5','light':'#fffaf0','shade':'#d7ccc0','fur':'#e7ddd1','red':'#ae474a','rose':'#cf7772','dark':'#342f3c','gold':'#e1a347'}

def tile(kind, face, w, h):
    key = kind + ':' + face
    if key in patches: return patches[key]['uv']
    x,y,row = cursor
    if x+w+2 > SIZE: x,y,row=2,y+row+2,0
    assert y+h+2 <= SIZE
    cursor[:] = [x+w+2,y,max(row,h)]
    uv=[x,y,x+w,y+h]
    base=palette['light' if face=='up' else 'shade' if face=='down' else 'white']
    draw.rectangle([x,y,x+w-1,y+h-1],fill=base)
    if min(w,h)>2:
        draw.line([(x,y+h-1),(x+w-1,y+h-1)],fill=palette['fur'])
        for px in range(1,w-1,4):
            py=1+(px*3)%max(1,h-2)
            draw.point((x+px,y+py),fill=palette['fur'])
    if kind=='head':
        if face=='north':
            for px in [1,w-3]:
                draw.rectangle([x+px,y+2,x+px+1,y+3],fill=palette['dark'])
                draw.point((x+px+(0 if px==1 else 1),y+2),fill=palette['gold'])
            draw.point((x+w//2,y+1),fill=palette['red'])
            draw.point((x+w//2,y),fill=palette['rose'])
        if face in ['east','west']:
            px=w-2 if face=='east' else 1
            draw.rectangle([x+px,y+2,x+px,y+3],fill=palette['dark'])
            draw.point((x+px,y+2),fill=palette['gold'])
            draw.line([(x+1,y+h-2),(x+w-2,y+h-2)],fill=palette['shade'])
    if kind=='muzzle':
        if face=='north':
            draw.rectangle([x,y,x+w-1,y],fill=palette['dark'])
            draw.point((x+w//2,y+1),fill=palette['dark'])
        if face in ['east','west']:
            draw.line([(x,y+h-1),(x+w-1,y+h-1)],fill=palette['shade'])
    if kind=='ear' and face=='north':
        draw.rectangle([x+1,y+1,x+w-2,y+h-2],fill=palette['red'])
        draw.point((x+1,y+1),fill=palette['rose'])
    if kind.startswith('leg') and face not in ['up','down']:
        draw.line([(x,y+h-1),(x+w-1,y+h-1)],fill=palette['shade'])
    if kind in ['tail_tip','tail_long']:
        if face in ['east','west','up','down']:
            for py in range(max(0,h-3),h):
                for px in range(w):
                    if py>=h-2 or px==w//2: draw.point((x+px,y+py),fill=palette['rose' if py==h-3 else 'red'])
        if face=='south': draw.rectangle([x,y,x+w-1,y+h-1],fill=palette['red'])
    patches[key]={'uv':uv,'kind':kind,'face':face,'size':[w,h]}
    return uv

elements=[]
groups=[]
def group(name,origin,parent=None,rotation=None):
    g={'name':name,'uuid':uid(),'origin':origin,'rotation':rotation or [0,0,0],'children':[],'export':True,'isOpen':True}
    (parent['children'] if parent else groups).append(g)
    return g
def cube(name,kind,start,size,bone):
    x,y,z=start; w,h,d=size
    face_sizes={'north':(w,h),'south':(w,h),'east':(d,h),'west':(d,h),'up':(w,d),'down':(w,d)}
    faces={f:{'uv':tile(kind,f,int(a),int(b)),'texture':0} for f,(a,b) in face_sizes.items()}
    c={'name':name,'uuid':uid(),'type':'cube','from':start,'to':[x+w,y+h,z+d],'origin':bone['origin'],'rotation':[0,0,0],'box_uv':False,'autouv':0,'faces':faces,'visibility':True,'export':True}
    elements.append(c); bone['children'].append(c['uuid'])
    return c

root=group('root',[0,0,0])
body=group('body',[0,8,0],root)
cube('body_block','body',[-3.5,5,-7],[7,6,14],body)
neck=group('neck',[0,9,-6],body)
cube('neck_block','neck',[-2.5,7,-9],[5,5,4],neck)
head=group('head',[0,11,-7],neck)
cube('head_block','head',[-3.5,8,-12],[7,6,6],head)
muzzle=group('muzzle',[0,10,-12],head)
cube('muzzle_single_block','muzzle',[-1.5,8.5,-16],[3,3,4],muzzle)
for side,sign in [('left',1),('right',-1)]:
    ear=group('ear_'+side,[sign*2.3,13.5,-9],head,[0,0,-sign*10])
    cube('ear_'+side+'_single_block','ear',[sign*2.3-1.5,13.5,-9.5],[3,4,1],ear)
    for position,z in [('front',-5),('hind',5)]:
        leg=group('leg_'+position+'_'+side,[sign*2.5,5.8,z],body)
        width=2 if position=='front' else 3
        cube('leg_'+position+'_'+side+'_single_block','leg_'+position,[sign*2.5-width/2,0,z-1.5],[width,6,3],leg)

tails=group('tails',[0,9,6],body)
for i,theta in enumerate([-80,-60,-40,-20,0,20,40,60,80],1):
    angle=math.radians(theta)
    direction=[math.sin(angle)*.95,math.cos(angle)*.95,.6]
    norm=math.sqrt(sum(v*v for v in direction)); dx,dy,dz=[v/norm for v in direction]
    pitch=-math.degrees(math.asin(dy)); yaw=math.degrees(math.atan2(dx,dz))
    origin=[(i-5)*.35,9,6.5]
    tail=group(f'tail_{i:02}',origin,tails,[pitch,yaw,0])
    x,y,z=origin
    single=i in [4,5,6]
    length=17 if single else 11
    cube(f'tail_{i:02}_'+('single' if single else 'base'),'tail_long' if single else 'tail_base',[x-1.5,y-1.5,z-.3],[3,3,length],tail)
    if not single:
        tip=group(f'tail_{i:02}_tip',[x,y,z+10.5],tail,[-8,0,0])
        cube(f'tail_{i:02}_tip','tail_tip',[x-1,y-1,z+10.3],[2,2,7],tip)

assert len(elements)==25
texture=OUT/'uv_paint_guide.png'
atlas.save(texture)
atlas.resize((1024,1024),Image.Resampling.NEAREST).save(OUT/'uv_paint_guide_1024.png')
model={'meta':{'format_version':'5.0','model_format':'bedrock','box_uv':False},'name':'九尾狐 · 25方块','model_identifier':'shanhaijing.nine_tailed_fox','visible_box':[6,5,1], 'resolution':{'width':SIZE,'height':SIZE},'elements':elements,'outliner':groups,'textures':[{'name':'nine_tailed_fox.png','id':'0','uuid':uid(),'width':SIZE,'height':SIZE,'uv_width':SIZE,'uv_height':SIZE,'source':'data:image/png;base64,'+base64.b64encode(texture.read_bytes()).decode()}]}
(OUT/'nine_tailed_fox_blockout.bbmodel').write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'uv-layout.json').write_text(json.dumps(patches,indent=2),encoding='utf-8')
print(json.dumps({'cubes':len(elements),'faces':150,'texture':[SIZE,SIZE],'patches':len(patches),'output':str(OUT)},ensure_ascii=False))
