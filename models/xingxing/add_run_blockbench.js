(() => {
Timeline.pause();const groups=Object.fromEntries(Group.all.map(g=>[g.name,g])),old=Animation.all.slice(),oldHashes=Object.fromEntries(old.map(a=>[a.name,JSON.stringify(AnimationCodec.codecs.bedrock.compileAnimation(a))]));
Undo.initEdit({animations:old});
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

const name="animation.xingxing.run",length=0.64,steps=32,tracks={},expected=[];
function key(b,ch,t,v){tracks[b]||={name:b,keyframes:[]};tracks[b].keyframes.push({channel:ch,time:round(t),interpolation:"linear",data_points:[{x:round(v[0]),y:round(v[1]),z:round(v[2])}]});}
function step(phase,stride,lift,base,stance){phase=((phase%1)+1)%1;if(phase<stance)return [base[0],base[1],base[2]-stride+2*stride*phase/stance];const u=(phase-stance)/(1-stance);return [base[0],base[1]+lift*Math.sin(Math.PI*u),base[2]+stride*Math.cos(Math.PI*u)];}
for(let i=0;i<=steps;i++){const u=i/steps,t=u*length,phase=u===1?0:u,w=2*Math.PI*phase,root=[0,-0.9+0.5*Math.cos(2*Math.PI*(phase-0.72)),0],body=-8+2*Math.sin(w),qb=rx(body),contacts={};
key("root","position",t,root);key("body","rotation",t,[body,0,0]);key("head","rotation",t,[-body+2+1.2*Math.sin(w-0.3),0,0]);
for(const side of ["left","right"]){contacts["hand_"+side]=step(phase,1.9,2.35,groups["hand_"+side].origin,0.44);contacts["foot_"+side]=step(phase+(side==="left"?0.12:0.62),2.0,1.45,groups["foot_"+side].origin,0.42);
for(const kind of ["arm","leg"]){const angles=ik(kind,side,contacts[(kind==="arm"?"hand_":"foot_")+side],V(root),qb,name+"@"+t);for(const [b,v] of Object.entries(angles))key(b,"rotation",t,v);}}
key("tail_base","rotation",t,[5*Math.cos(w+0.5),7*Math.sin(w+0.8),0]);key("tail_curl","rotation",t,[0,0,6*Math.sin(w+0.4)]);expected.push({time:round(t),contacts});
}
const animators={};for(const [b,tr] of Object.entries(tracks))animators[groups[b].uuid]=tr;
const a=new Animation({name,loop:"loop",length,snapping:50,animators}).add(false);
Undo.finishEdit("Add run: synchronous arms and alternating hind legs",{animations:Animation.all.slice()});
globalThis._xingxingRunTargets=expected;
a.select();Animation.all.forEach(v=>v.playing=v===a);Timeline.setTime(0.22);Animator.preview();
return {name:a.name,length:a.length,keyframes:Object.values(a.animators).reduce((s,b)=>s+b.keyframes.length,0),clamps,otherChanged:old.filter(v=>JSON.stringify(AnimationCodec.codecs.bedrock.compileAnimation(v))!==oldHashes[v.name]).map(v=>v.name)};
})()
