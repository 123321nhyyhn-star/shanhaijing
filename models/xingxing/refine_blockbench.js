(() => {
const tex=Texture.all[0],made=[],groups=Object.fromEntries(Group.all.map(g=>[g.name,g]));
Undo.initEdit({elements:[],outliner:true});
const uv={fur:[2,2,14,14],fur_light:[18,2,30,14],fur_mid:[82,2,94,14],fur_dark:[50,2,62,14],teal:[98,18,110,30]};
function add(n,from,to,col,g){const c=new Cube({name:n,from,to,box_uv:false,autouv:0}).addTo(groups[g]).init();for(const f of Object.values(c.faces)){f.texture=tex.uuid;f.uv=uv[col].slice()}made.push(c)}
for(const s of [-1,1]){
for(let r=0;r<6;r++){
const y=4.1+r*1.65, x=s===1?2.15:-3.55;
add("chest_fur_border_"+s+"_"+r,[x,y,-2.9],[x+1.4,y+2,-2.1],r%3===0?"fur_light":r%2?"fur_mid":"fur","body");
add("flank_fur_"+s+"_"+r,[s===1?2.95:-3.8,y,-1.35],[s===1?3.85:-2.95,y+2.0,2.1],r%2?"fur_light":"fur","body");
}
for(let r=0;r<4;r++){const x=s===1?5.65:-7.45,y=17.2+r*2.1;add("mane_silhouette_"+s+"_"+r,[x,y,3.3],[x+1.8,y+1.15,5.55],r%2?"fur_light":"fur_mid","mane");}
}
for(let r=0;r<4;r++)add("back_centre_lock_"+r,[-0.65,13-r*1.9,3.7],[0.85,15.1-r*1.9,4.65],r%2?"fur_mid":"fur_light","body");
Canvas.updateAll();Undo.finishEdit("Refine fur silhouette",{elements:made,outliner:true});unselectAll();
return {added:made.length,total:Cube.all.length};
})()
