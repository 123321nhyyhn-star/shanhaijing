(() => {
Timeline.pause();Animator.showDefaultPose();
const groups=Object.fromEntries(Group.all.map(g=>[g.name,g])),oldAnims=Animation.all.slice();
Undo.initEdit({elements:Cube.all.slice(),outliner:true,animations:oldAnims});
for(const c of Cube.all){for(let ax=0;ax<3;ax++)if(c.from[ax]>c.to[ax]){const t=c.from[ax];c.from[ax]=c.to[ax];c.to[ax]=t;const faces=ax===0?["east","west"]:ax===1?["up","down"]:["north","south"];const ua=c.faces[faces[0]].uv.slice(),ub=c.faces[faces[1]].uv.slice();c.faces[faces[0]].uv=ub;c.faces[faces[1]].uv=ua;}}
for(const side of ["left","right"]){const s=side==="left"?1:-1;groups["arm_"+side].addTo(groups.body);
const fore=new Group({name:"forearm_"+side,origin:[s*5.15,7.1,-4.75]}).addTo(groups["arm_"+side]).init();groups[fore.name]=fore;
Cube.all.find(c=>c.name==="forearm_support_"+side).addTo(fore);groups["hand_"+side].addTo(fore);
const shin=new Group({name:"shin_"+side,origin:[s*2.8,3.7,8.15]}).addTo(groups["leg_"+side]).init();groups[shin.name]=shin;
Cube.all.find(c=>c.name==="bent_shin_"+side).addTo(shin);groups["foot_"+side].addTo(shin);
}
Canvas.updateAll();Animator.showDefaultPose();
const V=a=>new THREE.Vector3(...a),C=V(groups.body.origin),targets={},created=[],clamps=[];
const D=180/Math.PI,rad=Math.PI/180,rx=v=>new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1,0,0),v*rad);
const euler=q=>new THREE.Euler().setFromQuaternion(q,"ZYX").toArray().slice(0,3).map(v=>Math.round(v*D*100000)/100000);
const round=v=>Math.round(v*100000)/100000;
const mix=(a,b,t)=>a+(b-a)*t,sm=t=>{t=Math.max(0,Math.min(1,t));return t*t*(3-2*t)};
function ik(kind,side,target,rootPos,bodyQ,label){
const upper=groups[(kind==="arm"?"arm_":"leg_")+side],middle=groups[(kind==="arm"?"forearm_":"shin_")+side],end=groups[(kind==="arm"?"hand_":"foot_")+side];
const parentQ=kind==="arm"?bodyQ:new THREE.Quaternion(),pivot=kind==="arm"?C:V([0,0,0]);
const sr=V(upper.origin),er=V(middle.origin),wr=V(end.origin),A=er.clone().sub(sr),B=wr.clone().sub(er),L1=A.length(),L2=B.length();
const S=sr.clone().sub(pivot).applyQuaternion(parentQ).add(pivot).add(rootPos),T=V(target),delta=T.clone().sub(S),distance=delta.length(),d=Math.min(L1+L2-0.001,Math.max(Math.abs(L1-L2)+0.001,distance));
if(Math.abs(d-distance)>0.03)clamps.push({label,kind,side,error:round(distance-d)});
const dir=delta.normalize(),a=(L1*L1-L2*L2+d*d)/(2*d),h=Math.sqrt(Math.max(0,L1*L1-a*a));
let hint=A.clone().applyQuaternion(parentQ);hint.addScaledVector(dir,-hint.dot(dir));if(hint.length()<0.001)hint=V([side==="left"?0.2:-0.2,0,1]).addScaledVector(dir,-dir.z);
hint.normalize();const E=S.clone().addScaledVector(dir,a).addScaledVector(hint,h);
const invParent=parentQ.clone().invert(),u=E.clone().sub(S).applyQuaternion(invParent).normalize(),q1=new THREE.Quaternion().setFromUnitVectors(A.clone().normalize(),u);
const v=T.clone().sub(E).applyQuaternion(invParent).applyQuaternion(q1.clone().invert()).normalize(),q2=new THREE.Quaternion().setFromUnitVectors(B.clone().normalize(),v);
const q3=parentQ.clone().multiply(q1).multiply(q2).invert();
return {[upper.name]:euler(q1),[middle.name]:euler(q2),[end.name]:euler(q3)};
}
function gait(phase,stride,lift,base){
phase=((phase%1)+1)%1;const stance=0.64;
if(phase<stance)return [base[0],base[1],base[2]-stride+2*stride*phase/stance];
const u=(phase-stance)/(1-stance);return [base[0],base[1]+lift*Math.sin(Math.PI*u),base[2]+stride*Math.cos(Math.PI*u)];
}
function create(name,len,steps,sample){
const tracks={},expected=[];function key(b,ch,time,v){tracks[b]||={name:b,keyframes:[]};tracks[b].keyframes.push({channel:ch,time:round(time),interpolation:"linear",data_points:[{x:round(v[0]),y:round(v[1]),z:round(v[2])}]});}
for(let i=0;i<=steps;i++){const t=len*i/steps,pose=sample(t,i/steps),rp=V(pose.root),bq=rx(pose.body);
key("root","position",t,pose.root);key("body","rotation",t,[pose.body,0,pose.roll||0]);key("head","rotation",t,[-pose.body+(pose.pitch||0),pose.yaw||0,0]);
for(const side of ["left","right"])for(const kind of ["arm","leg"]){const limb=(kind==="arm"?"hand_":"foot_")+side,T=pose.contacts[limb],angles=ik(kind,side,T,rp,bq,name+"@"+round(t));for(const [b,v] of Object.entries(angles))key(b,"rotation",t,v);}
key("tail_base","rotation",t,[pose.tailPitch||0,pose.tailYaw||0,0]);key("tail_curl","rotation",t,[0,0,pose.tailCurl||0]);
expected.push({time:round(t),contacts:pose.contacts});
}
const animators={};for(const [n,tr] of Object.entries(tracks))animators[groups[n].uuid]=tr;
const a=new Animation({name,loop:"loop",length:len,snapping:40,animators}).add(false);created.push(a);targets[a.name]=expected;return a;
}
function walk(fast){return (t,u)=>{
const phase=u,omega=2*Math.PI*u,rp=[0,(fast?-0.95:-0.78)+(fast?0.22:0.12)*Math.cos(2*omega),0],contacts={};
for(const side of ["left","right"]){const offset=side==="left"?0:0.5;contacts["hand_"+side]=gait(phase+offset,fast?1.0:0.72,fast?1.7:1.1,groups["hand_"+side].origin);contacts["foot_"+side]=gait(phase+offset+0.5,fast?1.25:0.85,fast?1.0:0.7,groups["foot_"+side].origin);}
return {root:rp,body:fast?-4:0,pitch:fast?2:-1,yaw:1.5*Math.sin(omega),contacts,tailYaw:(fast?6:3)*Math.sin(omega+0.6),tailPitch:2*Math.cos(2*omega),tailCurl:(fast?5:2)*Math.sin(omega)};
};}
create("animation.xingxing.crawl",1.6,32,walk(false));
create("animation.xingxing.crawl_fast",0.8,32,walk(true));
create("animation.xingxing.stand_observe",6,120,(t,u)=>{
const rise=sm((t-0.15)/1.05)*(1-sm((t-4.75)/1.05)),contacts={};
for(const side of ["left","right"]){const h=groups["hand_"+side].origin,f=groups["foot_"+side].origin;contacts["hand_"+side]=[h[0],mix(h[1],4.5,rise),mix(h[2],1.7,rise)];contacts["foot_"+side]=[f[0],f[1],mix(f[2],6.2,rise)];}
let yaw=0,pitch=0;
const knots=[[0,0,0],[1.2,0,0],[1.9,26,-2],[2.5,0,2],[3.2,-26,-1],[3.85,0,-9],[4.45,0,3],[4.8,0,0],[6,0,0]];
for(let i=0;i<knots.length-1;i++)if(t>=knots[i][0]&&t<=knots[i+1][0]){const k=sm((t-knots[i][0])/(knots[i+1][0]-knots[i][0]));yaw=mix(knots[i][1],knots[i+1][1],k);pitch=mix(knots[i][2],knots[i+1][2],k);break;}
return {root:[0,2*rise,0],body:32*rise,pitch,yaw,contacts,tailYaw:4*rise*Math.sin(t*1.5),tailCurl:3*rise*Math.sin(t*1.8)};
});
Undo.finishEdit("Rig elbow and knee joints and add crawl, stand observe and fast crawl",{elements:Cube.all.slice(),outliner:true,animations:Animation.all.slice()});
globalThis._xingxingAnimationTargets=targets;
Animation.all.forEach(a=>a.playing=false);created[0].select();created[0].playing=true;Timeline.setTime(0);Animator.preview();
return {animations:created.map(a=>({name:a.name,length:a.length,keyframes:Object.values(a.animators).reduce((s,b)=>s+b.keyframes.length,0)})),bones:Group.all.length,cubes:Cube.all.length,clamps:clamps.slice(0,15),clampCount:clamps.length};
})()
