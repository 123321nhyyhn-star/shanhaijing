(() => {
Timeline.pause();const a=Animation.all.find(v=>v.name==="animation.xingxing.stand_observe"),gs=Object.fromEntries(Group.all.map(g=>[g.name,g])),head=a.animators[gs.head.uuid],body=a.animators[gs.body.uuid];
const before=AnimationCodec.codecs.bedrock.compileAnimation(a),oldRest=JSON.stringify(Object.fromEntries(Object.entries(before.bones).filter(([n])=>n!=="head")));
Undo.initEdit({animations:[a]});
const knots=[[0,0],[1.35,0],[1.65,55],[2.4,55],[2.85,-55],[4.1,-55],[4.65,0],[6,0]],rad=Math.PI/180,expected=[],sm=t=>t*t*(3-2*t);
for(const k of head.rotation){
const t=k.time;let yaw=0;
for(let i=0;i<knots.length-1;i++){const l=knots[i],r=knots[i+1];if(t>=l[0]&&t<=r[0]){yaw=l[1]+(r[1]-l[1])*sm((t-l[0])/(r[0]-l[0]));break;}}
const b=body.rotation.find(v=>Math.abs(v.time-t)<.000001),br=["x","y","z"].map(n=>Number(b.get(n))*rad);
const qbody=new THREE.Quaternion().setFromEuler(new THREE.Euler(...br,"ZYX")),qhead=qbody.invert().multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),yaw*rad));
const e=new THREE.Euler().setFromQuaternion(qhead,"ZYX"),v=e.toArray().slice(0,3).map(n=>Math.round(n/rad*100000)/100000);
k.extend({x:v[0],y:v[1],z:v[2]});expected.push({time:t,yaw});
}
Undo.finishEdit("Faster left and right look with a pause between",{animations:[a]});
globalThis._observeFastLookTargets=expected;
a.select();Animation.all.forEach(v=>v.playing=v===a);Timeline.setTime(0);Animator.preview();
const after=AnimationCodec.codecs.bedrock.compileAnimation(a),newRest=JSON.stringify(Object.fromEntries(Object.entries(after.bones).filter(([n])=>n!=="head")));
return {leftTurnSeconds:.3,leftHoldSeconds:.75,rightTurnSeconds:.45,restOfObserveUnchanged:oldRest===newRest,otherChanged:Animation.all.filter(v=>v!==a&&JSON.stringify(AnimationCodec.codecs.bedrock.compileAnimation(v))!==globalThis._observeOtherHashes[v.name]).map(v=>v.name)};
})()
