import numpy as np, json
from PIL import Image
from scipy import ndimage
names={'front':['head','torso','armL','armR','legL','legR','can'],'back':['head','torso','armL','armR','legL','legR'],'side':['head','torso','arm','leg']}
import os;os.makedirs('parts',exist_ok=True)
meta={}
for n,lst in names.items():
    im=np.array(Image.open(f'src/{n}.png'))
    a=im[...,3]>40
    a2=ndimage.binary_closing(a,iterations=2)
    lab,k=ndimage.label(a2)
    objs=ndimage.find_objects(lab);sizes=ndimage.sum(a2,lab,range(1,k+1))
    comps=[(i+1,objs[i]) for i in range(k) if sizes[i]>2000]
    comps.sort(key=lambda c:(c[1][0].start//300,c[1][1].start))
    for name,(l,sl) in zip(lst,comps):
        m=ndimage.binary_dilation(lab==l,iterations=3)
        sub=im[sl[0].start-3 if sl[0].start>=3 else 0:sl[0].stop+3,sl[1].start-3 if sl[1].start>=3 else 0:sl[1].stop+3].copy()
        mm=m[sl[0].start-3 if sl[0].start>=3 else 0:sl[0].stop+3,sl[1].start-3 if sl[1].start>=3 else 0:sl[1].stop+3]
        sub[...,3]=np.where(mm,sub[...,3],0)
        Image.fromarray(sub).save(f'parts/{n}_{name}.png')
        meta[f'{n}_{name}']=sub.shape[1::-1]
print(json.dumps(meta))
json.dump(meta,open('parts/meta.json','w'))
