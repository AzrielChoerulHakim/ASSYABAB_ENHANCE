/* CAHAYA — original 3D book, rehal, chamber, and light-to-pixel choreography. */
(() => {
'use strict';
const {M,Geometry:G,Renderer,PI,TAU,mix,clamp,smooth,rand,color}=window.A3D;
const C=(w,h,fn)=>{let c=document.createElement('canvas');c.width=w;c.height=h;fn(c.getContext('2d',{willReadFrequently:true}),w,h);return c;};
function ornament(c,x,y,r,n=8){c.save();c.translate(x,y);for(let k=0;k<3;k++){c.beginPath();for(let j=0;j<=n*2;j++){let a=j/(n*2)*TAU-PI/2,s=r*(j%2?.78:1)*(1-k*.115);j?c.lineTo(Math.cos(a)*s,Math.sin(a)*s):c.moveTo(Math.cos(a)*s,Math.sin(a)*s);}c.closePath();c.stroke();}for(let j=0;j<n*2;j++){let a=j/(n*2)*TAU;c.beginPath();c.ellipse(Math.cos(a)*r*.86,Math.sin(a)*r*.86,r*.085,r*.17,a+PI/2,0,TAU);c.stroke();}c.restore();}
function gildedCover(){return C(900,1300,(c,w,h)=>{let r=rand(511);c.fillStyle='#15362c';c.fillRect(0,0,w,h);for(let i=0;i<48000;i++){let v=r()>.5?'204,182,128':'1,9,4';c.fillStyle=`rgba(${v},${r()*.085})`;c.fillRect(r()*w,r()*h,.5+r()*1.3,.5+r()*1.3);}c.strokeStyle='#b29a61';c.lineWidth=1.8;for(let b of[27,33,41,64,76])c.strokeRect(b,b,w-b*2,h-b*2);
 for(let y=91;y<h-70;y+=24)for(let x=90;x<w-70;x+=24){c.strokeStyle='#8791673a';c.beginPath();c.arc(x,y,7,0,TAU);c.stroke();}
 c.strokeStyle='#c8b680';c.lineWidth=1.2;for(let y=55;y<h-40;y+=30){c.beginPath();c.moveTo(43,y-10);c.quadraticCurveTo(62,y,43,y+10);c.stroke();c.beginPath();c.moveTo(w-43,y-10);c.quadraticCurveTo(w-62,y,w-43,y+10);c.stroke();}
 c.fillStyle='#19392d';c.beginPath();c.ellipse(w/2,h/2,280,375,0,0,TAU);c.fill();c.strokeStyle='#d3bb7a';c.lineWidth=1.8;ornament(c,w/2,h/2,320,12);
 for(let a=0;a<TAU;a+=TAU/48){c.save();c.translate(w/2,h/2);c.rotate(a);c.beginPath();c.moveTo(168,0);c.bezierCurveTo(228,-38,276,-16,305,0);c.bezierCurveTo(276,16,228,38,168,0);c.stroke();c.restore();}
 c.fillStyle='#15352b';c.beginPath();c.ellipse(w/2,h/2,140,180,0,0,TAU);c.fill();c.strokeStyle='#d0b87a';c.stroke();c.fillStyle='#e0cb94';c.textAlign='center';c.direction='rtl';c.font='72px Georgia,serif';c.fillText('القرآن',w/2,h/2-23);c.fillText('الكريم',w/2,h/2+69);c.direction='ltr';
 for(let x of[132,w-132])for(let y of[140,h-140]){c.strokeStyle='#cdb97c';c.lineWidth=1.4;ornament(c,x,y,38);}
 c.strokeStyle='#b59e64';for(let y of[245,h-245]){c.beginPath();c.moveTo(w*.28,y);c.quadraticCurveTo(w*.5,y-45,w*.72,y);c.quadraticCurveTo(w*.5,y+45,w*.28,y);c.stroke();}
});}
function flyleaf(){return C(640,900,(c,w,h)=>{let r=rand(28),gr=c.createLinearGradient(0,0,w,0);gr.addColorStop(0,'#ad9669');gr.addColorStop(.12,'#ded0ac');gr.addColorStop(.48,'#f0e7cd');gr.addColorStop(1,'#e1d4b0');c.fillStyle=gr;c.fillRect(0,0,w,h);for(let i=0;i<11000;i++){c.fillStyle='rgba(100,80,37,.025)';c.fillRect(r()*w,r()*h,1,1);}c.strokeStyle='#ad985e';c.lineWidth=1.2;for(let b of[34,39,50])c.strokeRect(b,b,w-b*2,h-b*2);for(let x of[83,w-83])for(let y of[86,h-86])ornament(c,x,y,24);c.strokeStyle='#b9a26b';c.lineWidth=1;ornament(c,w/2,h/2,186,12);c.beginPath();c.ellipse(w/2,h/2,67,91,0,0,TAU);c.stroke();/* Ornamental flyleaf, not a fabricated page of scripture. */});}
function wood(){return C(300,900,(c,w,h)=>{let r=rand(255);c.fillStyle='#694521';c.fillRect(0,0,w,h);for(let i=0;i<380;i++){let x=r()*w;c.strokeStyle=r()>.5?'#cca66533':'#2d160c55';c.lineWidth=.4+r()*1.2;c.beginPath();for(let y=0;y<h;y+=9){let X=x+Math.sin(y*.011+x*.05)*9+Math.sin(y*.037+x*.1)*1.7;y?c.lineTo(X,y):c.moveTo(X,y);}c.stroke();}});}
function stone(){return C(512,512,(c,w,h)=>{let r=rand(25);c.fillStyle='#22373b';c.fillRect(0,0,w,h);for(let i=0;i<40000;i++){c.fillStyle=r()>.5?'#d1d9c805':'#071b1908';c.fillRect(r()*w,r()*h,1.5,1.5);}for(let j=0;j<17;j++){let x=r()*w;c.beginPath();for(let y=0;y<h;y+=7){let X=x+Math.sin(y*.028+j)*10+Math.sin(y*.072)*2;y?c.lineTo(X,y):c.moveTo(X,y);}c.lineWidth=.5;c.strokeStyle='#a2b8ac22';c.stroke();}});}
function pageEdges(){return C(256,256,(c,w,h)=>{c.fillStyle='#d6c5a0';c.fillRect(0,0,w,h);for(let y=0;y<h;y+=3){c.fillStyle=y%2?'#ae97725c':'#f6e6bd6b';c.fillRect(0,y,w,.8);}});}
function windowTexture(){return C(300,650,(c,w,h)=>{let gr=c.createLinearGradient(0,0,0,h);gr.addColorStop(0,'#9eab9e');gr.addColorStop(.5,'#e7d9b5');gr.addColorStop(1,'#51655b');c.fillStyle=gr;c.fillRect(0,0,w,h);c.strokeStyle='#354b3c';c.lineWidth=4;for(let x=-h;x<w+h;x+=35){c.beginPath();c.moveTo(x,0);c.lineTo(x+h,h);c.stroke();c.beginPath();c.moveTo(x,0);c.lineTo(x-h,h);c.stroke();}c.fillStyle='#11262222';c.fillRect(0,0,w,h);});}
function monitorTexture(){return C(1200,760,(c,w,h)=>{c.fillStyle='#071a23';c.fillRect(0,0,w,h);c.strokeStyle='#456169';c.lineWidth=1;c.strokeRect(22,22,w-44,h-44);c.fillStyle='#9fb3b2';c.font='13px Arial';c.fillText('ASSYABAB  /  MULTIMEDIA STUDIO',46,56);c.fillStyle='#bca16c';c.beginPath();c.arc(w-52,51,4,0,TAU);c.fill();let gr=c.createLinearGradient(80,90,1000,550);gr.addColorStop(0,'#5c817b');gr.addColorStop(.5,'#324e58');gr.addColorStop(1,'#172b35');c.fillStyle=gr;c.fillRect(55,88,w-110,440);c.strokeStyle='#b5bfb34d';c.beginPath();c.arc(890,185,105,0,TAU);c.stroke();c.fillStyle='#ece4d1';c.font='80px Georgia';c.fillText('Ilmu yang',100,250);c.font='italic 91px Georgia';c.fillText('menjadi karya.',100,350);c.fillStyle='#b2c1b3';c.font='13px Arial';c.fillText('SEBUAH PESAN. BANYAK KEMUNGKINAN.',104,462);c.fillStyle='#a1b3ae';c.font='11px Arial';c.fillText('01   PESAN',55,573);c.fillText('02   MEDIUM',55,620);for(let i=0;i<7;i++){c.fillStyle=i%3?'#496763':'#a19169';c.fillRect(180+i*130,554,124,25);c.fillStyle=i%2?'#587078':'#657963';c.fillRect(180+i*130,600,124,25);}c.fillStyle='#ddc38c';c.fillRect(640,543,2,100);c.fillStyle='#759089';c.font='10px Arial';c.fillText('ILUSTRASI STUDIO — BUKAN PERANGKAT LUNAK PENYUNTING',55,697);});}
// Smooth rounded boxes avoid the hard unlit cuboids of the earlier experiment.
function bevelBox(w,h,d,r=.04,n=8){const g=new G(),dims=[w,h,d],hs=dims.map(v=>v/2),inner=hs.map(v=>Math.max(0,v-r));
 for(let axis=0;axis<3;axis++)for(let sign of[-1,1]){let a=(axis+1)%3,b=(axis+2)%3;const point=(u,v)=>{let p=[0,0,0];p[axis]=hs[axis]*sign;p[a]=(u-.5)*dims[a];p[b]=(v-.5)*dims[b];let q=p.map((x,i)=>clamp(x,-inner[i],inner[i])),N=p.map((x,i)=>x-q[i]),len=Math.hypot(...N)||1;N=N.map(v=>v/len);return [...q.map((x,i)=>x+N[i]*r),...N,u,v];};
  for(let i=0;i<n;i++)for(let j=0;j<n;j++){let A=point(i/n,j/n),B=point((i+1)/n,j/n),D=point(i/n,(j+1)/n),C=point((i+1)/n,(j+1)/n);if(sign>0)g.v.push(...A,...B,...C,...A,...C,...D);else g.v.push(...A,...C,...B,...A,...D,...C);}}
 return g;}
function archPath(cx,base,z,w,h){const pts=[[cx-w/2,base,z],[cx-w/2,base+h-w/2,z]];for(let i=0;i<=54;i++){let a=PI-i/54*PI;pts.push([cx+Math.cos(a)*w/2,base+h-w/2+Math.sin(a)*w/2,z]);}pts.push([cx+w/2,base,z]);return pts;}
class CahayaScene{
 constructor(canvas){this.canvas=canvas;this.renderer=new Renderer(canvas);this.room=[];this.studio=[];this.pages=[];this.coverParts=[];this.ribbons=[];this.progress=0;this.time=0;this.pointer=[0,0];this.metrics={frames:0,bookOpen:0,scene:'chamber',webgl:true};this.quality=1;this.makeRoom();this.makeBook();this.makeStudio();this.resize();}
 add(geo,position=[0,0,0],rotation=[0,0,0],opts={},dest=this.room){return this.renderer.mesh(geo,{matrix:M.compose(position,rotation),...opts,group:dest})&&this.addLast(dest);}
 addLast(dest){const m=this.renderer.meshes.at(-1);dest.push(m);return m;}
 makeRoom(){let r=this.renderer,stoneTex=r.texture(stone()),glass=r.texture(windowTexture()),gold=color('a99158');
 this.floor=this.add(new G().plane(38,38),[0,-.07,0],[0,0,0],{color:color('344442'),rough:.25,metal:.55,mode:1});
 // Inlaid floor joints, not a glowing decorative magic circle.
 const joints=new G();for(let x=-15;x<=15;x+=3)joints.tube([[x,-.062,-20],[x,-.062,15]],.008,3);for(let z=-18;z<=12;z+=3)joints.tube([[-15,-.062,z],[15,-.062,z]],.008,3);this.add(joints,[0,0,0],[0,0,0],{color:color('4c5a50'),rough:.8});
 this.add(new G().box(28,13,.6),[0,6.1,-7.2],[0,0,0],{texture:stoneTex,color:[1,1,1],rough:1});
 for(let [x,z,w,h]of[[0,-6.7,3.9,7.1],[-5.9,-6.7,3.1,6.8],[5.9,-6.7,3.1,6.8]]){
  const path=archPath(x,.05,z,w,h);this.add(new G().tube(path,.11,12),[0,0,0],[0,0,0],{color:color('627164'),rough:.55,metal:.25});this.add(new G().tube(archPath(x,.07,z+.06,w-.23,h-.14),.018,8),[0,0,0],[0,0,0],{color:gold,rough:.35,metal:.9});
  // Arched lattice is clipped geometrically, with a lit, distant environment.
  let geo=new G(),centre=[x,.06,z-.01],points=archPath(x,.06,z-.01,w-.36,h-.25);for(let i=0;i<points.length-1;i++){const a=centre,b=points[i],cc=points[i+1];geo.tri(a,b,cc,[[.5,0],[(b[0]-x)/(w-.36)+.5,(b[1]-.06)/(h-.25)],[(cc[0]-x)/(w-.36)+.5,(cc[1]-.06)/(h-.25)]]);}
  this.add(geo,[0,0,0],[0,0,0],{texture:glass,color:color('cbd0bb'),emission:x===0?.3:.1,rough:1,shadow:false});
 }
 for(let side of[-1,1])for(let z of[-5,-.5,4.0]){let x=side*6.7;this.add(new G().cylinder(.18,.24,7.7,32),[x,3.82,z],[0,0,0],{color:color('485951'),rough:.65});for(let y of[.14,.27,6.85,7.06])this.add(new G().cylinder(.29,.29,.055,32),[x,y,z],[0,0,0],{color:gold,metal:.85,rough:.33});}
 // One coherent shaft, split by the window grille into very soft shafts.
 for(let i=0;i<9;i++){let d=i*.155,g=new G().quad([-4.4+d,7.5,-3.4],[-4.22+d,7.5,-3.4],[2.5+d,-.04,3.7],[1.2+d,-.04,3.9]);this.add(g,[0,0,0],[0,0,0],{color:color('e3d3aa'),mode:2,emission:1.1,alpha:.023,shadow:false,additive:true});}
 for(let [x,z,s]of[[-3.7,-2.1,1],[3.9,-3.6,.85]]){const body=new G().cylinder(.25,.32,.15,8,[0,.1,0]).cylinder(.27,.27,.55,8,[0,.45,0]).cylinder(.08,.28,.20,8,[0,.80,0]);const m=this.add(body,[x,0,z],[0,0,0],{color:gold,metal:.75,rough:.35});m.matrix=M.compose([x,0,z],[0,0,0],[s,s,s]);this.add(new G().cylinder(.205,.205,.35,8),[x,.42*s,z],[0,0,0],{color:color('dabe81'),emission:1.0,shadow:false});let bar=new G();for(let j=0;j<8;j++){let a=j/8*TAU;bar.cylinder(.016,.016,.61,6,[Math.cos(a)*.27,.45,Math.sin(a)*.27]);}this.add(bar,[x,0,z],[0,0,0],{color:color('2c3024'),metal:.8});}
 }
 makeBook(){const r=this.renderer,cover=r.texture(gildedCover()),paper=r.texture(flyleaf()),edge=r.texture(pageEdges()),woodTex=r.texture(wood()),w=1.89,h=2.76;this.w=w;this.coverTex=cover;
 // Two intersecting walnut planks with slim brass inlay and carved end medallions.
 for(let side of[-1,1]){let mat=M.compose([0,.69,0],[0,0,side*.46]);const board=this.add(bevelBox(3.2,.15,1.58,.055,12),[0,0,0],[0,0,0],{texture:woodTex,color:[1,1,1],rough:.45});board.matrix=mat;
  const trim=new G();for(let z of[-.72,.72])trim.tube([[-1.52,.082,z],[1.52,.082,z]],.008,4);let m=this.add(trim,[0,0,0],[0,0,0],{color:color('be9b5a'),metal:.9,rough:.4});m.matrix=mat;
  const engrave=new G();for(let x of[-1.27,1.27])for(let j=0;j<3;j++){let pts=[];for(let k=0;k<=24;k++){let a=k/24*TAU,rr=k%2?.11+j*.024:.16+j*.024;pts.push([x+Math.cos(a)*rr,.083,Math.sin(a)*rr]);}engrave.tube(pts,.007,3);}m=this.add(engrave,[0,0,0],[0,0,0],{color:color('caab69'),metal:.7,rough:.6});m.matrix=mat;
 }
 const base=(geo,local,opts={})=>{let m=this.add(geo,[0,0,0],[0,0,0],opts);this.coverParts.push({m,local});return m;};
 base(bevelBox(w+.1,.085,h+.1,.036,12),M.translate(w/2,0,0),{color:color('17372c'),metal:.28,rough:.5});
 base(bevelBox(w-.05,.145,h-.075,.018,9),M.translate(w/2,.105,0),{texture:edge,color:color('f1dfb8'),rough:.9});
 base(new G().plane(w-.075,h-.10,48,8),M.translate(w/2,.186,0),{texture:paper,color:[1,1,1],rough:1,curl:.04});
 this.front=this.add(bevelBox(w+.1,.08,h+.1,.037,12),[0,0,0],[0,0,0],{color:color('1f4434'),metal:.22,rough:.5});
 this.frontExterior=this.add(new G().plane(w+.02,h+.02,1,1),[0,0,0],[0,0,0],{texture:cover,color:[1,1,1],metal:.4,rough:.54});
 this.frontInterior=this.add(new G().plane(w-.05,h-.05),[0,0,0],[0,0,0],{texture:paper,color:color('d2c092'),rough:.8});
 this.spine=this.add(new G().cylinder(.093,.093,h+.065,30),[0,0,0],[PI/2,0,0],{color:color('234433'),rough:.5,metal:.25});
 for(let i=0;i<18;i++){let m=this.add(new G().plane(w-.09,h-.12,58,10),[0,0,0],[0,0,0],{color:i%5===0?[1,1,1]:color('eaddbb'),texture:i===17||i===0||i===8?paper:null,rough:.95});this.pages.push(m);}
 // A single line of light around the book. It never extracts or distorts scripture.
 for(let j=0;j<2;j++){let g=new G(),pts=[];for(let i=0;i<=200;i++){let a=i/200*TAU*1.10+j*.9,rad=2.0+j*.13;pts.push([Math.cos(a)*rad,1.7+i/200*.6+j*.14,Math.sin(a)*rad*.72]);}g.tube(pts,.006-j*.0015,5);let m=this.add(g,[0,0,0],[0,0,0],{color:color('edd497'),emission:.7,alpha:.04,additive:true,shadow:false});this.ribbons.push(m);}
 this.updateBook(0);
 }
 updateBook(open){const w=this.w;this.metrics.bookOpen=open;const base=M.compose([-w/2*(1-open),1.18,0],[0,0,.15]);this.base=base;for(let {m,local}of this.coverParts)m.matrix=M.mul(base,local);this.spine.matrix=M.mul(base,M.mul(M.translate(0,.1,0),M.rx(PI/2)));
  let a=mix(.04,PI-.32,smooth(0,.72,open));let pivot=M.mul(base,M.mul(M.translate(0,.205,0),M.rz(a)));this.front.matrix=M.mul(pivot,M.translate(w/2,0,0));this.frontExterior.matrix=M.mul(pivot,M.translate(w/2,.044,0));this.frontInterior.matrix=M.mul(pivot,M.mul(M.translate(w/2,-.044,0),M.rx(PI)));
  for(let i=0;i<this.pages.length;i++){let lag=(this.pages.length-1-i)*.014,progress=smooth(.07+lag,.78+lag,open),angle=mix(.014,PI-.34-i*.0017,progress);this.pages[i].matrix=M.mul(base,M.mul(M.translate(0,.19+i*.0029,0),M.mul(M.rz(angle),M.translate(w/2,0,0))));this.pages[i].curl=Math.sin(progress*PI)*(.30+.08*Math.sin(i*.7))+.02;}
 }
 makeStudio(){const r=this.renderer,screen=r.texture(monitorTexture());this.add(new G().plane(40,40),[0,-.07,0],[0,0,0],{color:color('173139'),mode:1,metal:.7,rough:.3},this.studio);
 this.add(bevelBox(8,.22,4.0,.09,8),[.2,.75,-.3],[0,0,0],{color:color('233d40'),metal:.3,rough:.4},this.studio);
 this.add(bevelBox(5.88,3.8,.18,.085,10),[.2,3.05,-1.3],[0,0,0],{color:color('314b52'),metal:.8,rough:.25},this.studio);
 this.add(new G().plane(5.62,3.54),[.2,3.05,-1.19],[PI/2,0,0],{texture:screen,color:color('ffffff'),emission:.75,rough:1,shadow:false},this.studio);
 this.add(bevelBox(.21,1.1,.22,.02),[.2,1.22,-1.32],[0,0,0],{color:color('5d6f6c'),metal:.85,rough:.25},this.studio);this.add(bevelBox(1.8,.09,.94,.04),[.2,.905,-1.23],[0,0,0],{color:color('5b7478'),metal:.8,rough:.35},this.studio);
 const keys=new G();for(let z=0;z<5;z++)for(let x=0;x<14;x++)keys.box(.112,.028,.11,[(x-6.5)*.142,.91,.21+z*.138]);this.add(keys,[.2,0,0],[0,0,0],{color:color('7b8f89'),rough:.6},this.studio);this.add(bevelBox(2.12,.08,.82,.045,8),[.2,.86,.47],[0,0,0],{color:color('203637'),metal:.5,rough:.5},this.studio);
 // Camera body and lens, as an illustrative studio object.
 this.add(bevelBox(.88,.63,.45,.045),[-2.7,1.26,.22],[0,-.3,0],{color:color('233033'),metal:.5,rough:.48},this.studio);this.add(new G().cylinder(.26,.28,.65,44),[-2.77,1.27,.63],[PI/2,0,0],{color:color('1a252b'),metal:.8,rough:.28},this.studio);this.add(new G().cylinder(.205,.205,.01,48),[-2.77,1.27,.966],[PI/2,0,0],{color:color('547986'),metal:.85,rough:.18},this.studio);
 let pixel=new G(),rr=rand(710);for(let i=0;i<110;i++){let s=.015+rr()*.025;pixel.box(s,s,s,[(rr()-.5)*12,.6+rr()*6,(rr()-.5)*7]);}this.pixelCloud=this.add(pixel,[0,0,-1],[0,0,0],{color:color('b6c1ac'),emission:.25,alpha:.55,shadow:false},this.studio);
 for(let z of[-7,-12,-18])this.add(new G().tube([[-12,6,z],[12,6,z]],.007,5),[0,0,0],[0,0,0],{color:color('799f9b'),emission:.5,shadow:false},this.studio);
 }
 resize(){const r=this.canvas.getBoundingClientRect();this.renderer.resize(Math.max(1,r.width),Math.max(1,r.height),this.quality);}
 render(progress,time=0){this.progress=clamp(progress);this.time=time;const p=this.progress,narrow=this.canvas.clientWidth<760;let eye,target,env,objects=this.room;let open=smooth(.08,.52,p),dive=smooth(.62,.80,p),portal=smooth(.70,.80,p);this.updateBook(open);
 if(p<.8){let approach=smooth(0,.60,p);eye=[mix(5.0,.2,approach),mix(4.2,6.4,approach),mix(8.3,8.1,approach)];target=[mix(-1.65,0,approach),mix(1.9,2.45,approach),0];if(dive>0){eye=eye.map((v,i)=>mix(v,[0,1.83,.13][i],dive));target=[0,1.35,0];}if(narrow){eye[0]*=.3;eye[2]*=1.38;target[0]=0;target[1]+=1.00;}
 for(let j=0;j<this.ribbons.length;j++){this.ribbons[j].matrix=M.ry(time*(j===0?.045:-.033));this.ribbons[j].alpha=.025+open*.085;}
 env={fogColor:[.029,.057,.061],key:[1.10,1.04,.90],fog:.028,glow:[open*.13,open*.09,open*.045],energy:open,portal,bloom:.8,shadows:true,reflect:true};this.metrics.scene='chamber';
 }else{objects=this.studio;let q=smooth(.8,1,p);eye=[mix(.2,4.6,q),mix(3.05,4.6,q),mix(-.8,11.8,q)];target=[mix(.2,-2.4,q),2.6,-1.1];if(narrow){eye[0]*=.4;eye[2]+=3.4;target[0]=.2;target[1]+=1.3;}env={fogColor:[.027,.052,.071],key:[.78,1.03,1.12],fog:.023,glow:[.07,.11,.14],energy:.6,portal:1-smooth(.80,.875,p),bloom:.48,shadows:true,reflect:true};this.pixelCloud.matrix=M.ry(time*.012);this.metrics.scene='studio';}
 eye[0]+=this.pointer[0]*.09;eye[1]+=this.pointer[1]*.06;
 this.renderer.render(objects,{...env,eye,target,time,fov:.72,particles:true});this.metrics.frames=this.renderer.frames;this.metrics.progress=p;
 }
 dispose(){this.renderer.dispose();}
}
window.AssyababCahaya=CahayaScene;
})();
