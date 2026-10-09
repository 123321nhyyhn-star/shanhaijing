(() => {
Timeline.pause();const a=Animation.all.find(v=>v.name==="animation.xingxing.stand_observe"),groups=Object.fromEntries(Group.all.map(g=>[g.name,g]));
Undo.initEdit({animations:[a]});
const V=a=>new THREE.Vector3(...a),C=V(groups.body.origin),targets={},created=[],clamps=[];
const D=180/Math.PI,rad=Math.PI/180,rx=v=>new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1,0,0),v*rad);
const euler=q=>new THREE.Euler().setFromQuaternion(q,"ZYX").toArray().slice(0,3).map(v=>Math.round(v*D*100000)/100000);
const round=v=>Math.round(v*100000)/100000;
const mix=(a,b,t)=>a+(b-a)*t,sm=t=>{t=Math.max(0,Math.min(1,t));return t*t*(3-2*t)};
function ik(kind,side,target,rootPos,bodyQ,label,seat=0){
const upper=groups[(kind==="arm"?"arm_":"leg_")+side],middle=groups[(kind==="arm"?"forearm_":"shin_")+side],end=groups[(kind==="arm"?"hand_":"foot_")+side];
const parentQ=kind==="arm"?bodyQ:new THREE.Quaternion(),pivot=kind==="arm"?C:V([0,0,0]);
const sr=V(upper.origin),er=V(middle.origin),wr=V(end.origin),A=er.clone().sub(sr),B=wr.clone().sub(er),L1=A.length(),L2=B.length();
const S=sr.clone().sub(pivot).applyQuaternion(parentQ).add(pivot).add(rootPos),T=V(target),delta=T.clone().sub(S),distance=delta.length(),d=Math.min(L1+L2-0.001,Math.max(Math.abs(L1-L2)+0.001,distance));
if(Math.abs(d-distance)>0.03)clamps.push({label,kind,side,error:round(distance-d)});
const dir=delta.normalize(),a=(L1*L1-L2*L2+d*d)/(2*d),h=Math.sqrt(Math.max(0,L1*L1-a*a));
let hint=A.clone().applyQuaternion(parentQ);if(kind==="leg")hint=V([side==="left"?0.6:-0.6,2,-3]);hint.addScaledVector(dir,-hint.dot(dir));if(hint.length()<0.001)hint=V([side==="left"?0.2:-0.2,0,1]).addScaledVector(dir,-dir.z);
hint.normalize();const E=S.clone().addScaledVector(dir,a).addScaledVector(hint,h);
const invParent=parentQ.clone().invert(),u=E.clone().sub(S).applyQuaternion(invParent).normalize(),q1=new THREE.Quaternion().setFromUnitVectors(A.clone().normalize(),u);
const v=T.clone().sub(E).applyQuaternion(invParent).applyQuaternion(q1.clone().invert()).normalize(),q2=new THREE.Quaternion().setFromUnitVectors(B.clone().normalize(),v);
const q3=parentQ.clone().multiply(q1).multiply(q2).invert();
return {[upper.name]:euler(q1),[middle.name]:euler(q2),[end.name]:euler(q3)};
}

const ry=v=>new THREE.Quaternion().setFromAxisAngle(V([0,1,0]),v*rad);
const tracks={},expected=[];
function key(b,ch,t,v){tracks[b]||={name:b,keyframes:[]};tracks[b].keyframes.push({channel:ch,time:round(t),interpolation:"linear",data_points:[{x:round(v[0]),y:round(v[1]),z:round(v[2])}]});}
const knots=[[0,0],[1.35,0],[2.2,55],[2.55,55],[3.8,-55],[4.1,-55],[4.65,0],[6,0]];
for(let i=0;i<=480;i++){
const t=i/80,rise=sm(t/0.6)*(1-sm((t-4.65)/1.05)),seat=1-rise,root=[0,mix(-2.95,2,rise),0],body=mix(40,32,rise),qb=rx(body),contacts={};
let yaw=0;for(let j=0;j<knots.length-1;j++)if(t>=knots[j][0]&&t<=knots[j+1][0]){yaw=mix(knots[j][1],knots[j+1][1],sm((t-knots[j][0])/(knots[j+1][0]-knots[j][0])));break;}
key("root","position",t,root);key("body","rotation",t,[body,0,0]);
key("head","rotation",t,euler(qb.clone().invert().multiply(ry(yaw))));
for(const side of ["left","right"]){
const s=side==="left"?1:-1;
contacts["foot_"+side]=[mix(s*3.4,s*2.7,rise),1.25,mix(-0.2,6.2,rise)];
for(const [name,v]of Object.entries(ik("leg",side,contacts["foot_"+side],V(root),qb,"observe@"+t,seat)))key(name,"rotation",t,v);
const baseline=ik("arm",side,[s*5.8,mix(2.1,4.5,rise)+2.8*rise*seat,mix(1,1.7,rise)],V(root),qb,"arm@"+t);
const S=V(groups["arm_"+side].origin),E=V(groups["forearm_"+side].origin),W=V(groups["hand_"+side].origin),A=E.clone().sub(S).normalize(),B=W.clone().sub(E).normalize();
const uq=new THREE.Quaternion().setFromUnitVectors(A,V([s*0.06,-0.984,-0.168]).normalize()),fq=new THREE.Quaternion().setFromUnitVectors(B,V([s*0.06,-0.8,-0.6]).normalize()),hq=new THREE.Quaternion().setFromUnitVectors(V([0,0,-1]),V([s*0.06,-0.8,-0.6]).normalize());
const fromE=v=>new THREE.Quaternion().setFromEuler(new THREE.Euler(...v.map(x=>x*rad),"ZYX"));
const oldU=qb.clone().multiply(fromE(baseline["arm_"+side])),oldF=oldU.clone().multiply(fromE(baseline["forearm_"+side]));
const uw=oldU.slerp(uq,sm((rise-.65)/.35)),fw=oldF.slerp(fq,sm((rise-.4)/.45)),hw=new THREE.Quaternion().slerp(hq,sm((rise-.65)/.35));
for(const[name,q]of Object.entries({["arm_"+side]:qb.clone().invert().multiply(uw),["forearm_"+side]:uw.clone().invert().multiply(fw),["hand_"+side]:fw.clone().invert().multiply(hw)}))key(name,"rotation",t,euler(q));
}
key("tail_base","rotation",t,[-80*seat,4*rise*Math.sin(t*1.5),0]);key("tail_curl","rotation",t,[0,0,3*rise*Math.sin(t*1.8)]);
expected.push({time:round(t),rise,yaw,contacts});
}
const animators={};for(const[name,tr]of Object.entries(tracks))animators[groups[name].uuid]=tr;
a.extend({length:6,loop:"loop",snapping:80,animators});a.select();Animation.all.forEach(v=>v.playing=v===a);
let maxGroundCorrection=0;
for(const f of expected){Timeline.setTime(f.time);Animator.preview();Project.model_3d.updateMatrixWorld(true);
const minY=Math.min(...Cube.all.map(c=>new THREE.Box3().setFromObject(c.mesh).min.y));
const lift=Math.max(0,-minY)+.015*Math.min(1,10*f.rise,10*(1-f.rise));
if(lift>1e-7){const k=a.animators[groups.root.uuid].position.find(k=>Math.abs(k.time-f.time)<1e-6);k.extend({y:round(Number(k.get("y"))+lift)});for(const p of Object.values(f.contacts))p[1]+=lift;maxGroundCorrection=Math.max(maxGroundCorrection,lift);}
}
Undo.finishEdit("Quick rise, pause, wide head look, then sit",{animations:[a]});
globalThis._observeSequenceTargets=expected;
a.select();Animation.all.forEach(v=>v.playing=v===a);Timeline.setTime(0);Animator.preview();
return {maxGroundCorrection,clamps:clamps.slice(0,8),clampCount:clamps.length,keyframes:Object.values(a.animators).reduce((n,b)=>n+b.keyframes.length,0),otherChanged:Animation.all.filter(v=>v!==a&&JSON.stringify(AnimationCodec.codecs.bedrock.compileAnimation(v))!==globalThis._observeOtherHashes[v.name]).map(v=>v.name)};
})()
