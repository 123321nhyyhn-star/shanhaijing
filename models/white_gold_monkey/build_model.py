"""Original cuboid model and hand-designed pixel atlas from the supplied multiview."""
from pathlib import Path
import base64, hashlib, json, math, random, uuid
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent
SIZE = 512
atlas = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
elements, groups, roots, nodes, uv_records = [], [], [], {}, []
P = {
 'white': ['#fff4e6','#f7e8d8','#eedaca','#e4cdbb','#fffaf0'],
 'gold': ['#efac20','#ffcb43','#db8b10','#ffe16a','#c77812'],
 'skin': ['#ffd7b6','#f8caa8','#ffe1c5','#efbd9b'],
 'brown': ['#6d331b','#894323','#a3562a','#5a2818','#bc7133'],
 'dark': ['#442319','#532a1c','#371c14'],
 'nose': ['#60321e','#7a4023','#4a251b'],
}

def uid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, 'original.white_gold_monkey/'+name))

def group(name, origin, parent=None):
    g = dict(name=name, uuid=uid(name), origin=origin, rotation=[0,0,0], export=True,
             visibility=True, isOpen=True, color=len(groups)%8, children=[])
    groups.append(g)
    node = dict(uuid=g['uuid'], isOpen=True, children=[])
    nodes[name] = node
    (nodes[parent]['children'] if parent else roots).append(node)
    return name

cursor_x, cursor_y, row_h = 2, 2, 0
def pack(w,h):
    global cursor_x, cursor_y, row_h
    if cursor_x+w+2 > SIZE:
        cursor_x=2; cursor_y+=row_h+4; row_h=0
    if cursor_y+h+2 > SIZE: raise RuntimeError('Atlas full')
    pos=(cursor_x,cursor_y); cursor_x+=w+4; row_h=max(row_h,h)
    return pos

def rect(d, box, color):
    x0,y0,x1,y1=(int(v) for v in box)
    if x1>=x0 and y1>=y0: d.rectangle((x0,y0,x1,y1), fill=color)

def face_art(w,h,mat,name,face):
    seed=int(hashlib.sha256((name+face).encode()).hexdigest()[:8],16)
    rnd=random.Random(seed)
    spotted=mat=='coat'
    pal=P['skin' if mat=='face' else 'white' if spotted or mat in ('bib','ear') else mat]
    im=Image.new('RGBA',(w,h),pal[0]); d=ImageDraw.Draw(im)
    # Small coherent patches, no gradients or anti-aliasing.
    if mat not in ('face','ear','nose','dark'):
        for i in range(max(1,w*h//48)):
            x=rnd.randrange(w); y=rnd.randrange(h)
            rect(d,(x,y,x+rnd.randint(1,3),y+rnd.randint(1,2)),rnd.choice(pal[:3]))
    if mat in ('white','coat','bib','gold','skin','brown'):
        rect(d,(0,h-1,w-1,h-1),pal[2])
        if h>3: rect(d,(0,0,w-1,0),pal[-1] if mat!='skin' else pal[2])
    if spotted and w>=3 and h>=3:
        for i in range(max(1,int(w*h/65))):
            x=rnd.randrange(max(1,w-2)); y=rnd.randrange(max(1,h-2))
            sw=rnd.randint(2,min(6,w)); sh=rnd.randint(2,min(6,h))
            rect(d,(x,y,x+sw,y+sh),P['gold'][i%2])
            rect(d,(x,y+sh-1,x+max(1,sw-2),y+sh),P['gold'][2])
            rect(d,(x+1,y,x+max(1,sw-1),y+1),P['gold'][3])
    if mat=='bib':
        rect(d,(0,0,1,h-1),P['white'][2])
        rect(d,(w-2,0,w-1,h-1),P['white'][1])
    if mat=='ear' and face=='north':
        rim=max(2,round(w*.18)); t=max(2,round(h*.16))
        rect(d,(rim,t,w-rim-1,h-t-1),'#f2c39e')
        rect(d,(rim+1,t+1,w-rim-2,h-t-2),'#ffd5aa')
        rect(d,(rim,t+1,rim+2,h-t-2),'#e9a76a')
        rect(d,(rim+2,t+3,w-rim-2,h-t-3),'#f4b530')
        rect(d,(rim+3,t+2,w-rim-1,t+4),'#ffda68')
    if mat=='face' and face=='north':
        # 36×34 portrait: warm skin, white sclera, amber iris, two glints.
        d.rectangle((0,0,w-1,h-1),fill='#ffdab9')
        rect(d,(0,h-3,w-1,h-1),'#f7c7a4')
        for a in (0.12,0.63):
            x=round(a*w); ew=round(.25*w); y=round(.24*h); eh=round(.36*h)
            rect(d,(x-1,y-1,x+ew,y+eh),'#efc1a1')
            rect(d,(x,y,x+ew-1,y+eh-1),'#fffef6')
            rect(d,(x,y,x+ew-1,y),'#7c432c')
            px=x+max(2,ew//4)
            rect(d,(px,y+2,x+ew-2,y+eh-1),'#20150f')
            rect(d,(px,y+eh-5,x+ew-2,y+eh-1),'#78420f')
            rect(d,(px+1,y+eh-3,x+ew-3,y+eh-1),'#b27516')
            rect(d,(px+1,y+2,px+2,y+3),'#ffffff')
            rect(d,(x+ew-3,y+5,x+ew-3,y+5),'#fff6dc')
            rect(d,(x-1,y-4,x+ew,y-3),'#78422c')
        # Nose has geometry; a U-shaped smile is drawn below it.
        cy=round(h*.78); cx=w//2
        rect(d,(cx-5,cy,cx+4,cy),'#5d3325')
        rect(d,(cx-6,cy-1,cx-6,cy-1),'#5d3325')
        rect(d,(cx+5,cy-1,cx+5,cy-1),'#5d3325')
        rect(d,(2,round(h*.66),4,round(h*.69)),'#fac5a7')
        rect(d,(w-5,round(h*.66),w-3,round(h*.69)),'#fac5a7')
    if name=='lantern_body' and face in ('north','south','east','west'):
        rect(d,(1,1,w-2,2),'#c67b27')
        rect(d,(1,h-3,w-2,h-2),'#d18d31')
        cx=w//2; cy=h//2
        ring=[(-2,-3),(0,-3),(2,-1),(2,1),(0,3),(-2,1),(-2,-1)]
        for x,y in ring: rect(d,(cx+x-1,cy+y-1,cx+x,cy+y),'#ffcf4c')
        rect(d,(cx-1,cy-1,cx,cy),'#f6b72f')
        rect(d,(0,3,1,h-4),'#592818')
        rect(d,(w-2,3,w-1,h-4),'#592818')
    return im

def cube(name, pos, size, mat, bone, rotation=None, origin=None, face_density=None):
    x,y,z=pos; w,h,d=size
    c=dict(name=name,uuid=uid('cube/'+name),type='cube',box_uv=False,autouv=0,
           from_=[x,y,z],to=[x+w,y+h,z+d],origin=origin or groups[[g['name'] for g in groups].index(bone)]['origin'],
           rotation=rotation or [0,0,0],inflate=0,visibility=True,export=True,faces={})
    c['from']=c.pop('from_')
    sizes={'north':(w,h),'south':(w,h),'east':(d,h),'west':(d,h),'up':(w,d),'down':(w,d)}
    for face,(a,b) in sizes.items():
        density=4 if mat in ('face','ear') and face=='north' else (face_density or 2)
        fw=max(1,math.ceil(a*density)); fh=max(1,math.ceil(b*density))
        fx,fy=pack(fw,fh)
        tile=face_art(fw,fh,mat,name,face)
        atlas.paste(tile,(fx,fy))
        # Pad island with edge colors so mipmaps cannot read transparent gutters.
        atlas.paste(tile.crop((0,0,fw,1)),(fx,fy-1))
        atlas.paste(tile.crop((0,fh-1,fw,fh)),(fx,fy+fh))
        atlas.paste(tile.crop((0,0,1,fh)),(fx-1,fy))
        atlas.paste(tile.crop((fw-1,0,fw,fh)),(fx+fw,fy))
        c['faces'][face]=dict(uv=[fx,fy,fx+fw,fy+fh],texture=0)
        uv_records.append(dict(cube=name,face=face,rect=[fx,fy,fw,fh],material=mat))
    elements.append(c); nodes[bone]['children'].append(c['uuid'])
    return c

def segment(name,a,b,width,depth,mat,bone):
    dx,dy,dz=[b[i]-a[i] for i in range(3)]; length=math.sqrt(dx*dx+dy*dy+dz*dz)
    # A local +Y cuboid points from a to b; use Rz * Rx as Blockbench Euler.
    az=-math.degrees(math.atan2(dx,dy))
    rx=math.degrees(math.atan2(dz,math.hypot(dx,dy)))
    return cube(name,[a[0]-width/2,a[1]-.13,a[2]-depth/2],[width,length+.26,depth],mat,bone,[rx,0,az],a)

group('root',[0,0,0]); group('body',[0,5,1],'root'); group('neck',[0,14,0],'body')
group('head',[0,15,0],'neck'); group('crown',[0,25,0],'head')
group('ear_left',[5.9,21,0],'head'); group('ear_right',[-5.9,21,0],'head')
for sign,s in ((-1,'right'),(1,'left')):
    group('upper_arm_'+s,[sign*3.1,14,0],'body')
    group('forearm_'+s,[sign*4.8,8.4,-1],'upper_arm_'+s)
    group('hand_'+s,[sign*5.8,2 if sign<0 else 8,-3.2],'forearm_'+s)
    group('thigh_'+s,[sign*2.2,5.3,2],'body')
    group('shin_'+s,[sign*3.7,3,1.3],'thigh_'+s)
    group('foot_'+s,[sign*3.8,1,-.2],'shin_'+s)
group('tail_base',[0,4.6,3.2],'body')
group('tail_curl',[-8.4,5.6,5.8],'tail_base')
group('tail_tip',[-7.0,10,5.8],'tail_curl')
group('lantern',[5.6,7.4,-4.1],'hand_left')

# Upright slim torso with tapering cream chest.
cube('hips',[-2.8,2.8,-.5],[5.6,4.4,5.7],'coat','body')
cube('torso',[-2.75,5.5,-1.5],[5.5,8.6,4.9],'coat','body')
cube('shoulders',[-3.3,11.6,-1.35],[6.6,2.6,4.6],'coat','body')
cube('neck_core',[-1.8,13.4,-1.2],[3.6,2.6,3.4],'white','neck')
for i,(y,w,h,z) in enumerate([(11.4,4.5,2.8,-1.75),(9.2,3.9,2.2,-1.77),(7.1,3.3,2.1,-1.73),(5.3,2.7,1.8,-1.68),(3.6,2.0,1.7,-1.55)]):
    cube('cream_bib_'+str(i),[-w/2,y,z],[w,h,.45],'bib' if i<3 else 'skin','body')

# Asymmetric arms: right supports the seated body; left bends to grip the lantern.
segment('upper_arm_right',[-3.5,13.7,0],[-4.8,8.4,-1],2.5,2.7,'coat','upper_arm_right')
segment('forearm_right',[-4.8,8.4,-1],[-6,2,-3.1],2.6,2.8,'coat','forearm_right')
cube('palm_right',[-7.55,.7,-4.75],[3.3,1.7,3.6],'white','hand_right')
for i in range(3):
    cube('finger_right_'+str(i),[-7.35+i*1.06,.1,-5.15],[.9,1.3,1.1],'white','hand_right')
cube('thumb_right',[-4.45,.7,-3.8],[.8,1.4,1.8],'white','hand_right')
segment('upper_arm_left',[3.5,13.7,0],[4.8,8.7,-.6],2.5,2.7,'coat','upper_arm_left')
segment('forearm_left',[4.8,8.7,-.6],[5.7,8.4,-3.7],2.6,2.4,'coat','forearm_left')
cube('grip_palm_left',[4.2,7.8,-4.4],[3.1,1.6,2.4],'white','hand_left')
for i in range(3):
    cube('grip_finger_left_'+str(i),[4.3+i*.98,7.1,-4.95],[.85,1.4,1.15],'white','hand_left')
cube('grip_thumb_left',[3.9,7.7,-3.9],[.9,1.3,1.6],'white','hand_left')

# Short bent haunches and flat three-toed feet.
for sign,s in ((-1,'right'),(1,'left')):
    x=sign*3.5
    segment('haunch_'+s,[sign*2.5,5.5,2.2],[sign*3.9,3.5,-.3],3.5,3.6,'coat','thigh_'+s)
    segment('shin_'+s,[sign*3.9,3.5,-.3],[sign*3.8,1.2,.1],2.8,2.9,'coat','shin_'+s)
    cube('foot_pad_'+s,[x-1.8,.15,-1.55],[3.6,1.4,3.8],'white','foot_'+s)
    for i in range(3): cube('toe_'+s+'_'+str(i),[x-1.65+i*1.12,0,-2.05],[.98,1.15,1.25],'white','foot_'+s)

# Head shell: stepped lower jaw and rounded cuboid silhouette.
cube('head_core',[-5.7,15.8,-3.65],[11.4,9.1,8.7],'coat','head')
cube('head_lower',[-4.9,14.5,-3.55],[9.8,2.3,7.8],'white','head')
cube('back_cap',[-4.9,16.5,4.5],[9.8,7.9,1.1],'coat','head')
cube('face',[-4.5,15.1,-4.35],[9,8.5,1.15],'face','head')
cube('soft_chin',[-3.45,14.6,-4.05],[6.9,.65,.8],'skin','head')
cube('nose',[-.66,18.2,-4.9],[1.32,.7,.7],'nose','head')
cube('nose_tip',[-.34,18.02,-5.03],[.68,.28,.35],'dark','head')

for sign,s in ((-1,'right'),(1,'left')):
    cube('ear_outer_'+s,[5.7 if sign>0 else -8.9,18.0,-1.9],[3.2,5.4,2.15],'ear','ear_'+s)
    # Three silhouette-changing cheek locks, no dense voxel noise.
    for i,(y,w,h,z) in enumerate([(14.8,1.5,2,-4.15),(16.5,1.3,2.1,-4.25),(23.0,1.5,1.7,-3.9)]):
        cube('cheek_lock_'+s+'_'+str(i),[4.5 if sign>0 else -4.5-w,y,z],[w,h,1.65], 'gold' if i==0 else 'coat','head')
    cube('temple_'+s,[5.1 if sign>0 else -6.3,23.5,-2.8],[1.2,2,5.6],'coat','head')

# Stepped swept hair, large white clusters and occasional solid amber locks.
cube('crown_lower',[-5.45,24.0,-3.45],[10.9,1.7,8.1],'coat','crown')
cube('crown_mid',[-4.5,25.5,-2.6],[9,1.5,6.8],'white','crown')
cube('crown_upper',[-3.0,26.7,-1.6],[6,1.35,5.2],'coat','crown')
crest=[(-2.6,27.9,.3,2.2,1.4,2.7,'white'),(-1.0,28.8,.6,1.6,1.35,2,'gold'),
       (.35,27.8,-.9,2.2,1.3,2.4,'white'),(2.45,26.8,-1.2,1.55,1.3,2.2,'gold'),
       (-3.75,26.5,-2.45,1.65,1.5,2.6,'gold'),(-1.6,25.7,-3.1,2.1,1.5,1.6,'white'),
       (.4,24.95,-3.9,1.5,1.2,1.4,'white'),(2,24.65,-3.7,2,1.35,1.5,'white')]
for i,(x,y,z,w,h,d,mat) in enumerate(crest): cube('swept_tuft_'+str(i),[x,y,z],[w,h,d],mat,'crown')
locks=[(-5.7,24.9,-1.3,1.5,1.15,2.5,'white'),(-4.7,26.0,.8,1.8,1.1,2.1,'white'),
       (-3.2,27.0,2.6,2,1.05,1.5,'white'),(-1.2,26.9,3.15,2,1.5,1.4,'white'),
       (1.1,26.1,3.6,2.25,1.35,1.35,'gold'),(3.45,25.1,2.5,1.8,1.1,2,'white'),
       (4.5,24.6,.3,1.5,1.1,2.2,'white'),(-4.9,24.0,-4.0,2.1,1.1,1.0,'white'),
       (-3.3,25.05,-3.7,1.8,1.4,1.2,'white'),(1.0,26.5,-2.3,1.6,1.5,1.35,'white')]
for i,(x,y,z,w,h,d,mat) in enumerate(locks): cube('crown_edge_lock_'+str(i),[x,y,z],[w,h,d],mat,'crown')
for i,(x,y,z,w,h,d) in enumerate([(-4.8,23.4,5.05,3,1.6,.85),(-2.5,21.3,5.13,4.4,1.8,.75),(1.8,19.3,4.95,3.1,1.8,.85),(-3.8,17.4,4.6,3.6,1.6,.9)]):
    cube('rear_fur_step_'+str(i),[x,y,z],[w,h,d],'coat','head')

# Connected square-section spiral, thinning towards the inner curl.
path=[[0,4.6,3.2],[-2.6,4.1,4.7],[-5.6,4.45,5.8],[-8.4,5.6,5.8],
      [-10.3,7.7,5.8],[-11.0,10.3,5.8],[-10.5,12.4,5.8],[-8.8,13.6,5.8],
      [-6.8,13.4,5.8],[-5.8,11.7,5.8],[-6.25,10.0,5.8],[-7.6,9.4,5.8],[-8.4,10.2,5.8],[-8.3,11.0,5.8]]
for i in range(len(path)-1):
    width=1.4 if i<8 else 1.25 if i<11 else .95
    segment('tail_segment_'+str(i),path[i],path[i+1],width,width,'gold' if i%3==1 else 'coat', 'tail_base' if i<3 else 'tail_curl' if i<10 else 'tail_tip')

# Lantern: open handle, stepped rounded body, cap and gold patterned panels.
cube('lantern_handle_top',[4.3,6.9,-4.36],[2.6,.45,.48],'dark','lantern')
for x in (4.3,6.4): cube('lantern_handle_side_'+str(x),[x,5.9,-4.36],[.48,1.25,.48],'dark','lantern')
cube('lantern_neck',[4.65,5.55,-4.75],[1.9,.6,1.9],'gold','lantern')
cube('lantern_lid',[3.85,5.2,-5.45],[3.5,.5,3.3],'dark','lantern')
cube('lantern_top_band',[3.9,4.7,-5.5],[3.4,.6,3.4],'gold','lantern')
cube('lantern_body',[3.4,1.45,-5.85],[4.4,3.3,4.1],'brown','lantern',face_density=3)
cube('lantern_belly',[3.05,2.1,-5.5],[5.1,2.0,3.4],'brown','lantern')
cube('lantern_bottom_band',[3.85,.95,-5.4],[3.5,.6,3.2],'gold','lantern')
cube('lantern_foot',[4.15,.45,-5.1],[2.9,.55,2.65],'dark','lantern')

# Match the supplied front view: lamp on the viewer's right, spiral tail on left.
for c in elements:
    c['from'][0],c['to'][0]=-c['to'][0],-c['from'][0]
    c['origin']=list(c['origin']); c['origin'][0]=-c['origin'][0]
    c['rotation'][1]*=-1; c['rotation'][2]*=-1
for g in groups:
    g['origin']=list(g['origin']); g['origin'][0]=-g['origin'][0]
    g['rotation'][1]*=-1; g['rotation'][2]*=-1

png=OUT/'white_gold_monkey.png'; atlas.save(png)
tex=dict(name=png.name,uuid=uid('texture'),id='0',path=png.as_posix(),relative_path=png.name,
         width=SIZE,height=SIZE,uv_width=SIZE,uv_height=SIZE,render_mode='default',visible=True,
         source='data:image/png;base64,'+base64.b64encode(png.read_bytes()).decode(),saved=True)
model=dict(meta=dict(format_version='5.0',model_format='bedrock',box_uv=False),
           name='白金卷尾灵猴 · 多视图建模',model_identifier='white_gold_monkey',
           resolution=dict(width=SIZE,height=SIZE),visible_box=[4,4,1.5],
           elements=elements,groups=groups,outliner=roots,textures=[tex],animations=[],
           ai_used=True,ai_agents='codex',bedrock_animation_mode='entity')
(OUT/'white_gold_monkey.bbmodel').write_text(json.dumps(model,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'uv_layout.json').write_text(json.dumps(uv_records,indent=2),encoding='utf-8')
print(json.dumps(dict(cubes=len(elements),bones=len(groups),atlas=[SIZE,SIZE],uv_islands=len(uv_records),
                      atlas_used_height=cursor_y+row_h,height=30.15,files=[png.name,'white_gold_monkey.bbmodel'])))
