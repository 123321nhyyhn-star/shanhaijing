(() => {
const tex=Texture.all[0],old=Cube.all.slice(),made=[],colors={fur:"#ae3419",fur_light:"#cb4423",fur_hot:"#dc522d",fur_dark:"#7b230f",fur_mid:"#b93a1c"};
Undo.initEdit({elements:old,textures:[tex],bitmap:true,outliner:true});
let seed=237;const rnd=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296};
const sample=document.createElement("canvas");sample.width=tex.width;sample.height=tex.height;const sc=sample.getContext("2d");sc.drawImage(tex.img,0,0);const originalColor=new Map();
for(const c of old){const u=c.faces.north.uv,p=sc.getImageData(Math.floor((u[0]+u[2])/2),Math.floor((u[1]+u[3])/2),1,1).data;originalColor.set(c.uuid,"#"+Array.from(p.slice(0,3)).map(v=>v.toString(16).padStart(2,"0")).join(""));}
const panels=old.filter(c=>/^(upper|forearm)_coat_.*_(front|side)_/.test(c.name));
for(const c of panels){
const front=c.name.includes("_front_"),parts=front?3:2,span=front?0:2,len=c.to[span]-c.from[span];for(let j=0;j<parts;j++){
const from=c.from.slice(),to=c.to.slice();from[span]+=j*len/parts+0.03;to[span]=c.from[span]+(j+1)*len/parts-0.03;from[1]+=rnd()*0.05;to[1]=from[1]+0.86+rnd()*0.11;
if(front){from[2]-=rnd()*0.12;to[2]=from[2]+0.48;}else{from[0]-=0.03*rnd();to[0]=from[0]+0.53;}
const a=new Cube({name:c.name+"_voxel_"+j,from,to,origin:c.origin.slice(),rotation:c.rotation.slice(),box_uv:false,autouv:0}).addTo(c.parent).init();a._xingColor=[colors.fur,colors.fur_light,colors.fur_mid,colors.fur_hot][Math.floor(rnd()*4)];made.push(a);
}c.remove();
}
for(const c of Cube.all){if(/^rear_mane_/.test(c.name)){c.to[0]=c.from[0]+1.88;c.to[1]=c.from[1]+1.48;}if(/^side_mane_/.test(c.name)){c.to[1]=c.from[1]+1.53;c.to[2]=c.from[2]+1.93;}if(/^sideburn_/.test(c.name))c.to[1]=c.from[1]+1.73;}
const defs=[];for(const c of Cube.all){const size=c.to.map((v,i)=>v-c.from[i]);for(const [name,f] of Object.entries(c.faces)){const ax=name==="east"||name==="west"?[2,1]:name==="up"||name==="down"?[0,2]:[0,1];defs.push({c,f,name,w:Math.max(2,Math.ceil(size[ax[0]]*3)),h:Math.max(2,Math.ceil(size[ax[1]]*3))});}}
let N=512,layout;for(;;){let x=1,y=1,row=0,ok=true;layout=[];for(const d of defs){if(x+d.w+2>N){x=1;y+=row+2;row=0}if(y+d.h+2>N){ok=false;break}layout.push([x,y]);x+=d.w+2;row=Math.max(row,d.h)}if(ok)break;N*=2;}
const atlas=document.createElement("canvas");atlas.width=N;atlas.height=N;const ctx=atlas.getContext("2d");ctx.fillStyle="#722410";ctx.fillRect(0,0,N,N);
function tint(hex,k){const rgb=hex.match(/\w\w/g).map(v=>parseInt(v,16));return "#"+rgb.map(v=>Math.max(0,Math.min(255,Math.round(v*k))).toString(16).padStart(2,"0")).join("")}
defs.forEach((d,i)=>{const [x,y]=layout[i];let col=d.c._xingColor||originalColor.get(d.c.uuid)||colors.fur;const fur=(!/face|ear|hand|foot/.test(d.c.parent?.name||""))||/fur|coat|mane|crest|sideburn/.test(d.c.name);if(fur&&col.toLowerCase().startsWith("#a"))col=colors.fur;
ctx.fillStyle=col;ctx.fillRect(x-1,y-1,d.w+2,d.h+2);
if(fur){for(let py=1;py<d.h-1;py+=2)for(let px=1;px<d.w-1;px+=2){if(rnd()<0.32){ctx.fillStyle=tint(col,0.87+rnd()*0.25);ctx.fillRect(x+px,y+py,Math.min(2,d.w-px),Math.min(2,d.h-py));}}ctx.fillStyle=tint(col,1.10);ctx.fillRect(x,y,d.w,1);ctx.fillStyle=tint(col,0.87);ctx.fillRect(x,y+d.h-1,d.w,1);}
else if(!/mc_eye|nostril|cavity/.test(d.c.name)){ctx.fillStyle=tint(col,1.035);ctx.fillRect(x,y,d.w,Math.min(2,d.h));ctx.fillStyle=tint(col,0.97);ctx.fillRect(x,y+d.h-1,d.w,1);}
d.f.texture=tex.uuid;d.f.uv=[x,y,x+d.w,y+d.h];});
Project.texture_width=N;Project.texture_height=N;tex.uv_width=N;tex.uv_height=N;tex.name="xingxing_v2.png";tex.fromDataURL(atlas.toDataURL("image/png"));
Cube.all.forEach(c=>delete c._xingColor);Canvas.updateAll();unselectAll();Undo.finishEdit("Stagger voxel fur and remove overlapping fur faces",{elements:Cube.all.slice(),textures:[tex],bitmap:true,outliner:true});return {total:Cube.all.length,atlas:N,panels:panels.length};
})()
