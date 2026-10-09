(() => {
Timeline.pause();const a=Animation.all.find(v=>v.name==="animation.xingxing.stand_observe"),groups=Object.fromEntries(Group.all.map(v=>[v.name,v]));
Undo.initEdit({animations:[a]});const V=a=>new THREE.Vector3(...a),C=V(groups.body.origin),targets={},created=[],clamps=[];
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

const vals=k=>["x","y","z"].map(n=>Number(k.get(n))),qEuler=v=>new THREE.Quaternion().setFromEuler(new THREE.Euler(...v.map(x=>x*rad),"ZYX"));
const body=a.animators[groups.body.uuid],root=a.animators[groups.root.uuid];
for(const side of ["left","right"]){const s=side==="left"?1:-1,S=V(groups["arm_"+side].origin),E=V(groups["forearm_"+side].origin),W=V(groups["hand_"+side].origin),A=E.clone().sub(S).normalize(),B=W.clone().sub(E).normalize();
const upperDir=V([s*0.06,-0.984,-0.168]).normalize(),lowerDir=V([s*0.06,-0.8,-0.6]).normalize(),upperGoal=new THREE.Quaternion().setFromUnitVectors(A,upperDir),lowerGoal=new THREE.Quaternion().setFromUnitVectors(B,lowerDir),handGoal=new THREE.Quaternion().setFromUnitVectors(V([0,0,-1]),lowerDir);
for(let i=0;i<=120;i++){const t=i/20,rise=sm((t-0.15)/1.05)*(1-sm((t-4.75)/1.05)),wu=sm((rise-0.65)/0.35),wf=sm((rise-0.4)/0.45),wh=wu;
const bk=body.rotation.find(v=>Math.abs(v.time-t)<0.0001),rk=root.position.find(v=>Math.abs(v.time-t)<0.0001),qb=qEuler(vals(bk)),h=groups["hand_"+side].origin;
const baseline=ik("arm",side,[h[0],mix(h[1],4.5,rise),mix(h[2],1.7,rise)],V(vals(rk)),qb,"relaxed@"+t);
const oldUpper=qb.clone().multiply(qEuler(baseline["arm_"+side])),oldLower=oldUpper.clone().multiply(qEuler(baseline["forearm_"+side]));
const uw=oldUpper.slerp(upperGoal,wu),fw=oldLower.slerp(lowerGoal,wf),hw=new THREE.Quaternion().slerp(handGoal,wh);
const qs={[ "arm_"+side]:qb.clone().invert().multiply(uw),["forearm_"+side]:uw.clone().invert().multiply(fw),["hand_"+side]:fw.clone().invert().multiply(hw)};
for(const [name,q] of Object.entries(qs)){const k=a.animators[groups[name].uuid].rotation.find(v=>Math.abs(v.time-t)<0.0001),v=euler(q);k.extend({x:v[0],y:v[1],z:v[2]});}
}}
Undo.finishEdit("Natural downward arms with staged release from ground support",{animations:[a]});a.select();Animation.all.forEach(v=>v.playing=v===a);
let minHand=999,minFoot=999,upperMax=-999,lowerMax=-999;
for(let i=0;i<=360;i++){const t=i/60;Timeline.setTime(t);Animator.preview();Project.model_3d.updateMatrixWorld(true);for(const side of ["left","right"]){const p=["arm_","forearm_","hand_"].map(n=>groups[n+side].mesh.getWorldPosition(new THREE.Vector3()));if(t>=1.2&&t<=4.75){upperMax=Math.max(upperMax,p[1].y-p[0].y);lowerMax=Math.max(lowerMax,p[2].y-p[1].y);}minHand=Math.min(minHand,new THREE.Box3().setFromObject(Cube.all.find(c=>c.parent===groups["hand_"+side]).mesh).min.y);minFoot=Math.min(minFoot,new THREE.Box3().setFromObject(Cube.all.find(c=>c.parent===groups["foot_"+side]).mesh).min.y);}}
const matrices=t=>{Timeline.setTime(t);Animator.preview();Project.model_3d.updateMatrixWorld(true);return Group.all.map(v=>v.mesh.matrixWorld.elements.slice())};const first=matrices(0),last=matrices(6);let seam=0;first.forEach((m,j)=>m.forEach((v,k)=>seam=Math.max(seam,Math.abs(v-last[j][k]))));
globalThis._standRelaxedQA={minHand,minFoot,upperMax,lowerMax,seam};return globalThis._standRelaxedQA;
})()
