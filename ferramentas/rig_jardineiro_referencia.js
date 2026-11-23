/* ---------- jardineiro: cut-out puppet from the user's drawings ---------- */
const RIG_META={"front_head":[585,516],"front_torso":[351,447],"front_armL":[193,365],"front_armR":[190,365],"front_legL":[201,418],"front_legR":[204,416],"front_can":[519,360],"back_head":[554,532],"back_torso":[328,451],"back_armL":[196,368],"back_armR":[197,368],"back_legL":[205,421],"back_legR":[204,421],"side_head":[647,611],"side_torso":[355,549],"side_arm":[168,443],"side_leg":[272,508],"side_arm_dk":[168,443],"side_leg_dk":[272,508]};
const RIG_IMG={};let RIG_OK=0;
function rigLoad(){const ks=Object.keys(RIG_META);ks.forEach(k=>{const im=new Image();im.onload=()=>{if(++RIG_OK===ks.length)SPRV++};im.src='sprites/'+k+'.png';RIG_IMG[k]=im})}
const rigReady=()=>RIG_OK===Object.keys(RIG_META).length;
function part(k,px,py,x,y,rot,sx,sy){const[w,h]=RIG_META[k];c.save();c.translate(x,y);if(rot)c.rotate(rot);if(sx||sy)c.scale(sx||1,sy||1);c.drawImage(RIG_IMG[k],-px,-py,w,h);c.restore()}
function rigCarry(it,x,y,flip){
  if(!it)return;
  if(it.kind==='can'){c.save();c.translate(x,y);if(flip)c.scale(-1,1);part('front_can',150,60,0,0,0,.62,.62);c.restore();return}
  if(it.kind==='plant'&&it.p){c.save();c.translate(x,y);c.scale(20,20);plantAt(it.p,0,8,21);c.restore();return}
  c.save();c.translate(x,y);c.scale(18,18);
  if(it.kind==='spray'){RR(-2.2,-6,4.4,9,1.2,'#f4f6f1');RR(-1.4,-8.5,2.8,2.8,1,'#2f9e44')}
  else if(it.kind==='sack'){RR(-5.5,-6,11,11,3,'#9b7449')}
  else if(it.kind==='tray'){RR(-8,-2,16,5,1.5,'#2c2c2c');[-5,0,5].forEach(x=>{L(x,-2,x,-5,'#4f9a3a',1.2);O(x,-5.5,1.6,'#6fbf4a')})}
  c.restore();
}
function drawRig(w){
  const dx=Math.cos(w.dir),dy=Math.sin(w.dir),f=Math.abs(dy)>=Math.abs(dx)*.8?(dy>0?'d':'u'):(dx>0?'r':'l');
  const mv=w.moving?1:0,ph=w.walk*.23,s1=Math.sin(ph)*mv,bob=Math.abs(Math.sin(ph))*mv,t=performance.now()/1000,breath=1+Math.sin(t*2.2+w.x)*.015;
  const S0=52/1141,sc=S0*(w.sc||1);
  c.save();c.translate(w.x,Y(w.y));
  E(0,0,11*(w.sc||1),4*(w.sc||1),0,'rgba(0,0,0,.24)');
  c.scale(sc,sc);c.translate(0,-bob*26);
  const carry=w.carry,watering=w.anim==='water';
  if(f==='d'||f==='u'){
    const v=f==='d'?'front':'back',lift=a=>-Math.max(0,a)*46;
    part(v+'_legL',100,35,-62,-383+lift(s1),s1*.08,1,1);
    part(v+'_legR',102,35,62,-383+lift(-s1),-s1*.08,1,1);
    const can=carry&&carry.kind==='can',aL=carry&&!can?-.45:.12*s1+.04,aR=can?.3:carry?.45:.12*s1-.04;
    part(v+'_armL',RIG_META[v+'_armL'][0]*.62,32,-150,-602,aL,1,1);
    part(v+'_armR',RIG_META[v+'_armR'][0]*.38,32,150,-602,aR,1,1);
    if(f==='u')rigCarry(carry,can?60:0,can?-330:-430,false);
    const[tw,th]=RIG_META[v+'_torso'];part(v+'_torso',tw/2,th,0,-268,0,1,breath);
    if(f==='d')rigCarry(carry,can?60:0,can?-300:-400,false);
    const[hw,hh_]=RIG_META[v+'_head'];part(v+'_head',hw/2,hh_,0,-268-th*breath+(f==='d'?95:75),Math.sin(t*1.7+w.y)*.02*(1-mv),1,1);
  }else{
    if(f==='l')c.scale(-1,1);
    c.scale(.83,.83);
    const A=.5*s1,armR=watering?-1.25:carry?-.9:-.55*s1;
    part('side_arm_dk',84,34,-8,-760,.55*s1,1,1);
    part('side_leg_dk',92,40,-10,-468,-A,1,1);
    part('side_leg',92,40,12,-468,A,1,1);
    const[tw,th]=RIG_META.side_torso;part('side_torso',tw*.5,th,0,-318,0,1,breath);
    const[hw,hh_]=RIG_META.side_head;part('side_head',hw*.52,hh_,10,-318-th*breath+120,Math.sin(t*1.7+w.y)*.02*(1-mv),1,1);
    part('side_arm',84,34,22,-760,armR,1,1);
    if(carry){const ax=22+Math.sin(-armR)*370,ay=-760+Math.cos(armR)*370;rigCarry(carry,ax+(carry.kind==='can'?40:0),ay+(carry.kind==='can'?-20:-30),false)}
  }
  c.restore();
}
