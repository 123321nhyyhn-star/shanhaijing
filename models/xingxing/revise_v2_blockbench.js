(() => {
const tex=Texture.all[0],old=Cube.all.slice(),made=[],groups=Object.fromEntries(Group.all.map(g=>[g.name,g]));
Undo.initEdit({elements:old,outliner:true,textures:[tex],bitmap:true});
const sample=document.createElement("canvas");sample.width=tex.width;sample.height=tex.height;const sc=sample.getContext("2d");sc.drawImage(tex.img,0,0);
const colors={fur:"#ae3419",fur_light:"#cb4423",fur_hot:"#dc522d",fur_dark:"#7b230f",fur_mid:"#b93a1c",cream:"#fff0db",cream_shadow:"#e6c4a7",cream_light:"#fff7e6",skin:"#ffd0ac",skin_light:"#ffdaba",skin_shade:"#e9ac87",teal:"#368c94",teal_light:"#53a4a8",teal_dark:"#296872",white:"#fff6e6",black:"#211208",brow:"#743322",nose:"#81452c",nostril:"#35170e",lip:"#dba782",mouth:"#44211b"};
const originalColor=new Map();for(const c of old){const f=c.faces.north,u=f.uv;const x=Math.min(tex.width-1,Math.max(0,Math.floor((u[0]+u[2])/2))),y=Math.min(tex.height-1,Math.max(0,Math.floor((u[1]+u[3])/2)));const p=sc.getImageData(x,y,1,1).data;originalColor.set(c.uuid,"#"+Array.from(p.slice(0,3)).map(v=>v.toString(16).padStart(2,"0")).join(""));}
function add(n,from,to,col,group,rotation=[0,0,0],origin=[0,0,0]){const c=new Cube({name:n,from,to,rotation,origin,box_uv:false,autouv:0}).addTo(groups[group]).init();c._xingColor=colors[col]||col;made.push(c);return c;}
function b(n,x,y,z,w,h,d,col,g,rot,org){return add(n,[x,y,z],[x+w,y+h,z+d],col,g,rot,org)}
function shift(c,d){for(const prop of ["from","to","origin"])for(let i=0;i<3;i++)c[prop][i]+=d[i]}
const isDesc=(c,n)=>{let p=c.parent;while(p instanceof Group){if(p.name===n)return true;p=p.parent}return false};
const remove=old.filter(c=>isDesc(c,"arm_left")||isDesc(c,"arm_right")||isDesc(c,"leg_left")||isDesc(c,"leg_right")||c.parent?.name==="neck"||(c.parent?.name==="face"&&!["face_upper","face_cheeks"].includes(c.name)));
remove.forEach(c=>c.remove());
for(const c of Cube.all){if(isDesc(c,"head"))shift(c,[0,-1.8,-3]);else if(c.parent?.name==="body"){for(const p of ["from","to","origin"]){c[p][0]*=1.17;c[p][1]+=1;c[p][2]+=4.5}c.origin=[0,6,5.5];c.rotation=[-32,0,0];}else if(isDesc(c,"tail_base"))shift(c,[0,1,4.5]);}
for(const g of Group.all){if(["head","face","mane","ear_left","ear_right"].includes(g.name)){g.origin[1]-=1.8;g.origin[2]-=3;}if(g.name.startsWith("tail_")){g.origin[1]+=1;g.origin[2]+=4.5;}}
groups.body.origin=[0,6,5.5];groups.neck.origin=[0,13.2,-2.7];
for(const s of ["left","right"]){groups["arm_"+s].addTo(groups.root);groups["arm_"+s].rotation=[0,0,0];}
b("neck_support",-2.4,12.6,-4.1,4.8,3.3,4.0,"fur_dark","neck");
b("neck_front_white",-1.7,12.8,-4.35,3.4,2.4,0.5,"cream","neck");
const hp=[0,-1.8,-3];
function face(n,x,y,z,w,h,d,col){return b(n,x,y+hp[1],z+hp[2],w,h,d,col,"face")}
face("lower_face", -3.45,16.65,-5.75,6.9,3.1,1.15,"skin");
for(const s of [-1,1]){const nm=s===1?"left":"right",x=s===1?1.3:-4.3;
face("mc_eye_white_"+nm,x,21.0,-5.93,3,2,0.4,"white");
face("mc_eye_pupil_"+nm,s===1?1.8:-2.8,21.0,-6.04,1,2,0.28,"black");
face("mc_brow_block_"+nm,x-0.1,23.1,-6.03,3.1,0.65,0.65,"brow");
face("mc_brow_step_"+nm,s===1?1.15:-1.9,22.65,-6.05,0.75,0.7,0.65,"brow");
}
face("muzzle_upper_left",-2.45,18.4,-6.65,2.3,0.85,1.3,"skin_light");
face("muzzle_upper_right",0.15,18.4,-6.65,2.3,0.85,1.3,"skin_light");
face("upper_lip_volume",-1.7,18.05,-6.9,3.4,0.6,1.15,"lip");
face("mouth_cavity",-1.35,17.35,-6.4,2.7,0.8,0.85,"mouth");
face("lower_jaw_volume",-2.1,16.35,-6.55,4.2,1.03,1.2,"skin_shade");
face("lower_lip_volume",-1.6,17.05,-6.82,3.2,0.35,1.25,"lip");
face("muzzle_corner_left",-2.15,17.15,-6.65,0.9,1.25,1.1,"skin");
face("muzzle_corner_right",1.25,17.15,-6.65,0.9,1.25,1.1,"skin");
face("nose_bridge_volume",-0.55,19.5,-6.65,1.1,1.15,1.0,"skin_shade");
face("nose_tip_volume",-0.55,19.05,-7.3,1.1,0.95,1.45,"nose");
for(const s of [-1,1]){const nm=s===1?"left":"right",x=s===1?0.5:-1.2;
face("nose_wing_top_"+nm,x,19.6,-7.0,0.7,0.45,1.2,"nose");
face("nose_wing_outer_"+nm,s===1?1.0:-1.2,19.15,-7.0,0.2,0.65,1.2,"nose");
face("nose_wing_bottom_"+nm,x,19.05,-6.98,0.7,0.15,1.2,"nose");
face("nostril_recess_"+nm,s===1?0.55:-0.97,19.2,-6.79,0.42,0.38,0.35,"nostril");
}
function seg(n,p,q,w,d,col,g){
const v=p.map((x,i)=>x-q[i]),len=Math.hypot(...v),rot=[Math.atan2(v[2],v[1])*180/Math.PI,0,-Math.atan2(v[0],Math.hypot(v[1],v[2]))*180/Math.PI];
const c=b(n,q[0]-w/2,q[1],q[2]-d/2,w,len,d,col,g,rot,q);return {q,len,rot,w,d,g};
}
function sleeve(a,prefix){for(let r=0;r<a.len-0.6;r+=1.05){const k=Math.floor(r/1.05);const col=k%4===0?"fur_light":k%3===0?"fur_dark":"fur_mid";b(prefix+"_front_"+k,a.q[0]-a.w/2+0.1,a.q[1]+r,a.q[2]-a.d/2-0.28,a.w-0.2,1.18,0.5,col,a.g,a.rot,a.q);for(const s of [-1,1])b(prefix+"_side_"+s+"_"+k,a.q[0]+(s===1?a.w/2-0.15:-a.w/2-0.4),a.q[1]+r+0.1,a.q[2]-a.d/2+0.1,0.55,1.2,a.d-0.2,k%2?"fur":"fur_light",a.g,a.rot,a.q);if(k===2||k===4)b(prefix+"_teal_"+k,a.q[0]-a.w/2+0.4,a.q[1]+r+0.2,a.q[2]-a.d/2-0.34,0.8,0.72,0.18,k%2?"teal":"teal_light",a.g,a.rot,a.q);}}
for(const s of [-1,1]){
const nm=s===1?"left":"right",ag="arm_"+nm,hg="hand_"+nm,lg="leg_"+nm,fg="foot_"+nm;
const shoulder=[s*4.0,13.0,-0.25],elbow=[s*5.15,7.1,-4.75],wrist=[s*5.6,2.1,-9.8];
groups[ag].origin=shoulder;groups[hg].origin=wrist;groups[lg].origin=[s*2.1,6.5,5.5];groups[fg].origin=[s*2.7,1.25,5.4];
b("shoulder_round_"+nm,s*4-1.8,11.4,-2.4,3.6,3.4,4.1,"fur_mid",ag);
sleeve(seg("upper_arm_support_"+nm,shoulder,elbow,3.3,3.65,"fur",ag),"upper_coat_"+nm);
b("elbow_joint_"+nm,s*5.15-1.65,5.95,-6.25,3.3,2.6,3.1,"fur_dark",ag);
sleeve(seg("forearm_support_"+nm,elbow,wrist,3.25,3.3,"fur_mid",ag),"forearm_coat_"+nm);
b("wrist_cuff_"+nm,s*5.6-1.6,1.45,-11.2,3.2,1.8,2.8,"fur_light",hg);
b("palm_weight_"+nm,s*5.6-1.8,0.55,-11.75,3.6,1.7,3.8,"cream",hg);
b("hand_back_"+nm,s*5.6-1.65,2.1,-10.95,3.3,0.65,2.7,"cream_shadow",hg);
for(let i=0;i<4;i++){
const x=s*5.6-1.72+i*0.87;
b("ground_knuckle_"+nm+"_"+i,x,0,-12.85,0.76,1.6,1.65,i%2?"cream_light":"cream",hg);
b("curled_finger_"+nm+"_"+i,x,0.25,-12.15,0.76,1.7,1.25,"cream",hg);
}
b("thumb_"+nm,s*5.6+(s===1?-2.25:1.5),0.35,-10.75,0.85,1.2,1.5,"cream_shadow",hg);
const hip=[s*2.1,6.5,5.5],knee=[s*2.8,3.7,8.15],ankle=[s*2.75,1.2,5.45];
seg("bent_thigh_"+nm,hip,knee,2.85,3.0,"fur",lg);
b("knee_mass_"+nm,s*2.8-1.5,2.8,6.8,3.0,2.25,2.8,"fur_mid",lg);
seg("bent_shin_"+nm,knee,ankle,2.2,2.3,"fur_dark",lg);
b("hindfoot_"+nm,s*2.75-1.55,0,3.45,3.1,1.2,4.25,"cream_shadow",fg);
b("hindfoot_top_"+nm,s*2.75-1.45,1.05,4.45,2.9,0.55,3.0,"cream",fg);
for(let i=0;i<3;i++)b("hind_toe_"+nm+"_"+i,s*2.75-1.5+i*1.02,0,2.95,0.9,0.9,1.4,"cream",fg);
}
let seed=7901;const rnd=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296};
for(const c of Cube.all.slice().filter(c=>c.parent?.name==="mane"&&(/rear_mane|side_mane|forehead_fur|swept_crest/.test(c.name)))){
if(rnd()>0.52)continue;const w=c.to[0]-c.from[0],h=c.to[1]-c.from[1],d=c.to[2]-c.from[2],col=rnd()>0.5?"fur_light":"fur_hot";
if(c.name.startsWith("rear"))b("fine_fur_"+c.name,c.from[0]+w*0.2,c.from[1]+h*0.3,c.to[2]-0.12,Math.min(0.95,w*0.5),Math.min(1.1,h*0.6),0.45,col,"mane");
else if(c.name.startsWith("side")){const s=(c.from[0]+c.to[0])/2>0?1:-1;b("fine_fur_"+c.name,s===1?c.to[0]-0.1:c.from[0]-0.35,c.from[1]+0.3,c.from[2]+d*0.15,0.45,0.9,Math.min(0.95,d*0.5),col,"mane");}
else b("fine_fur_"+c.name,c.from[0]+0.3,c.from[1]+h*0.3,c.from[2]-0.3,Math.min(0.9,w*0.5),Math.min(0.9,h*0.5),0.45,col,"mane");
}
const defs=[];for(const c of Cube.all){const size=c.to.map((v,i)=>v-c.from[i]);for(const [name,f] of Object.entries(c.faces)){const ax=name==="east"||name==="west"?[2,1]:name==="up"||name==="down"?[0,2]:[0,1];defs.push({c,f,name,w:Math.max(2,Math.ceil(size[ax[0]]*3)),h:Math.max(2,Math.ceil(size[ax[1]]*3))});}}
let N=512,layout;for(;;){let x=1,y=1,row=0,ok=true;layout=[];for(const d of defs){if(x+d.w+2>N){x=1;y+=row+2;row=0}if(y+d.h+2>N){ok=false;break}layout.push([x,y]);x+=d.w+2;row=Math.max(row,d.h)}if(ok)break;N*=2;}
const atlas=document.createElement("canvas");atlas.width=N;atlas.height=N;const ctx=atlas.getContext("2d");ctx.fillStyle="#722410";ctx.fillRect(0,0,N,N);
function tint(hex,k){const rgb=hex.match(/\w\w/g).map(v=>parseInt(v,16));return "#"+rgb.map(v=>Math.max(0,Math.min(255,Math.round(v*k))).toString(16).padStart(2,"0")).join("")}
defs.forEach((d,i)=>{const [x,y]=layout[i];let col=d.c._xingColor||originalColor.get(d.c.uuid)||colors.fur;const fur=(!/face|ear|hand|foot/.test(d.c.parent?.name||""))||/fur|coat|mane|crest|sideburn/.test(d.c.name);if(fur&&col.toLowerCase().startsWith("#a"))col=colors.fur;
ctx.fillStyle=col;ctx.fillRect(x-1,y-1,d.w+2,d.h+2);
if(fur){for(let py=1;py<d.h-1;py+=2)for(let px=1;px<d.w-1;px+=2){if(rnd()<0.32){ctx.fillStyle=tint(col,0.87+rnd()*0.25);ctx.fillRect(x+px,y+py,Math.min(2,d.w-px),Math.min(2,d.h-py));}}ctx.fillStyle=tint(col,1.10);ctx.fillRect(x,y,d.w,1);ctx.fillStyle=tint(col,0.87);ctx.fillRect(x,y+d.h-1,d.w,1);}
else if(!/mc_eye|nostril|cavity/.test(d.c.name)){ctx.fillStyle=tint(col,1.035);ctx.fillRect(x,y,d.w,Math.min(2,d.h));ctx.fillStyle=tint(col,0.97);ctx.fillRect(x,y+d.h-1,d.w,1);}
d.f.texture=tex.uuid;d.f.uv=[x,y,x+d.w,y+d.h];});
Project.texture_width=N;Project.texture_height=N;tex.uv_width=N;tex.uv_height=N;tex.name="xingxing_v2.png";tex.fromDataURL(atlas.toDataURL("image/png"));delete tex._xingColor;Cube.all.forEach(c=>delete c._xingColor);Canvas.updateAll();unselectAll();
Undo.finishEdit("Rebuild gorilla ground support, Minecraft eyes, volumetric muzzle and fur atlas",{elements:Cube.all.slice(),outliner:true,textures:[tex],bitmap:true});
const p=Preview.selected;p.setProjectionMode(false);p.camera.position.set(46,31,-73);p.controls.target.set(0,13,-1);p.controls.update();
return {cubes:Cube.all.length,bones:Group.all.length,atlas:N,removed:remove.length,added:made.length};
})()
