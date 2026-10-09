(() => {
const tex=Texture.all[0],old=Cube.all.slice(),before=old.length,groups=Object.fromEntries(Group.all.map(g=>[g.name,g]));
Undo.initEdit({elements:old,outliner:true,textures:[tex],bitmap:true});
const keep=new Set(["torso","shoulder_mass","hips","neck_support","head_core","jaw_mass","face_upper","face_cheeks","lower_face","mc_eye_white_left","mc_eye_white_right","mc_brow_block_left","mc_brow_block_right","nose_tip_volume","mouth_cavity","lower_jaw_volume","ear_rim_left","ear_rim_right","upper_arm_support_left","upper_arm_support_right","forearm_support_left","forearm_support_right","bent_thigh_left","bent_thigh_right","bent_shin_left","bent_shin_right","hindfoot_left","hindfoot_right"]);
old.filter(c=>!keep.has(c.name)).forEach(c=>c.remove());
function add(n,from,to,g,rotation=[0,0,0],origin=[0,0,0]){return new Cube({name:n,from,to,rotation,origin,box_uv:false,autouv:0}).addTo(groups[g]).init();}
add("simple_crown",[-5.8,24.75,-5.8],[5.8,26.55,2.8],"mane");
add("simple_crest_left",[-4.8,26.55,-2.8],[-1.5,28.0,0.8],"mane");
add("simple_crest_right",[-1.5,26.55,-1.8],[2.5,27.35,1.8],"mane");
add("simple_sideburn_left",[4.6,13.9,-8.15],[6.8,23.5,-6.25],"mane");
add("simple_sideburn_right",[-6.8,13.9,-8.15],[-4.6,23.5,-6.25],"mane");
add("simple_rear_coat",[-6.5,15.0,1.55],[6.5,25.4,3.05],"mane");
add("simple_upper_muzzle",[-2.25,16.4,-9.8],[2.25,17.45,-8.35],"face");
for(const s of [-1,1])add("simple_ground_hand_"+(s===1?"left":"right"),[s*5.6-1.8,0,-12.85],[s*5.6+1.8,2.55,-7.95],"hand_"+(s===1?"left":"right"));
const nose=Cube.all.find(c=>c.name==="nose_tip_volume");nose.from[0]=-0.85;nose.to[0]=0.85;
for(const c of Cube.all.filter(c=>c.name.startsWith("forearm_support"))){c.from[1]-=0.15;c.to[1]+=0.15;}
for(const c of Cube.all.filter(c=>c.name.startsWith("hindfoot"))){c.from[2]=2.95;c.to[1]=1.55;}
const tail=[[0,6.3,7.6],[3.5,5.35,9.3],[6.8,6.8,9.3],[8.5,9.3,9.3],[8.3,12.3,9.3],[5.8,13.1,9.3],[4.2,11.6,9.3],[4.7,10.1,9.3],[6.3,10.4,9.3]];
for(let i=0;i<tail.length-1;i++){const p=tail[i+1],q=tail[i],d=p.map((v,k)=>v-q[k]),len=Math.hypot(...d),rot=[Math.atan2(d[2],Math.hypot(d[0],d[1]))*180/Math.PI,0,-Math.atan2(d[0],d[1])*180/Math.PI],w=i<6?1.4:1.2;add("simple_tail_"+i,[q[0]-w/2,q[1]-0.1,q[2]-w/2],[q[0]+w/2,q[1]+len+0.1,q[2]+w/2],i<2?"tail_base":i<6?"tail_curl":"tail_tip",rot,q);}
const defs=[];for(const c of Cube.all){const s=c.to.map((v,i)=>v-c.from[i]);for(const [name,f] of Object.entries(c.faces)){const ax=name==="east"||name==="west"?[2,1]:name==="up"||name==="down"?[0,2]:[0,1];defs.push({c,f,name,w:Math.max(2,Math.ceil(s[ax[0]]*2)),h:Math.max(2,Math.ceil(s[ax[1]]*2))});}}
defs.sort((a,b)=>b.h-a.h||b.w-a.w);let N=128,layout;for(;;){let x=1,y=1,row=0,ok=true;layout=[];for(const d of defs){if(x+d.w+2>N){x=1;y+=row+2;row=0}if(y+d.h+2>N){ok=false;break}layout.push([x,y]);x+=d.w+2;row=Math.max(row,d.h)}if(ok)break;N*=2;}
const atlas=document.createElement("canvas");atlas.width=N;atlas.height=N;const ctx=atlas.getContext("2d");ctx.fillStyle="#893019";ctx.fillRect(0,0,N,N);
let seed=124;const rnd=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296};
const fur=["#ae3b20","#b84122","#c34a29","#a23319","#9a3019"];
defs.forEach((d,i)=>{
const [x,y]=layout[i],n=d.c.name,gn=d.c.parent?.name||"";let col="#b44022",kind="fur";
if(gn==="face"){kind="skin";col="#ffd2b1";if(n.includes("eye")){kind="eye";col="#fff6e9";}if(n.includes("brow")){kind="solid";col="#78311d";}if(n.includes("nose")){kind="nose";col="#77442c";}if(n.includes("cavity")){kind="solid";col="#49261c";}if(n.includes("jaw"))col="#edbb96";}
if(gn.startsWith("ear")){kind="ear";col="#fff0db";}
if(gn.startsWith("hand")||gn.startsWith("foot")){kind="hand";col="#ffedd6";}
ctx.fillStyle=col;ctx.fillRect(x-1,y-1,d.w+2,d.h+2);
if(kind==="fur"){for(let py=0;py<d.h;py+=3)for(let px=0;px<d.w;px+=3){ctx.fillStyle=fur[Math.floor(rnd()*fur.length)];ctx.fillRect(x+px,y+py,Math.min(3,d.w-px),Math.min(3,d.h-py));}
ctx.fillStyle="#c4502f";ctx.fillRect(x,y,d.w,1);ctx.fillStyle="#983018";ctx.fillRect(x,y+d.h-1,d.w,1);
if(n==="torso"&&d.name==="north"){for(let py=0;py<Math.floor(d.h*0.87);py++){const t=py/d.h,half=Math.max(1,Math.round(d.w*(0.34-0.2*t)));ctx.fillStyle=py%4===0?"#edcfb3":"#fff0dc";ctx.fillRect(x+Math.floor(d.w/2)-half,y+py,2*half,1);}}
if(n==="neck_support"&&d.name==="north"){ctx.fillStyle="#fff0dc";ctx.fillRect(x+Math.floor(d.w*0.25),y,Math.ceil(d.w*0.5),d.h);}
if((n.includes("arm_support")&&["north","east","west"].includes(d.name))||(n==="simple_rear_coat"&&d.name==="south")||(n==="simple_crown"&&d.name==="north")){
ctx.fillStyle="#3c9198";ctx.fillRect(x+Math.floor(d.w*0.24),y+Math.floor(d.h*0.25),Math.max(1,Math.ceil(d.w*0.28)),Math.max(1,Math.ceil(d.h*0.12)));
ctx.fillStyle="#55a3a7";ctx.fillRect(x+Math.floor(d.w*0.5),y+Math.floor(d.h*0.65),Math.max(1,Math.ceil(d.w*0.24)),Math.max(1,Math.ceil(d.h*0.13)));
}}
if(kind==="eye"&&d.name==="north"){ctx.fillStyle="#21140b";const px=n.endsWith("left")?1:3;ctx.fillRect(x+px,y,2,d.h);}
if(kind==="ear"&&d.name==="north"){ctx.fillStyle="#f0bca0";ctx.fillRect(x+Math.floor(d.w*0.3),y+Math.floor(d.h*0.18),Math.max(1,Math.floor(d.w*0.48)),Math.max(1,Math.floor(d.h*0.64)));}
if(kind==="hand"&&d.name==="north"){ctx.fillStyle="#d7b495";for(let k=1;k<4;k++)ctx.fillRect(x+Math.floor(d.w*k/4),y+Math.floor(d.h*0.35),1,d.h-Math.floor(d.h*0.35));}
d.f.texture=tex.uuid;d.f.uv=[x,y,x+d.w,y+d.h];});
Project.texture_width=N;Project.texture_height=N;tex.uv_width=N;tex.uv_height=N;tex.name="xingxing_simple.png";tex.fromDataURL(atlas.toDataURL("image/png"));
Canvas.updateAll();unselectAll();Undo.finishEdit("Simplify Xingxing into main cuboids and painted fur",{elements:Cube.all.slice(),outliner:true,textures:[tex],bitmap:true});
const p=Preview.selected;p.setProjectionMode(false);p.camera.position.set(46,31,-73);p.controls.target.set(0,13,-1);p.controls.update();
return {before,after:Cube.all.length,reduction:Math.round((1-Cube.all.length/before)*100)+"%",texture:N};
})()
