/* Original multilayer matte landscape. An illustration, not a surveyed campus. */
(() => {
'use strict';
const TAU=Math.PI*2,clamp=(v,a=0,b=1)=>Math.min(b,Math.max(a,v));
function rng(seed){return()=>{seed|=0;seed=seed+0x6D2B79F5|0;let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
function rgb(s){return s.match(/\w\w/g).map(x=>parseInt(x,16));}
function blend(a,b,t){a=rgb(a);b=rgb(b);return`rgb(${a.map((v,i)=>Math.round(v+(b[i]-v)*t)).join(',')})`;}
const THEMES=[
 {sky:['607f86','b9bca7'],far:'a4b8ab',near:'143b3e',sun:'f3e4b7',sunPos:[.76,.20],mist:'c4d0b8'},
 {sky:['63909d','d4d8bd'],far:'9fbcaf',near:'225548',sun:'fff0c4',sunPos:[.42,.10],mist:'d1dec4'},
 {sky:['676f7d','d5ae8c'],far:'b1aaa2',near:'263c40',sun:'f4c992',sunPos:[.71,.38],mist:'d4b5a0'},
 {sky:['111c30','49606b'],far:'4e6673',near:'0d2531',sun:'d7e0dc',sunPos:[.74,.18],mist:'8ea7aa'}
];
class Landscape {
 constructor(canvas,seed=813){this.canvas=canvas;this.ctx=canvas.getContext('2d',{alpha:false});this.seed=seed;this.day=0;this.layers=[];this.pointer=[0,0];this.zoom=0;this.wind=0;this.still=false;this.frozenState=null;this.lastState=null;this.visible=true;this.diagnostics={};this.resize();}
 resize(){const r=this.canvas.getBoundingClientRect();this.w=Math.max(1,Math.round(r.width));this.h=Math.max(1,Math.round(r.height));this.dpr=Math.min(devicePixelRatio||1,1.5);this.canvas.width=Math.round(this.w*this.dpr);this.canvas.height=Math.round(this.h*this.dpr);this.bake();}
 off(w=this.w,h=this.h){let c=document.createElement('canvas');c.width=w;c.height=h;return c;}
 setDay(day){if(this.day===day)return;this.day=clamp(day,0,3);this.bake();}
 bake(){const w=this.w,h=this.h,t=THEMES[this.day],random=rng(this.seed);this.layers=[];
  for(let l=0;l<8;l++){
   const c=this.off(),g=c.getContext('2d',{willReadFrequently:true}),ridge=[];const far=l<3;
   for(let x=0;x<=w+4;x+=3){let u=x/w;let peak=Math.exp(-Math.pow((u-.36-l*.014)/(.13+l*.017),2))*.24+Math.exp(-Math.pow((u-.58+l*.003)/(.12+l*.01),2))*.19;
    let y=(.61+l*.043-peak*(1-l*.085)+.018*Math.sin(u*16+l*1.6)+.008*Math.sin(u*39+l*.67)+.003*Math.cos(u*119+l)+.0015*Math.sin(u*319))*h;
    if(l>4){const e=(l-4)/3; y=(.79+l*.017 - e*(.28*Math.exp(-Math.pow((u+.05)/.3,2))+.26*Math.exp(-Math.pow((u-1.02)/.28,2))) + .012*Math.sin(u*35+l))*h;}
    ridge.push([x,y]);
   }
   g.beginPath();g.moveTo(-2,h+2);ridge.forEach(p=>g.lineTo(...p));g.lineTo(w+2,h+2);g.closePath();g.save();g.clip();
   const top=blend(t.far,t.near,(l+1)/8),bottom=blend(t.far,t.near,Math.min(1,(l+2)/8));const gr=g.createLinearGradient(0,h*.35,0,h);gr.addColorStop(0,top);gr.addColorStop(1,bottom);g.fillStyle=gr;g.fillRect(0,0,w,h);
   // Fine granular canopy, not straight strokes across the whole mountainside.
   for(let k=0;k<18000;k++){
    let x=random()*w,y=random()*h,yy=ridge[Math.min(ridge.length-1,Math.floor(x/3))][1];if(y<yy)continue;
    let slope=clamp((y-yy)/(h*.35)),size=(.3+random()*(1.15+l*.27))*(.7+slope*.6);
    g.fillStyle=random()>.52?`rgba(225,235,196,${.018+l*.004})`:`rgba(5,31,36,${.014+l*.005})`;
    g.beginPath();g.ellipse(x,y,size*1.45,size*.65,-.2,0,TAU);g.fill();
   }
   // Broad reflected light varies over valleys, avoiding a plastic striped surface.
   for(let j=0;j<6;j++){let x=w*(j*.18+random()*.05),yy=h*.57;let grad=g.createRadialGradient(x,yy,0,x,yy,w*.3);grad.addColorStop(0,'rgba(226,227,189,.015)');grad.addColorStop(1,'rgba(226,227,189,0)');g.fillStyle=grad;g.fillRect(0,0,w,h);}
   g.restore();
   // Individual treetops break the near-ridge silhouettes.
   if(l>3){g.fillStyle=top;for(let k=0;k<w/5;k++){let x=random()*w,pt=ridge[Math.min(ridge.length-1,Math.floor(x/3))],s=(1+random()*3.4)*(l/6);g.beginPath();g.ellipse(x,pt[1]-.6,s*1.2,s,0,0,TAU);g.fill();}}
   this.layers.push(c);
  }
  this.fog=this.off(1024,220);const f=this.fog.getContext('2d',{willReadFrequently:true}),rr=rng(718);for(let i=0;i<110;i++){let x=rr()*1200-80,y=85+rr()*90;let r=50+rr()*150;let gr=f.createRadialGradient(x,y,0,x,y,r);gr.addColorStop(0,'rgba(220,230,210,.042)');gr.addColorStop(1,'rgba(220,230,210,0)');f.fillStyle=gr;f.fillRect(x-r,y-r,r*2,r*2);}
  this.foliage=this.off();const fg=this.foliage.getContext('2d',{willReadFrequently:true});const leafR=rng(332);
  const branch=(x,y,len,ang,level)=>{if(level<=0)return;let X=x+Math.cos(ang)*len,Y=y+Math.sin(ang)*len;fg.strokeStyle=this.day===3?'#10232a':'#123437';fg.lineWidth=Math.max(.3,level*.75);fg.beginPath();fg.moveTo(x,y);fg.quadraticCurveTo((x+X)/2-9,(y+Y)/2,X,Y);fg.stroke();if(level<3){for(let j=0;j<14;j++){let ax=X+(leafR()-.5)*len*.8,ay=Y+(leafR()-.5)*len*.45;fg.fillStyle=blend(t.near,'173c36',leafR()*.3);fg.beginPath();fg.ellipse(ax,ay,2+leafR()*5,1.2+leafR()*2,ang+(leafR()-.5),0,TAU);fg.fill();}}branch(X,Y,len*.67,ang-.38-leafR()*.35,level-1);branch(X,Y,len*.69,ang+.3+leafR()*.4,level-1);};
  branch(-30,h*.96,w*.085,-.76,7);branch(w+35,h*.98,w*.075,-2.41,7);
  this.bakeAtmosphere();
 }
 bakeAtmosphere(){
  const {w,h}=this,t=THEMES[this.day],night=this.day===3;
  // Sky, stars and delicate cloud texture are prepared once per size/theme.
  this.sky=this.off();const g=this.sky.getContext('2d');
  const sky=g.createLinearGradient(0,0,0,h);sky.addColorStop(0,'#'+t.sky[0]);sky.addColorStop(.75,'#'+t.sky[1]);sky.addColorStop(1,'#'+t.far);g.fillStyle=sky;g.fillRect(0,0,w,h);
  const sx=w*t.sunPos[0],sy=h*t.sunPos[1],srad=Math.min(w,h)*.42,halo=g.createRadialGradient(sx,sy,0,sx,sy,srad);halo.addColorStop(0,night?'#d7e0dc16':'#f4e4bd42');halo.addColorStop(.4,night?'#d7e0dc08':'#f4e4bd18');halo.addColorStop(1,'#f4e4bd00');g.fillStyle=halo;g.fillRect(0,0,w,h);
  if(night){const r=rng(42);for(let i=0;i<95;i++){const a=r()*w,b=r()*h*.5;g.fillStyle=`rgba(234,239,224,${.15+r()*.6})`;g.fillRect(a,b,.7+r(),.7+r());}g.fillStyle='#dee3d5';g.beginPath();g.arc(sx,sy,9,0,TAU);g.fill();}

  this.cloud=this.off(768,128);const cg=this.cloud.getContext('2d'),cloudRandom=rng(583);
  for(let i=0;i<32;i++){const x=45+cloudRandom()*678,y=50+cloudRandom()*28,r=32+cloudRandom()*55;const gr=cg.createRadialGradient(x,y,0,x,y,r);gr.addColorStop(0,'#f2f0dc26');gr.addColorStop(.45,'#e4e7d712');gr.addColorStop(1,'#e4e7d700');cg.fillStyle=gr;cg.fillRect(x-r,y-r,r*2,r*2);}
  this.beam=this.off(192,640);const bg=this.beam.getContext('2d');
  // Layered soft shoulders instead of hard triangular edges or a bright fan.
  for(let i=6;i>0;i--){const spread=12+i*11,fade=bg.createLinearGradient(0,0,0,640);fade.addColorStop(0,'#fff2cf00');fade.addColorStop(.12,'#fff2cf10');fade.addColorStop(.43,'#fff2cf19');fade.addColorStop(1,'#fff2cf00');bg.fillStyle=fade;bg.beginPath();bg.moveTo(96-3-i,0);bg.lineTo(96+3+i,0);bg.lineTo(96+spread,640);bg.lineTo(96-spread,640);bg.closePath();bg.fill();}

  // Ten small rooted tufts, each made of four tapering, curved grass blades.
  // Sprites bend as a group around their roots; no blade paths are built per frame.
  this.grassSprites=[];
  const grassRandom=rng(846),dark=blend(t.near,'09282c',.36);
  for(let k=0;k<5;k++){const grass=this.off(100,150),gg=grass.getContext('2d');
   for(let j=0;j<4;j++){const root=47+grassRandom()*8,tip=12+grassRandom()*76,tipY=10+grassRandom()*65,curve=(tip-root)*.45;
    gg.fillStyle=dark;gg.beginPath();gg.moveTo(root-1.5,150);gg.bezierCurveTo(root+curve*.1,107,tip-curve,tipY+30,tip,tipY);gg.bezierCurveTo(tip-curve*.2,tipY+34,root+curve+3,110,root+2,150);gg.fill();
    if(!night){gg.strokeStyle='#afbb842b';gg.lineWidth=.7;gg.beginPath();gg.moveTo(root,149);gg.bezierCurveTo(root+curve*.2,104,tip-curve*.5,tipY+28,tip,tipY);gg.stroke();}
   }
   this.grassSprites.push(grass);
  }
  this.grassTufts=[.025,.115,.20,.33,.47,.58,.72,.83,.91,.98].map((x,i)=>({x,scale:[.78,.92,.49,.62,.43,.56,.48,.72,.62,.88][i],phase:i*1.79}));

  this.glow=this.off(64,64);const glow=this.glow.getContext('2d'),light=glow.createRadialGradient(32,32,0,32,32,32);light.addColorStop(0,'#fff7c7ff');light.addColorStop(.07,'#f7e59be8');light.addColorStop(.19,'#edce6875');light.addColorStop(.48,'#b6af5521');light.addColorStop(1,'#b6af5500');glow.fillStyle=light;glow.fillRect(0,0,64,64);
  const flyRandom=rng(936);this.fireflies=Array.from({length:w<650?9:12},(_,i)=>({x:.24+flyRandom()*.52,y:.75+flyRandom()*.135,phase:flyRandom()*TAU,speed:.25+flyRandom()*.24,size:17+flyRandom()*11,reflection:i%3!==0}));
  // A thin valley-floor water glimmer gives the reflections a physical surface.
  this.water=this.off();const wg=this.water.getContext('2d');wg.save();wg.translate(w*.50,h*.943);wg.scale(w*.30,h*.031);const water=wg.createRadialGradient(0,0,0,0,0,1);water.addColorStop(0,'#69868947');water.addColorStop(.6,'#4e74752b');water.addColorStop(1,'#4e747500');wg.fillStyle=water;wg.fillRect(-1,-1,2,2);wg.restore();
  for(let i=0;i<7;i++){const y=h*(.924+i*.0054),x=w*(.30+Math.sin(i*2.13)*.027),width=w*(.36-Math.abs(i-3)*.04);wg.strokeStyle=`rgba(135,164,159,${.07+(i%2)*.025})`;wg.lineWidth=.65;wg.beginPath();wg.moveTo(x,y);wg.quadraticCurveTo(x+width*.4,y-1,x+width,y);wg.stroke();}
 }
 drawSunlight(time,wind,near=false){
  if(this.day===3)return;const {ctx:g,w,h}=this,t=THEMES[this.day],sx=w*t.sunPos[0],sy=h*t.sunPos[1];
  g.save();if(near){g.beginPath();g.rect(0,h*.44,w,h*.44);g.clip();}
  g.globalCompositeOperation='screen';
  for(let i=0;i<4;i++){const breathing=.84+Math.sin(time*.09+i*.8)*.16;g.save();g.translate(sx+(i-1.5)*w*.011,sy-h*.04);g.rotate(.12+i*.10+Math.sin(time*.035+i)*.016+wind*.012);g.globalAlpha=(near?.19:.33)*breathing*(this.day===2?.72:1);const width=w*(.064+i*.010);g.drawImage(this.beam,-width/2,0,width,h*.82);g.restore();}
  g.restore();
 }
 drawClouds(time,wind){
  if(this.day===3)return;const {ctx:g,w,h}=this,t=THEMES[this.day];g.save();
  for(let i=0;i<3;i++){const drift=Math.sin(time*.028+i*1.7)*w*.032+wind*w*.008,cloudWidth=w*(.44+i*.08),x=w*(t.sunPos[0]-.29+i*.065)+drift,y=h*(t.sunPos[1]-.024+i*.056);g.globalAlpha=.19-i*.035;g.drawImage(this.cloud,x,y,cloudWidth,h*(.085+i*.012));}
  g.restore();
 }
 drawFireflies(time,wind){
  if(this.day!==3)return;const {ctx:g,w,h}=this;g.save();g.drawImage(this.water,0,0);g.globalCompositeOperation='screen';
  for(const fly of this.fireflies){const pulse=.34+.66*Math.pow((Math.sin(time*.73+fly.phase)+1)/2,2),x=fly.x*w+Math.sin(time*fly.speed+fly.phase)*12+wind*5,y=fly.y*h+Math.cos(time*fly.speed*.71+fly.phase)*7,size=fly.size*(w<650?.83:1);g.globalAlpha=pulse;g.drawImage(this.glow,x-size/2,y-size/2,size,size);
   // A subpixel sprite core disappears under the page's readability shade.
   // Keep the actual insect a tiny warm point, with the larger halo still soft.
   g.globalAlpha=.48+pulse*.5;g.fillStyle='#fff0b4';g.beginPath();g.arc(x,y,.7+pulse*.25,0,TAU);g.fill();
   if(fly.reflection){const yy=h*(.931+(fly.y-.75)*.16)+Math.sin(time*.27+fly.phase)*.7,ripple=3.5+pulse*2.5;g.globalAlpha=pulse*.60;g.drawImage(this.glow,x-size*.65,yy-2.5,size*1.3,5);g.fillStyle='#ead38f';g.fillRect(x-ripple/2,yy-.4,ripple,.8);g.globalAlpha=pulse*.30;g.drawImage(this.glow,x-size*.4+Math.sin(time*.6+fly.phase)*2,yy+3,size*.8,3);g.fillRect(x-ripple*.25+Math.sin(time*.6+fly.phase)*2,yy+4,ripple*.5,.65);}
  }
  g.restore();
 }
 drawGrass(time,wind){
  const {ctx:g,w,h}=this,baseHeight=Math.min(120,Math.max(64,h*.14));
  for(let i=0;i<this.grassTufts.length;i++){const tuft=this.grassTufts[i],height=baseHeight*tuft.scale,lean=Math.sin(time*.74+tuft.phase)*.018+Math.sin(time*.28+tuft.phase)*.012+wind*.12;g.save();g.translate(tuft.x*w,h+2);g.transform(1,0,-lean,1,0,0);g.rotate(lean*.22);g.globalAlpha=.86;g.drawImage(this.grassSprites[i%5],-height*.34,-height,height*.68,height);g.restore();}
 }
 render(time=0){if(!this.ctx)return;let {w,h,ctx:g,dpr}=this;
  if(this.still){if(!this.frozenState)this.frozenState=this.lastState||{time,pointer:[...this.pointer],zoom:this.zoom,wind:0};}
  else this.frozenState=null;
  const state=this.frozenState||{time,pointer:[...this.pointer],zoom:this.zoom,wind:clamp(Number(this.wind)||0,-1,1)};this.lastState=state;time=state.time;const wind=state.wind,pointer=state.pointer,zoom=state.zoom;
  Object.assign(this.diagnostics,{day:this.day,appliedWind:wind,grassTufts:10,grassBlades:40,sunlightShafts:this.day===3?0:4,thinClouds:this.day===3?0:3,fireflies:this.day===3?this.fireflies.length:0,reflections:this.day===3?this.fireflies.filter(f=>f.reflection).length:0,birdCount:this.day===3?0:9,frozenTime:time,still:!!this.still});
  g.setTransform(dpr,0,0,dpr,0,0);g.globalAlpha=1;g.globalCompositeOperation='source-over';g.drawImage(this.sky,0,0,w,h);
  this.drawSunlight(time,wind);this.drawClouds(time,wind);
  for(let i=0;i<this.layers.length;i++){let dx=pointer[0]*(i+1)*1.3+Math.sin(time*.025+i)*.5,dy=zoom*(i+1)*2;g.drawImage(this.layers[i],-5+dx,-3+dy,w+10,h+6);if(i===2||i===5){let y=h*(i===2?.58:.80),drift=Math.sin(time*.025+i)*w*.065+wind*w*(i===2?.010:.018);g.globalAlpha=i===2?.50:.25;g.drawImage(this.fog,-w*.2+drift,y-65+wind*(i===2?1.5:3),w*1.4,h*.22);g.globalAlpha=1;}if(i===2)this.drawSunlight(time,wind,true);}
  // Distant bird silhouettes move along separate paths, with articulated wings.
  if(this.day!==3){g.strokeStyle='#183a40b3';g.lineWidth=1.25;for(let i=0;i<9;i++){let phase=time*.028+i*.239,x=w*(.68+Math.sin(phase)*.11)+i*9,y=h*(.255+Math.cos(phase*1.2)*.05)+Math.sin(i*3.2)*17;let s=(1+i%3*.4)*(w<650?1.5:2.1),flap=Math.sin(time*(2.7+i*.08)+i)*s*.75;g.beginPath();g.moveTo(x-s*2,y-flap);g.quadraticCurveTo(x-s,y-s,x,y);g.quadraticCurveTo(x+s,y-s,x+s*2,y-flap);g.stroke();}}
  this.drawFireflies(time,wind);
  g.save();let sway=Math.sin(time*.28)*.0012+wind*.006;g.translate(w/2,h);g.rotate(sway);g.translate(-w/2,-h);g.drawImage(this.foliage,pointer[0]*2,0);g.restore();
  this.drawGrass(time,wind);
  let v=g.createLinearGradient(0,h*.85,0,h);v.addColorStop(0,'#0c2d3100');v.addColorStop(1,'#0c2d3155');g.fillStyle=v;g.fillRect(0,0,w,h);
 }
 dispose(){this.layers=[];this.fog=null;this.foliage=null;this.sky=null;this.cloud=null;this.beam=null;this.water=null;this.glow=null;this.grassSprites=[];this.grassTufts=[];this.fireflies=[];this.frozenState=null;this.lastState=null;}
}
window.AssyababLandscape=Landscape;
})();
