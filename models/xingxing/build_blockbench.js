(() => {
const palette = [
["fur","#a33318"],["fur_light","#bf4121"],["fur_hot","#d24b28"],["fur_dark","#78230f"],["fur_shadow","#5e1a0d"],["fur_mid","#ad361b"],["fur_tip","#c74928"],
["cream","#fff0de"],["cream_shadow","#e9cbb2"],["cream_light","#fff8eb"],["skin","#ffd1b0"],["skin_light","#ffdbbd"],["skin_shade","#edb190"],["ear_inner","#f4baa0"],
["teal","#34848c"],["teal_light","#4a9ca0"],["teal_dark","#28656e"],["eye_white","#fffaf1"],["eye_black","#130b07"],["eye_brown","#3b1e0e"],["eye_glint","#ffffff"],["brow","#652313"],["nose","#4b2114"],["mouth","#36170c"],["toe_shadow","#aa7356"]
];
Undo.initEdit({elements:[],outliner:true,textures:[]});
Project.texture_width=128;Project.texture_height=128;Project.box_uv=false;Project.model_identifier="xingxing";Project.name="狌狌 · 赤毛白耳";
const canvas=document.createElement("canvas");canvas.width=128;canvas.height=128;const ctx=canvas.getContext("2d");ctx.fillStyle="#a33318";ctx.fillRect(0,0,128,128);
const slots={};
palette.forEach(([n,c],i)=>{const x=(i%8)*16,y=Math.floor(i/8)*16;slots[n]=[x+2,y+2,x+14,y+14];ctx.fillStyle=c;ctx.fillRect(x,y,16,16);if(n.startsWith("fur")||n.startsWith("cream")||n==="skin"){ctx.fillStyle="rgba(255,235,209,0.045)";ctx.fillRect(x+3,y+2,5,4);ctx.fillRect(x+10,y+10,4,4);ctx.fillStyle="rgba(42,8,0,0.045)";ctx.fillRect(x+1,y+11,5,3);}});
const tex=new Texture({name:"xingxing.png",width:128,height:128}).fromDataURL(canvas.toDataURL("image/png")).add(false);tex.select();
const groups={}, made=[];
const g=(name,origin,parent)=>{const a=new Group({name,origin});if(parent)a.addTo(groups[parent]);a.init();groups[name]=a;return a};
g("root",[0,0,0]);g("body",[0,9,1],"root");g("neck",[0,14.5,0],"body");g("head",[0,16,0],"neck");g("face",[0,21,-5.5],"head");g("mane",[0,23,1],"head");g("ear_left",[6,21,0],"head");g("ear_right",[-6,21,0],"head");
for(const side of [-1,1]){const s=side===1?"left":"right";g("arm_"+s,[side*3.5,13.3,0],"body");g("hand_"+s,[side*5,2.1,-0.6],"arm_"+s);g("leg_"+s,[side*1.8,5,1],"root");g("foot_"+s,[side*1.8,1,-0.8],"leg_"+s);}
g("tail_base",[0,5.5,3],"body");g("tail_curl",[6.1,6.1,4.7],"tail_base");g("tail_tip",[8.7,10.5,4.7],"tail_curl");
function cube(name,from,to,col,group,rotation,origin){const a=new Cube({name,from,to,box_uv:false,autouv:0,origin:origin||[0,0,0],rotation:rotation||[0,0,0]});a.addTo(groups[group]);a.init();for(const f of Object.values(a.faces)){f.texture=tex.uuid;f.uv=slots[col].slice();}made.push(a);return a;}
function b(name,x,y,z,w,h,d,col,group,rotation,origin){return cube(name,[x,y,z],[x+w,y+h,z+d],col,group,rotation,origin)}
let seed=314159;function rnd(){seed=(seed*1664525+1013904223)>>>0;return seed/4294967296}
const furcols=["fur","fur_mid","fur_light","fur_tip","fur_dark"];function fc(){return furcols[Math.floor(rnd()*furcols.length)]}
b("torso", -3.15,4.1,-2.4,6.3,10.6,5.5,"fur","body");
b("shoulder_mass",-3.65,11.5,-2.1,7.3,3.1,4.9,"fur_mid","body");
b("hips",-2.9,3.1,-1.2,5.8,4,4.6,"fur_dark","body");
b("neck",-2.35,14,-1.75,4.7,3,4.1,"fur_dark","neck");
const bib=[[-2.55,12.65,5.1,2.0],[-2.4,10.65,4.8,2],[-2.1,8.65,4.2,2],[-1.7,6.8,3.4,1.85],[-1.35,5.6,2.7,1.2]];
bib.forEach((a,i)=>b("chest_white_"+i,a[0],a[1],-2.68,a[2],a[3],0.6,i%2?"cream":"cream_light","body"));
for(let y=6.3;y<14;y+=1.4){const half=y>12?2.2:y>9?1.8:1.35;b("bib_shade_"+y,-half,y,-2.74,0.5,1.15,0.18,"cream_shadow","body");b("bib_light_"+y,-0.7,y+0.05,-2.77,1.15,1.12,0.17,"cream_light","body");}
for(let row=0;row<6;row++)for(let c=0;c<4;c++){b("back_coat_"+row+"_"+c,-3.12+c*1.52,4.1+row*1.65,3.0,1.65,2.0,0.65+rnd()*0.3,fc(),"body");}
for(const side of [-1,1]){const s=side===1?"left":"right";let ag="arm_"+s,hg="hand_"+s,lg="leg_"+s,fg="foot_"+s;
const rot=[0,0,side*8],p=[side*3.5,13.3,0];
b("upper_arm_"+s,side===1?3.1:-5.5,6.4,-1.7,2.4,7.4,3.65,"fur",""+ag,rot,p);
b("forearm_"+s,side===1?3.5:-6.1,1.6,-2.0,2.6,6.5,3.9,"fur_mid",ag,rot,p);
for(let row=0;row<7;row++){const y=2+row*1.6;const x=side*(5.05-(y-2)*0.09);b("arm_lock_"+s+"_"+row,x-(side===1?0.05:1.35),y,-2.35,1.4,1.85,0.8,fc(),ag);b("arm_outer_fur_"+s+"_"+row,side===1?x+1.1:x-1.7,y+0.15,-0.85,0.65,1.85,2.3,fc(),ag);}
b("hand_"+s,side===1?3.4:-6.5,0.25,-3.1,3.1,1.8,4.4,"cream",hg);
b("hand_top_"+s,side===1?3.7:-6.2,1.65,-2.25,2.5,0.65,2.9,"cream_light",hg);
for(let j=0;j<3;j++){const x=side===1?3.6+j*0.98:-6.2+j*0.98;b("finger_"+s+"_"+j,x,0,-3.5,0.76,1.3,1.5,"cream_light",hg);}
b("leg_"+s,side===1?0.5:-2.8,0.9,-0.55,2.3,4.7,3.35,"fur_dark",lg);
b("leg_front_"+s,side===1?0.5:-2.8,1.4,-0.9,2.3,2.9,0.7,"fur",lg);
b("foot_"+s,side===1?0.3:-3.05,0,-2.05,2.75,1.05,4.5,"cream_shadow",fg);
b("foot_cap_"+s,side===1?0.4:-2.95,0.85,-1.2,2.55,0.5,3.25,"cream",fg);
for(let j=0;j<3;j++)b("toe_"+s+"_"+j,(side===1?0.38:-2.95)+j*0.86,0,-2.65,0.69,0.88,1.4,"cream",fg);
[[4.95,7.7,-2.46],[5.25,6.15,-2.52],[4.2,10.8,-2.37],[5.85,5.4,-0.8]].forEach((a,i)=>b("arm_teal_"+s+"_"+i,side===1?a[0]:-a[0]-0.82,a[1],a[2],0.82,1.13,0.34,i%2?"teal":"teal_light",ag));
}
b("head_core",-6.2,16.2,-4.5,12.4,10.55,9.5,"fur","head");
b("jaw_mass",-5.45,15.5,-4.85,10.9,2.5,8.8,"fur_dark","head");
b("face_upper",-4.6,20,-5.45,9.2,4.7,0.9,"skin_light","face");
b("face_cheeks",-4.35,18.3,-5.72,8.7,3,1.05,"skin","face");
b("face_muzzle",-3.4,16.8,-5.9,6.8,3,1.1,"skin","face");
b("chin",-2.55,16.25,-5.7,5.1,1,0.65,"skin_shade","face");
for(const side of [-1,1]){
const s=side===1?"left":"right",x=side===1?1.4:-4.05;
b("eye_white_"+s,x,20.35,-5.86,2.65,3.15,0.4,"eye_white","face");
b("eye_upper_lid_"+s,x-0.08,23.5,-5.92,2.8,0.5,0.4,"brow","face");
b("eye_lower_shadow_"+s,x+0.25,20.21,-5.95,2.3,0.18,0.13,"skin_shade","face");
const px=side===1?1.95:-3.5;
b("pupil_"+s,px,20.45,-6.04,1.6,2.45,0.25,"eye_black","face");
b("iris_bottom_"+s,px+0.08,20.47,-6.055,1.4,0.65,0.05,"eye_brown","face");
b("eye_glint_"+s,px+0.15,22.28,-6.085,0.5,0.52,0.05,"eye_glint","face");
b("eye_glint_small_"+s,px+1.03,21.85,-6.09,0.2,0.2,0.05,"eye_glint","face");
b("brow_"+s,x-0.06,24.12,-5.91,2.75,0.52,0.42,"brow","face");
}
b("nose_bridge",-0.62,19.67,-6.2,1.24,0.62,0.65,"nose","face");
b("nose_tip",-0.34,19.45,-6.28,0.68,0.32,0.42,"eye_black","face");
b("smile",-1.1,18.4,-6.015,2.2,0.15,0.1,"mouth","face");
b("smile_corner_left",1.06,18.48,-6.01,0.2,0.2,0.1,"mouth","face");
b("smile_corner_right",-1.26,18.48,-6.01,0.2,0.2,0.1,"mouth","face");
for(const side of [-1,1]){
const s=side===1?"left":"right",eg="ear_"+s;
b("ear_rim_"+s,side===1?6.05:-9.15,18.5,-2.55,3.1,5.1,4.4,"cream",eg);
b("ear_top_"+s,side===1?6.25:-8.95,23.6,-2.3,2.7,0.55,3.9,"cream_light",eg);
b("ear_inner_"+s,side===1?6.9:-8.65,19.4,-2.7,1.75,3.45,0.3,"ear_inner",eg);
b("ear_inner_shadow_"+s,side===1?6.9:-7.45,19.6,-2.77,0.55,2.8,0.1,"skin_shade",eg);
b("ear_front_edge_"+s,side===1?6.08:-9.15,18.7,-2.83,0.75,4.7,0.6,"cream_light",eg);
}
for(let row=0;row<3;row++)for(let c=0;c<6;c++){
const y=24.45+row*1.15;const x=-6.25+c*2.06+((row%2)*0.25);const cut=row===2&&(c===0||c===5);if(cut)continue;
b("forehead_fur_"+row+"_"+c,x,y,-5.4+row*0.65,2.2,1.5,1.5,fc(),"mane");
}
for(const side of [-1,1]){
for(let row=0;row<5;row++){
const y=16.25+row*1.8;const width=row===0?1.7:1.35;const x=side===1?4.8:-4.8-width;
b("sideburn_"+side+"_"+row,x,y,-5.35,width,2.05,1.9,fc(),"mane");
}
for(let row=0;row<6;row++)for(let col=0;col<4;col++){
const y=16.4+row*1.65;const z=-3.7+col*2.0;const protrude=0.35+rnd()*0.5;
const x=side===1?5.75:-6.25-protrude;
b("side_mane_"+side+"_"+row+"_"+col,x,y,z,0.9+protrude,2.0,2.1,fc(),"mane");
}
}
for(let row=0;row<7;row++)for(let col=0;col<6;col++){
const x=-6.1+col*1.95+(row%2)*0.2;const y=16.1+row*1.55;const z=4.25+((col+row)%3)*0.26;
b("rear_mane_"+row+"_"+col,x,y,z,2.1,1.85,0.9+rnd()*0.55,fc(),"mane");
}
const crest=[[-5.8,27.0,-1.8,2.7,1.4,3.2],[-4.8,28,-0.5,2.2,1.8,2.8],[-5.2,29.1,0.8,1.6,1.2,2],[-3.1,27.5,-2.5,2.7,1.6,3.4],[-2.1,28.4,-0.7,2.1,1.1,3],[-0.3,27.1,-2.8,2.8,1.5,3.3],[1.8,27.2,-1.8,2.5,1.1,3.2],[3.7,26.8,0.0,2.25,1.2,3],[-4.9,27.1,3,3.1,1.25,2.5],[-1.9,27.1,2.6,3.1,1.8,2.8],[1.1,26.8,2.5,3.3,1.6,2.8],[3.8,26.25,3,2,1.7,2.5]];
crest.forEach((a,i)=>b("swept_crest_"+i,...a,i%3?"fur_light":"fur_hot","mane"));
[[-7.0,25.8,2.7,2.1,1.2,2.5],[-7.6,24.1,4.0,2.0,1.1,2.2],[-7.5,21.4,4.5,2.0,1.2,1.9],[-7.1,18.8,4.3,1.8,1.15,2.1],[-6.3,16.7,3.8,1.55,1.15,2]].forEach((a,i)=>b("windward_lock_"+i,...a,fc(),"mane"));
[[-4.7,25.1,-5.54,1.1,1.0],[-5.75,24.35,-5.45,1.25,1.1],[-4.65,23.9,-5.56,1.0,1.0],[-3.8,24.65,-5.55,1.15,0.8]].forEach((a,i)=>b("temple_teal_"+i,a[0],a[1],a[2],a[3],a[4],0.28,i%2?"teal":"teal_light","mane"));
[[-4.3,22.5,5.51,1.45,0.8],[-3.2,21.6,5.57,1.3,0.9],[-2.1,22.5,5.54,1.0,0.85],[2.2,19.1,5.52,0.8,1.2]].forEach((a,i)=>b("rear_teal_"+i,a[0],a[1],a[2],a[3],a[4],0.3,i%2?"teal_light":"teal","mane"));
[[-2.6,8.5,3.99,0.9,1.7],[-1.7,9.6,4.01,0.9,1.2],[1.8,12,3.9,1,1.35],[1.3,5.65,4.0,0.85,1.1]].forEach((a,i)=>b("back_teal_"+i,a[0],a[1],a[2],a[3],a[4],0.24,i%2?"teal":"teal_dark","body"));
const tail=[[0,5.3,3.1],[1.2,4.9,4.5],[2.9,4.3,4.8],[4.7,4.45,4.8],[6.4,5.35,4.8],[7.7,6.6,4.8],[8.5,8.25,4.8],[8.55,10,4.8],[7.8,11.45,4.8],[6.15,12.05,4.8],[4.65,11.45,4.8],[4.15,10.05,4.8],[4.8,9.1,4.8],[6.15,9.3,4.8],[6.5,10.2,4.8]];
for(let i=0;i<tail.length-1;i++){
const a=tail[i],n=tail[i+1];const dx=n[0]-a[0],dy=n[1]-a[1],dz=n[2]-a[2];const len=Math.hypot(dx,dy,dz);const w=i>10?1.15:1.4;const az=-Math.atan2(dx,dy)*180/Math.PI,rx=Math.atan2(dz,Math.hypot(dx,dy))*180/Math.PI;
b("tail_segment_"+i,a[0]-w/2,a[1]-0.16,a[2]-w/2,w,len+0.3,w,i%4===0?"fur_dark":i%3===0?"fur_light":"fur",i<4?"tail_base":i<11?"tail_curl":"tail_tip",[rx,0,az],a);
}
Canvas.updateAll();unselectAll();Undo.finishEdit("Build Xingxing from multiview reference",{elements:made,textures:[tex],outliner:true});
Preview.selected.camera.position.set(43,28,-64);Preview.selected.controls.target.set(0,14.8,0);Preview.selected.controls.update();
return {cubes:made.length,bones:Object.keys(groups).length,texture:tex.name,height:30.3,front:"negative Z"};
})()
