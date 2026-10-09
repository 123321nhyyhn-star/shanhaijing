(() => {
Timeline.pause();const a=Animation.all.find(v=>v.name==="animation.xingxing.stand_observe"),groups=Object.fromEntries(Group.all.map(v=>[v.name,v]));
const projectFile=Project.save_path||Project.export_path;
if(!projectFile)throw new Error("Save the Blockbench project before running this script");
const outputPath=name=>require("path").join(require("path").dirname(projectFile),name);
Blockbench.writeFile(outputPath("xingxing_before_relaxed_stand.bbmodel"),{content:Codecs.project.compile()});
const otherBefore=Object.fromEntries(Animation.all.filter(v=>v!==a).map(v=>[v.name,JSON.stringify(AnimationCodec.codecs.bedrock.compileAnimation(v))]));
Undo.initEdit({animations:[a]});
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

const vals=k=>["x","y","z"].map(n=>Number(k.get(n))),qEuler=v=>new THREE.Quaternion().setFromEuler(new THREE.Euler(...v.map(x=>x*rad),"ZYX"));
const body=a.animators[groups.body.uuid],root=a.animators[groups.root.uuid];
for(const side of ["left","right"]){const s=side==="left"?1:-1,S=V(groups["arm_"+side].origin),E=V(groups["forearm_"+side].origin),W=V(groups["hand_"+side].origin),A=E.clone().sub(S).normalize(),B=W.clone().sub(E).normalize();
const upperDir=V([s*0.06,-0.984,-0.168]).normalize(),lowerDir=V([s*0.06,-0.887,-0.458]).normalize();
const upperWorld=new THREE.Quaternion().setFromUnitVectors(A,upperDir),lowerWorld=new THREE.Quaternion().setFromUnitVectors(B,lowerDir),handWorld=new THREE.Quaternion().setFromUnitVectors(V([0,0,-1]),lowerDir);
for(const name of ["arm_"+side,"forearm_"+side,"hand_"+side])for(const k of a.animators[groups[name].uuid].rotation){
const t=k.time,rise=sm((t-0.15)/1.05)*(1-sm((t-4.75)/1.05)),weight=sm((rise-0.25)/0.75),bk=body.rotation.find(v=>Math.abs(v.time-t)<0.0001),rk=root.position.find(v=>Math.abs(v.time-t)<0.0001),qb=qEuler(vals(bk));
const h=groups["hand_"+side].origin,T=[h[0],mix(h[1],4.5,rise),mix(h[2],1.7,rise)],baseline=ik("arm",side,T,V(vals(rk)),qb,"relaxed@"+t)[name];
const target=name.startsWith("arm_")?qb.clone().invert().multiply(upperWorld):name.startsWith("forearm_")?upperWorld.clone().invert().multiply(lowerWorld):lowerWorld.clone().invert().multiply(handWorld);
const v=euler(qEuler(baseline).slerp(target,weight));k.extend({x:v[0],y:v[1],z:v[2]});
}}
Undo.finishEdit("Relax both arms downward in stand observe",{animations:[a]});a.select();Animation.all.forEach(v=>v.playing=v===a);Timeline.setTime(2.5);Animator.preview();
const p=Preview.all.find(v=>v.id==="mcp_offscreen_stand_relaxed");p.setProjectionMode(false);p.camera.position.set(38,26,-55);p.controls.target.set(0,16,-1);p.controls.update();p.screenshot({crop:false,width:600,height:600},data=>Blockbench.writeFile(outputPath("stand_relaxed_preview.png"),{savetype:"image",content:data}));
return {clip:a.name,otherChanged:Animation.all.filter(v=>v!==a&&JSON.stringify(AnimationCodec.codecs.bedrock.compileAnimation(v))!==otherBefore[v.name]).map(v=>v.name)};
})()
