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
 constructor(canvas,seed=813){this.canvas=canvas;this.ctx=canvas.getContext('2d',{alpha:false});this.seed=seed;this.day=0;this.layers=[];this.pointer=[0,0];this.zoom=0;this.visible=true;this.resize();}
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
 }
 render(time=0){if(!this.ctx)return;let {w,h,ctx:g,dpr}=this,t=THEMES[this.day];g.setTransform(dpr,0,0,dpr,0,0);g.clearRect(0,0,w,h);
  let sky=g.createLinearGradient(0,0,0,h);sky.addColorStop(0,'#'+t.sky[0]);sky.addColorStop(.75,'#'+t.sky[1]);sky.addColorStop(1,'#'+t.far);g.fillStyle=sky;g.fillRect(0,0,w,h);
  let sx=w*t.sunPos[0],sy=h*t.sunPos[1],srad=Math.min(w,h)*.42,halo=g.createRadialGradient(sx,sy,0,sx,sy,srad);halo.addColorStop(0,this.day===3?'#d7e0dc16':'#f4e4bd42');halo.addColorStop(.4,this.day===3?'#d7e0dc08':'#f4e4bd18');halo.addColorStop(1,'#f4e4bd00');g.fillStyle=halo;g.fillRect(0,0,w,h);
  if(this.day===3){let r=rng(42);for(let i=0;i<95;i++){let a=r()*w,b=r()*h*.5;g.fillStyle=`rgba(234,239,224,${.15+r()*.6})`;g.fillRect(a,b,.7+r(),.7+r());}g.fillStyle='#dee3d5';g.beginPath();g.arc(sx,sy,9,0,TAU);g.fill();}
  for(let i=0;i<this.layers.length;i++){let dx=this.pointer[0]*(i+1)*1.3+Math.sin(time*.025+i)*.5,dy=this.zoom*(i+1)*2;g.drawImage(this.layers[i],-5+dx,-3+dy,w+10,h+6);if(i===2||i===5){let y=h*(i===2?.58:.80),drift=Math.sin(time*.025+i)*w*.065;g.globalAlpha=i===2?.50:.25;g.drawImage(this.fog,-w*.2+drift,y-65,w*1.4,h*.22);g.globalAlpha=1;}}
  // Distant bird silhouettes move along separate paths, with articulated wings.
  if(this.day!==3){g.strokeStyle='#183a40b3';g.lineWidth=1.25;for(let i=0;i<9;i++){let phase=time*.028+i*.239,x=w*(.68+Math.sin(phase)*.11)+i*9,y=h*(.255+Math.cos(phase*1.2)*.05)+Math.sin(i*3.2)*17;let s=(1+i%3*.4)*(w<650?1.5:2.1),flap=Math.sin(time*(2.7+i*.08)+i)*s*.75;g.beginPath();g.moveTo(x-s*2,y-flap);g.quadraticCurveTo(x-s,y-s,x,y);g.quadraticCurveTo(x+s,y-s,x+s*2,y-flap);g.stroke();}}
  g.save();let wind=Math.sin(time*.28)*.0012;g.translate(w/2,h);g.rotate(wind);g.translate(-w/2,-h);g.drawImage(this.foliage,this.pointer[0]*2,0);g.restore();
  let v=g.createLinearGradient(0,h*.85,0,h);v.addColorStop(0,'#0c2d3100');v.addColorStop(1,'#0c2d3155');g.fillStyle=v;g.fillRect(0,0,w,h);
 }
 dispose(){this.layers=[];this.fog=null;this.foliage=null;}
}
window.AssyababLandscape=Landscape;
})();
