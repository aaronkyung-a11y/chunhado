import sys, os
from PIL import Image, ImageDraw, ImageFont
indir=sys.argv[1]; out=sys.argv[2]; keys=sys.argv[3].split(',') if len(sys.argv)>3 and sys.argv[3] else None
files=sorted(f for f in os.listdir(indir) if f.endswith('.png'))
if keys: files=[k+'.png' for k in keys if os.path.exists(os.path.join(indir,k+'.png'))]
n=len(files); cols=4; cell=256
rows=(n+cols-1)//cols
sheet=Image.new('RGB',(cols*cell,rows*(cell+18)),(120,120,130))
d=ImageDraw.Draw(sheet)
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
for i,fn in enumerate(files):
    im=Image.open(os.path.join(indir,fn)).convert('RGBA').resize((cell,cell),Image.LANCZOS)
    x=(i%cols)*cell; y=(i//cols)*(cell+18)
    sheet.paste(im,(x,y),im)
    d.text((x+4,y+cell+2),fn[:-4],fill=(255,255,255),font=f)
sheet.save(out,quality=85)
print(n,'files')
