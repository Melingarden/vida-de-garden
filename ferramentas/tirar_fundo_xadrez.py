import numpy as np
from PIL import Image
from scipy import ndimage
im=np.array(Image.open('src/objs.png').convert('RGB')).astype(int)
mx=im.max(2);mn=im.min(2);sat=(mx-mn)/np.maximum(mx,1)
bgm=(sat<.07)&(mx>212)
lab,k=ndimage.label(bgm)
H,W=bgm.shape
border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
sizes=ndimage.sum(bgm,lab,range(1,k+1))
remove=np.zeros(k+1,bool)
for i in range(1,k+1):
    if i in border or sizes[i-1]>150: remove[i]=True
alpha=np.where(remove[lab],0,255).astype(np.uint8)
# soften: erode alpha edge by 1 to remove light halo
al=ndimage.binary_erosion(alpha>0,iterations=1)
out=np.dstack([im.astype(np.uint8),(al*255).astype(np.uint8)])
Image.fromarray(out,'RGBA').save('objs_alpha.png')
# components
a=ndimage.binary_closing(al,iterations=2)
lab2,k2=ndimage.label(a);objs=ndimage.find_objects(lab2);sz=ndimage.sum(a,lab2,range(1,k2+1))
comps=[(i+1,objs[i],int(sz[i])) for i in range(k2) if sz[i]>3000]
comps.sort(key=lambda c:(c[1][0].start//230,c[1][1].start))
for i,(l,sl,s) in enumerate(comps):print(i,'x',sl[1].start,sl[1].stop,'y',sl[0].start,sl[0].stop,s)
