import numpy as np, json, os
from PIL import Image, ImageEnhance
from scipy import ndimage
a=np.array(Image.open('src/plants.png').convert('RGB')).astype(int)
r,g,b=a[...,0],a[...,1],a[...,2];mx=a.max(2);mn=a.min(2)
bg0=(mn>=246)&((mx-mn)<=6)
neutral=((mx-mn)<=10)&((b-r)>=-3)&(mx>=110)
cand=bg0|neutral
lab,k=ndimage.label(cand)
border=np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]]));border=border[border>0]
region=np.isin(lab,border)
alpha=np.full(mx.shape,255.0)
v=mx.astype(float)
sh=np.clip((250-v)/250*2.0,0,.45)
alpha[region]=sh[region]*255
rgb=a.copy().astype(np.uint8)
rgb[region]=np.stack([np.full(region.sum(),35)]*3,1)
img=np.dstack([rgb,alpha.astype(np.uint8)])
# components = solid (non-region) pixels
solid=~region
solid=ndimage.binary_opening(solid,iterations=1)
lab2,k2=ndimage.label(ndimage.binary_closing(solid,iterations=3))
objs=ndimage.find_objects(lab2);sz=ndimage.sum(solid,lab2,range(1,k2+1))
comps=[(i+1,objs[i]) for i in range(k2) if sz[i]>4000]
comps.sort(key=lambda c:(c[1][0].stop//340,c[1][1].start))
print(len(comps))
names=[]
for sp in ['petunia','lavanda']:names+= [f'{sp}_{i}' for i in range(3)]
for sp in ['suculenta','orquidea']:names+= [f'{sp}_{i}' for i in range(3)]
for sp in ['monstera','oliveira']:names+= [f'{sp}_{i}' for i in range(3)]
names.append('vazio')
os.makedirs('out',exist_ok=True);meta={}
F=.5
for n,(l,sl) in zip(names,comps):
    pad=30
    y0,y1=max(0,sl[0].start-6),min(a.shape[0],sl[0].stop+pad);x0,x1=max(0,sl[1].start-6),min(a.shape[1],sl[1].stop+pad)
    sub=img[y0:y1,x0:x1].copy()
    m=lab2[y0:y1,x0:x1]==l
    A=a[y0:y1,x0:x1];MX=A.max(2).astype(float);MN=A.min(2)
    ys0,_=np.where(m);top,bot=ys0.min(),ys0.max()
    sat=(MX-MN)/np.maximum(MX,1)
    rows=np.arange(MX.shape[0])[:,None]>=bot-(bot-top)*.3
    shad=rows&(sat<.16)&(MX>90)
    al=np.clip((250-MX)/250*2,0,.45)*255
    sub[...,3]=np.where(shad,np.minimum(sub[...,3],al),sub[...,3]).astype(np.uint8)
    for ch in range(3):sub[...,ch]=np.where(shad,35,sub[...,ch])
    m=m&~shad
    # keep shadow pixels near the object
    near=ndimage.binary_dilation(m,iterations=pad)
    sub[...,3]=np.where(near,sub[...,3],0)
    # anchor: pot bottom = lowest solid row; center x of solid in bottom 12% of solid rows
    ys,xs=np.where(m);yb=ys.max();sel=ys>=yb-(yb-ys.min())*.12
    ax=xs[sel].mean();
    p=Image.fromarray(sub,'RGBA');W,H=p.size
    p=p.resize((round(W*F),round(H*F)),Image.LANCZOS);p.save(f'out/pl_{n}.png',optimize=True)
    # sick variant
    rr,gg,bb,aa=p.split();rgb_=Image.merge('RGB',(rr,gg,bb));rgb_=ImageEnhance.Color(rgb_).enhance(.25);rgb_=Image.blend(rgb_,Image.new('RGB',rgb_.size,(150,120,60)),.25);rgb_.putalpha(aa);rgb_.save(f'out/pl_{n}_s.png',optimize=True)
    meta[n]=[p.size[0],p.size[1],round(ax*F,1),round(yb*F,1)]
    print(n,sl[1].start,sl[0].start,meta[n])
json.dump(meta,open('out/plmeta.json','w'))
prev=Image.new('RGBA',(1600,560),(70,60,45,255));x=y=10;rh=0
for n in names:
    p=Image.open(f'out/pl_{n}.png')
    if x+p.width>1590:x=10;y+=rh+10;rh=0
    prev.alpha_composite(p,(x,y));x+=p.width+8;rh=max(rh,p.height)
prev.save('/tmp/pl_prev.png')
