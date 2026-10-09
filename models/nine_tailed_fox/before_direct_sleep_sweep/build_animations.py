"""Author editable Blockbench animation keys; geometry and texture are untouched."""
import json, math
from pathlib import Path
import numpy as np

OUT=Path(__file__).resolve().parent
MODEL=json.loads((OUT/'before_animations/nine_tailed_fox.bbmodel').read_text(encoding='utf-8'))
GROUPS={g['name']:g for g in MODEL['groups']}
BYID={g['uuid']:g['name'] for g in MODEL['groups']}
PARENTS={}
CUBE_PARENT={}
def scan(items,parent=None):
    for node in items:
        if isinstance(node,str): CUBE_PARENT[node]=parent
        else:
            name=BYID[node['uuid']];PARENTS[name]=parent;scan(node.get('children',[]),name)
scan(MODEL['outliner'])
TAU=math.tau
TIPS=[1,2,3,7,8,9]
LEGS=['leg_front_left','leg_front_right','leg_hind_left','leg_hind_right']
def sin(x):return math.sin(x)
def cos(x):return math.cos(x)
def smooth(x):
    x=max(0,min(1,x));return x*x*(3-2*x)
def pose():return {}
def setv(p,bone,channel,values):p.setdefault(bone,{})[channel]=list(values)
def rot(p,bone,values):setv(p,bone,'rotation',values)
def pos(p,bone,values):setv(p,bone,'position',values)
def scale(p,bone,values):setv(p,bone,'scale',values)
def absolute(p,bone,values):rot(p,bone,[v-d for v,d in zip(values,GROUPS[bone]['rotation'])])
def matrix(position,rotation):
    x,y,z=np.radians(rotation);cx,sx,cy,sy,cz,sz=cos(x),sin(x),cos(y),sin(y),cos(z),sin(z)
    rx=np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])
    ry=np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])
    rz=np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]])
    m=np.eye(4);m[:3,:3]=rz@ry@rx;m[:3,3]=position;return m
def bounds(p,filter_name=None):
    worlds={}
    for name,g in GROUPS.items():
        parent=PARENTS[name];parent_origin=GROUPS[parent]['origin'] if parent else [0,0,0]
        local=np.array(g['origin'])-parent_origin+np.array(p.get(name,{}).get('position',[0,0,0]))
        r=np.array(g['rotation'])+np.array(p.get(name,{}).get('rotation',[0,0,0]))
        local_matrix=matrix(local,r)
        local_matrix[:3,:3]=local_matrix[:3,:3]@np.diag(p.get(name,{}).get('scale',[1,1,1]))
        worlds[name]=(worlds[parent] if parent else np.eye(4))@local_matrix
    result=[]
    for c in MODEL['elements']:
        if filter_name and not filter_name(c['name']):continue
        bone=CUBE_PARENT[c['uuid']];origin=np.array(GROUPS[bone]['origin'])
        corners=np.array([[x,y,z,1] for x in [c['from'][0],c['to'][0]] for y in [c['from'][1],c['to'][1]] for z in [c['from'][2],c['to'][2]]],float)
        corners[:,:3]-=origin
        result.extend((worlds[bone]@corners.T).T[:,:3])
    return np.array(result)
def floor(p,clearance=.045):
    lowest=float(bounds(p)[:,1].min())
    pos(p,'root',[0,max(0,clearance-lowest),0]);return p

def tail_low(t):
    p=pose();phase=TAU*t/8
    for i in range(1,10):
        b=f'tail_{i:02}';a=(i-5)*12.0;off=i*2.39996
        pitch=(32 if i in TIPS else 21)+1.0*sin(phase+(off*.7))
        yaw=a+3.0*sin(phase+off)+.9*sin(2*phase-off)
        absolute(p,b,[pitch,yaw,.65*sin(phase-off)])
        if i in TIPS:absolute(p,b+'_tip',[-24+1.4*sin(phase+off-.5),1.2*sin(phase+off-.75),0])
    rot(p,'neck',[.7*sin(phase+.5),.8*sin(phase),0]);rot(p,'head',[-.5*sin(phase+.5),.8*sin(phase+.5),0])
    return floor(p)

def idle(t):
    p=pose();q=TAU*t/16
    common=10*sin(2*q)+3*sin(5*q+.4)
    for i in range(1,10):
        b=f'tail_{i:02}';phase=i*2.39996;freq=[2,3,4,3,2,5,4,3,2][i-1]
        x=7*sin(freq*q+phase)+3*sin((freq+3)*q-.6*phase)
        y=common+8*sin((freq+1)*q+phase)+3*sin((freq+5)*q+.7*phase)
        z=3*sin((freq+2)*q+.5*phase)
        rot(p,b,[x,y,z])
        if i in TIPS:rot(p,b+'_tip',[5*sin(freq*q+phase-.65),6*sin((freq+1)*q+phase-.55),1.5*sin((freq+2)*q+phase)])
    rot(p,'body',[.5*sin(2*q),.6*sin(q),.3*sin(q+.7)])
    rot(p,'neck',[1.4*sin(2*q+.8),2.8*sin(q+.9),0]);rot(p,'head',[-1*sin(2*q+.8),2.5*sin(3*q+1.2),.8*sin(q)])
    rot(p,'ear_left',[1.5*sin(5*q+.5),1.3*sin(3*q),0]);rot(p,'ear_right',[1.2*sin(4*q+.8),-1.2*sin(5*q+.6),0])
    return floor(p)

def walk(t):
    p=pose();q=TAU*t/1.2
    phase={'leg_front_left':0,'leg_hind_right':0,'leg_front_right':math.pi,'leg_hind_left':math.pi}
    pitch=1.5*sin(2*q)
    rot(p,'body',[pitch,.9*sin(q),.7*sin(q)])
    for b,ph in phase.items():
        angle=27*cos(q+ph)
        rot(p,b,[angle,0,0]);pos(p,b,[0,.55*max(0,sin(q+ph)),0])
    rot(p,'neck',[-.7*sin(2*q),.5*sin(q+.4),0]);rot(p,'head',[-pitch+.7*sin(2*q),-.5*sin(q+.4),-.4*sin(q)])
    for i in range(1,10):
        b=f'tail_{i:02}';base=GROUPS[b]['rotation']
        absolute(p,b,[base[0]*.72+2.5*sin(q+i*.6),base[1]+4*sin(q+i*.45),1.2*sin(q+i*.3)])
        if i in TIPS:rot(p,b+'_tip',[2*sin(q+i*.6-.6),3*sin(q+i*.45-.6),0])
    return floor(p)

def run(t):
    p=pose();q=TAU*t/.65
    body_pitch=-5+6*sin(q+.4)
    rot(p,'body',[body_pitch,1.3*sin(q),1.5*sin(q+.6)])
    pos(p,'body',[0,.18+.7*max(0,sin(q-.6)),0])
    for side,off in [('left',-.07),('right',.07)]:
        for front,amp,ph in [('front',42,0),('hind',48,2.25)]:
            b=f'leg_{front}_{side}';angle=amp*cos(q+ph+off)
            rot(p,b,[angle,0,0]);pos(p,b,[0,.55*max(0,sin(q+ph+off)),0])
    rot(p,'neck',[3-2*sin(q+.4),0,0]);rot(p,'head',[-body_pitch-3+2*sin(q+.4),0,-.5*sin(q+.6)])
    rot(p,'ear_left',[12+2*sin(q),0,0]);rot(p,'ear_right',[12+2*sin(q+.2),0,0])
    tail_q=TAU*t/2.6
    amplitudes=[12,23,17,29,19,32,22,14,27]
    elevations=[-40,-48,-43,-56,-53,-50,-45,-55,-41]
    frequencies=[1,2,1,3,2,1,3,2,1]
    for i in range(1,10):
        b=f'tail_{i:02}';phase=i*2.39996;freq=frequencies[i-1]
        x=elevations[i-1]+(6+i%4)*sin(freq*tail_q+phase)+2*sin(q+i*.4)
        y=(i-5)*10.5+amplitudes[i-1]*sin(freq*tail_q+phase)+4*sin((freq+2)*tail_q-.6*phase)
        z=(2+i%3)*sin((freq+1)*tail_q+.5*phase)
        absolute(p,b,[x,y,z])
        if i in TIPS:absolute(p,b+'_tip',[-8+7*sin(freq*tail_q+phase-.55),9*sin((freq+1)*tail_q+phase-.7),2*sin(freq*tail_q+phase)])
    return floor(p)

def sleeping_pose():
    p=pose();pos(p,'body',[0,-4,0])
    for b in LEGS:
        side=1 if b.endswith('left') else -1
        rot(p,b,[90,0,0 if 'front' in b else side*5])
        if 'front' in b:pos(p,b,[-side*1.4,0,0])
    pos(p,'neck',[-.5,-.6,.5]);rot(p,'neck',[-4,24,0])
    pos(p,'head',[0,-1.0,.5]);rot(p,'head',[-10,36,-32])
    rot(p,'ear_left',[-75,0,-8]);rot(p,'ear_right',[-75,0,8]);pos(p,'ear_left',[0,-1,0]);pos(p,'ear_right',[0,-1,0])
    yaw=[-165,-162,-159,-174,-169,-164,-147,-144,-141]
    for i in range(1,10):
        b=f'tail_{i:02}';side=-1 if i<5 else 1
        if i in TIPS:
            absolute(p,b,[6,yaw[i-1],0]);pos(p,b,[side*1.8-.8,-1.5,-1.5])
            absolute(p,b+'_tip',[-8,side*(-8),0])
        else:
            absolute(p,b,[4,yaw[i-1],0]);pos(p,b,[-.5,-1.5,-1.5])
    return p

SLEEP=sleeping_pose()
def sleep_down(t):
    p=pose();body_u=smooth((t-.25)/1.3);leg_u=smooth(t/1.45);head_u=smooth((t-4.8)/1.1)
    for b,channels in SLEEP.items():
        if b.startswith('tail_'):continue
        for ch,values in channels.items():
            if b=='body':u=body_u
            elif b in LEGS:u=leg_u
            elif b=='neck':u=smooth((t-4.65)/1.15)
            else:u=head_u
            setv(p,b,ch,[v*u for v in values])
    for i in range(1,10):
        b=f'tail_{i:02}';lower=smooth((t-.55-.025*(i-1))/1.4)
        sweep=smooth((t-2.35-.025*(i-1))/1.85)
        settle=smooth((t-4.2-.015*(i-1))/.85)
        base=GROUPS[b]['rotation'];lower_yaw=-65+2*(i-1)
        final_x=GROUPS[b]['rotation'][0]+SLEEP[b]['rotation'][0]
        final_y=GROUPS[b]['rotation'][1]+SLEEP[b]['rotation'][1]
        x=base[0]+(18-base[0])*lower
        hover_x=-8 if i in TIPS else 2
        x=x+(hover_x-18)*sweep+(final_x-hover_x)*settle
        y=base[1]+(lower_yaw-base[1])*lower+(final_y-lower_yaw)*sweep
        absolute(p,b,[x,y,0])
        mid_y=.8 if i in TIPS else 3.0
        tail_y=mid_y*body_u+(SLEEP[b]['position'][1]-mid_y)*settle
        pos(p,b,[SLEEP[b]['position'][0]*sweep,tail_y,SLEEP[b]['position'][2]*sweep])
        if i in TIPS:
            tip=b+'_tip';start=GROUPS[tip]['rotation'];final=[d+v for d,v in zip(start,SLEEP[tip]['rotation'])]
            absolute(p,tip,[start[0]+(-18-start[0])*lower+23*sweep+(final[0]-5)*settle,final[1]*settle,0])
    return floor(p)
def sleep_idle(t):
    p=json.loads(json.dumps(SLEEP));q=TAU*t/5
    p['body']['position'][1]+=.09*sin(q)
    p['head']['position'][1]+=.035*sin(q)
    for i in range(1,10):p[f'tail_{i:02}']['rotation'][0]+=.32*(sin(q+i*.3)-sin(i*.3))
    return floor(p)

def sitting_pose():
    p=pose();rot(p,'body',[30,0,0]);pos(p,'body',[0,-1.8,0])
    for b in LEGS:
        if 'front' in b:
            rot(p,b,[-30,0,0]);scale(p,b,[1,1.15,1])
        else:rot(p,b,[60,0,0])
    rot(p,'neck',[-18,0,0]);rot(p,'head',[-12,0,0])
    for i in range(1,10):
        b=f'tail_{i:02}';yaw=math.radians((i-5)*12);pitch=math.radians(6)
        world=np.array([sin(yaw)*cos(pitch),-sin(pitch),cos(yaw)*cos(pitch)])
        local=matrix([0,0,0],[-30,0,0])[:3,:3]@world
        absolute(p,b,[math.degrees(-math.asin(local[1])),math.degrees(math.atan2(local[0],local[2])),0])
        if i in TIPS:absolute(p,b+'_tip',[-4,0,0])
    return p

SIT=sitting_pose()

def sit_down(t):
    p=pose();body_u=smooth((t-.15)/1.65);tail_u=smooth((t-.25)/1.9)
    for b,channels in SIT.items():
        u=tail_u if b.startswith('tail_') else body_u
        if b.startswith('leg_hind'):u=smooth((t-.05)/1.5)
        for ch,values in channels.items():
            baseline=1 if ch=='scale' else 0
            setv(p,b,ch,[baseline+(v-baseline)*u for v in values])
    angle=math.radians(30*body_u)
    for b in ['leg_hind_left','leg_hind_right']:
        lowest=float(bounds(p,lambda name:name.startswith(b+'_'))[:,1].min())
        lift=max(0,.025-lowest)*smooth(t/.15)
        pos(p,b,[0,lift*cos(angle),-lift*sin(angle)])
    return floor(p)

def sit_idle(t):
    p=json.loads(json.dumps(SIT));q=TAU*t/6
    p['body']['position'][1]+=.06*sin(q)
    p['head']['rotation'][1]+=.9*sin(q)
    for i in range(1,10):
        b=f'tail_{i:02}';phase=i*2.39996
        p[b]['rotation'][0]+=.3*(sin(q+phase)-sin(phase))
        p[b]['rotation'][1]+=2*(sin(q+phase)-sin(phase))
        if i in TIPS:p[b+'_tip']['rotation'][1]+=1.1*(sin(q+phase-.4)-sin(phase-.4))
    return floor(p)

def animation(name,length,loop,step,fn):
    frames=int(round(length/step));step=length/frames
    animators={};stats=[]
    for k in range(frames+1):
        t=length if k==frames else k*step
        p=fn(0 if loop=='loop' and k==frames else t)
        stats.append({'time':round(t,5),'min_y':round(float(bounds(p)[:,1].min()),5),'root_y':p['root']['position'][1]})
        for b,channels in p.items():
            a=animators.setdefault(b,{'name':b,'type':'bone','keyframes':[]})
            for channel,values in channels.items():
                a['keyframes'].append({'channel':channel,'time':round(t,6),'interpolation':'linear','data_points':[dict(zip(['x','y','z'],[round(v,5) for v in values]))]})
    return {'name':'animation.nine_tailed_fox.'+name,'length':length,'loop':loop,'snapping':20,'animators':animators},stats

SPECS=[('tail_low',8,'loop',.125,tail_low),('idle',16,'loop',.125,idle),('walk',1.2,'loop',.05,walk),('run',2.6,'loop',.025,run),('sleep_down',6,'hold',.05,sleep_down),('sleep_idle',5,'loop',.125,sleep_idle),('sit_down',2.2,'hold',.05,sit_down),('sit_idle',6,'loop',.1,sit_idle)]
pack=[];audit={}
for name,length,loop,step,fn in SPECS:
    a,stats=animation(name,length,loop,step,fn);pack.append(a)
    audit[name]={'duration':length,'loop':loop,'bones':len(a['animators']),'keys':sum(len(b['keyframes']) for b in a['animators'].values()),'minimum_sample_y':min(s['min_y'] for s in stats),'maximum_floor_correction':round(max(s['root_y'] for s in stats),5),'final_root_y':round(stats[-1]['root_y'],5)}
(OUT/'animation-authoring.json').write_text(json.dumps({'animations':pack},indent=2),encoding='utf-8')
(OUT/'animation-authoring-audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
print(json.dumps(audit,indent=2))

