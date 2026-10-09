(() => {
Timeline.pause();const a=Animation.all.find(a=>a.name==="animation.xingxing.stand_observe"),g=Object.fromEntries(Group.all.map(v=>[v.name,v]));
const projectFile=Project.save_path||Project.export_path;
if(!projectFile)throw new Error("Save the Blockbench project before running this script");
const outputPath=name=>require("path").join(require("path").dirname(projectFile),name);
Blockbench.writeFile(outputPath("xingxing_before_stand_arm_fix.bbmodel"),{content:Codecs.project.compile()});
const otherBefore=Object.fromEntries(Animation.all.filter(v=>v!==a).map(v=>[v.name,JSON.stringify(AnimationCodec.codecs.bedrock.compileAnimation(v))]));
Undo.initEdit({animations:[a]});
const V=x=>new THREE.Vector3(...x),rad=Math.PI/180,deg=180/Math.PI,sm=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x)},qEuler=v=>new THREE.Quaternion().setFromEuler(new THREE.Euler(...v.map(x=>x*rad),"ZYX")),toEuler=q=>new THREE.Euler().setFromQuaternion(q,"ZYX").toArray().slice(0,3).map(x=>Math.round(x*deg*100000)/100000);
const vals=k=>["x","y","z"].map(n=>Number(k.get(n))),body=a.animators[g.body.uuid];
for(const side of ["left","right"]){
const s=side==="left"?1:-1,S=V(g["arm_"+side].origin),E=V(g["forearm_"+side].origin),W=V(g["hand_"+side].origin),A=E.clone().sub(S).normalize(),B=W.clone().sub(E).normalize();
const upperWorld=new THREE.Quaternion().setFromUnitVectors(A,V([s*0.08,-0.99,-0.10]).normalize());
const lowerWorld=new THREE.Quaternion().setFromUnitVectors(B,V([s*0.04,0.24,-0.97]).normalize());
for(const name of ["arm_"+side,"forearm_"+side,"hand_"+side])for(const k of a.animators[g[name].uuid].rotation){
const t=k.time,rise=sm((t-0.15)/1.05)*(1-sm((t-4.75)/1.05)),weight=sm((rise-0.25)/0.75),bodyKey=body.rotation.find(v=>Math.abs(v.time-t)<0.0001),qb=qEuler(vals(bodyKey));
const target=name.startsWith("arm_")?qb.clone().invert().multiply(upperWorld):name.startsWith("forearm_")?upperWorld.clone().invert().multiply(lowerWorld):new THREE.Quaternion();
const q=qEuler(vals(k)).slerp(target,weight),v=toEuler(q);k.extend({x:v[0],y:v[1],z:v[2]});
}
}
Undo.finishEdit("Correct stand observe arms: upper arms down and forearms fold upward",{animations:[a]});
a.select();Animation.all.forEach(v=>v.playing=v===a);Timeline.setTime(2.5);Animator.preview();
const changedOther=Animation.all.filter(v=>v!==a&&JSON.stringify(AnimationCodec.codecs.bedrock.compileAnimation(v))!==otherBefore[v.name]).map(v=>v.name);
const p=Preview.all.find(p=>p.id==="mcp_offscreen_stand_fix");p.setProjectionMode(false);p.camera.position.set(38,26,-55);p.controls.target.set(0,16,-1);p.controls.update();p.screenshot({crop:false,width:600,height:600},data=>Blockbench.writeFile(outputPath("stand_arm_fix_preview.png"),{savetype:"image",content:data}));
return {changed:a.name,otherChanged:changedOther};
})()
