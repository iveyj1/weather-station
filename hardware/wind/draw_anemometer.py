"""Regenerate drawings: QT_QPA_PLATFORM=offscreen FreeCADCmd hardware/wind/draw_anemometer.py
Requires FreeCAD and PySide6. Source model is opened read-only (never saved).
"""
from pathlib import Path
from html import escape
import FreeCAD as App
from PySide6 import QtCore, QtGui, QtSvg

ROOT = Path(__file__).resolve().parent
TOTAL_SHEETS = 4

class Sheet:
    def __init__(self, title, number, ox, oy, z0=0, scale=4):
        self.ox, self.oy, self.z0 = ox, oy, z0
        self.scale = scale
        self.items = ['<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 297 210">',
            '<rect width="297" height="210" fill="white"/>',
            '<defs><marker id="start" markerWidth="3" markerHeight="2" refX="0" refY="1" orient="auto" markerUnits="userSpaceOnUse"><path d="M3,0 L0,1 L3,2 Z" fill="#222"/></marker><marker id="arrow" markerWidth="3" markerHeight="2" refX="3" refY="1" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L3,1 L0,2 Z" fill="#222"/></marker></defs>',
            '<style>text{font-family:DejaVu Sans,sans-serif;font-size:3.2px;fill:#111} .dim{stroke:#333;stroke-width:.18;fill:none} .edge{stroke:#111;stroke-width:.5;fill:none} .axis{stroke:#267296;stroke-width:.25;stroke-dasharray:6,1.5,1,1.5;fill:none}</style>']
        self.items.append('<rect x="8" y="8" width="281" height="194" fill="none" stroke="#333" stroke-width=".25"/>')
        self.text(14,16,'ANEMOMETER / '+title, size=5)
        self.text(14,23,'XZ plane • viewed along −Y • positive X half-profile')
        self.line(8,193,289,193)
        self.text(14,199,f'Source: anemometer.FCStd | Dimensions: mm | Scale {scale}:1 at A4 landscape')
        self.text(280,199,f'{number} / {TOTAL_SHEETS}',anchor='end')
    def xy(self,x,z): return self.ox+self.scale*x,self.oy-self.scale*(z-self.z0)
    def line(self,x1,y1,x2,y2,cls='dim',extra=''):
        self.items.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}" {extra}/>')
    def text(self,x,y,text,size=3.2,anchor='start',rotate=None):
        trans='' if rotate is None else f' transform="rotate({rotate},{x},{y})"'
        self.items.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" style="font-size:{size}px"{trans}>{escape(text)}</text>')
    def h(self,a,b,y,label):
        x1,y1=self.xy(*a);x2,y2=self.xy(*b)
        for x,yy in [(x1,y1),(x2,y2)]: self.line(x,yy,x,y+(-2 if y<yy else 2))
        self.line(x1,y,x2,y,extra='marker-start="url(#start)" marker-end="url(#arrow)"')
        self.text((x1+x2)/2,y-1.5,label,anchor='middle')
    def v(self,a,b,x,label):
        x1,y1=self.xy(*a);x2,y2=self.xy(*b)
        for xx,y in [(x1,y1),(x2,y2)]: self.line(xx,y,x+(-2 if x<xx else 2),y)
        self.line(x,y1,x,y2,extra='marker-start="url(#start)" marker-end="url(#arrow)"')
        self.text(x-1.5,(y1+y2)/2,label,anchor='middle',rotate=-90)
    def leader(self,p,x,y,label):
        px,py=self.xy(*p)
        self.line(px,py,x-3,y-1,extra='marker-start="url(#start)"')
        self.text(x,y,label)
    def profile(self,sketch):
        placement=sketch.getGlobalPlacement()
        for i,g in enumerate(sketch.Geometry):
            if sketch.getConstruction(i): continue
            if not hasattr(g,'StartPoint'): raise ValueError('Expected line geometry')
            a,b=placement.multVec(g.StartPoint),placement.multVec(g.EndPoint)
            assert abs(a.y)<1e-8 and abs(b.y)<1e-8
            self.line(*self.xy(a.x,a.z),*self.xy(b.x,b.z),cls='edge')
    def axis(self,top,bottom):
        self.line(self.ox,bottom,self.ox,top,'axis')
        self.line(self.ox,top+5,self.ox,top,extra='marker-end="url(#arrow)"')
        self.text(self.ox-3,top-2,'+Z',anchor='end')
        self.text(self.ox-7,(top+bottom)/2,'Z — AXIS OF ROTATION',anchor='middle',rotate=-90)
    def notes(self,lines):
        for i,line in enumerate(lines): self.text(184,145+i*6,line,size=3)
    def save(self,name):
        path=ROOT/name
        path.write_text('\n'.join(self.items+['</svg>']))
        return path

doc=App.openDocument(str(ROOT/'anemometer.FCStd'))
sketches=[o for o in doc.Objects if o.TypeId=='Sketcher::SketchObject']
assert len(sketches)==TOTAL_SHEETS, 'Update drawing layouts for new sketches'
a,b,c,d=[doc.getObject(n) for n in ['Sketch','Sketch001','Sketch002','Sketch003']]
def point(sketch,index,end=False):
    g=sketch.Geometry[index]
    p=sketch.getGlobalPlacement().multVec(g.EndPoint if end else g.StartPoint)
    return p.x,p.z

def hd(sheet,p,q,y,ref=False):
    sheet.h(p,q,y,f'{abs(q[0]-p[0]):.3f}'.rstrip('0').rstrip('.')+(' (REF)' if ref else ''))
def vd(sheet,p,q,x,ref=False):
    sheet.v(p,q,x,f'{abs(q[1]-p[1]):.3f}'.rstrip('0').rstrip('.')+(' (REF)' if ref else ''))

z=point(a,0)[1]
s=Sheet(a.Label,1,90,170,z)
s.profile(a);s.axis(42,182)
hd(s,point(a,2,True),point(a,2),39)
hd(s,point(a,0),point(a,6),184)
hd(s,point(a,5,True),point(a,5),83)
vd(s,point(a,1),point(a,1,True),62)
vd(s,point(a,4),point(a,4,True),133)
vd(s,point(a,0,True),point(a,9,True),146)
vd(s,point(a,6),point(a,6,True),158)
s.leader((2,z+25),184,66,'SHAFT')
s.leader((5.5,z+15.5),184,82,'COLLAR')
s.leader((8,z+8.5),184,110,'BEARING')
s.notes(['Horizontal dimensions are radial.', 'Collar and bearing meet: no axial gap.', f'Lower end: Z = {z:.3f} (REF).', 'Axial position is unconstrained in source.', 'No tolerances specified in source.'])
paths=[s.save('anemometer-collar-bearing.svg')]
s=Sheet(b.Label,2,80,178)
s.profile(b);s.axis(39,185)
hd(s,point(b,0),point(b,2),32)
hd(s,point(b,2),point(b,2,True),32)
hd(s,point(b,6),point(b,6,True),188,True)
hd(s,point(b,5),point(b,5,True),108)
vd(s,point(b,3),point(b,3,True),163)
vd(s,point(b,7),point(b,7,True),59)
vd(s,point(b,4),point(b,4,True),110)
s.notes(['Horizontal dimensions are radial,', 'not diameters.', 'Base lies at Z = 0.', 'REF = derived/reference dimension.', 'No tolerances specified in source.'])
paths.append(s.save('anemometer-base.svg'))

z=point(c,2,True)[1]
s=Sheet(c.Label,3,80,110,z,scale=8)
s.profile(c);s.axis(64,135)
hd(s,point(c,0),point(c,0,True),86)
vd(s,point(c,1),point(c,1,True),170)
s.leader((4.75,z+.8),184,74,'PCB')
s.notes(['Horizontal dimension is radial.', f'Lower face: Z = {z:.3f} (REF).', 'Axial position is unconstrained in source.', 'No tolerances specified in source.'])
paths.append(s.save('anemometer-pcb.svg'))

z=point(d,1)[1]
s=Sheet(d.Label,4,65,177,z,scale=3)
s.profile(d);s.axis(39,185)
hd(s,point(d,3,True),point(d,3),32)
hd(s,point(d,1),point(d,1,True),188)
hd(s,point(d,5),point(d,5,True),100)
hd(s,point(d,7),point(d,7,True),112)
vd(s,point(d,4),point(d,4,True),46)
vd(s,point(d,8),point(d,8,True),99)
vd(s,point(d,2),point(d,2,True),153,True)
s.notes(['Horizontal dimensions are radial.', 'REF = measured/reference dimension.', f'Lower end: Z = {z:.3f} (REF).', 'Overall height and axial position', 'are unconstrained in source.', 'No tolerances specified in source.'])
paths.append(s.save('anemometer-sketch003.svg'))
# Render the same vector sheets into a four-page, full-size PDF.
app=QtGui.QGuiApplication.instance() or QtGui.QGuiApplication([])
writer=QtGui.QPdfWriter(str(ROOT/'anemometer-drawings.pdf'))
writer.setPageSize(QtGui.QPageSize(QtGui.QPageSize.A4))
writer.setPageOrientation(QtGui.QPageLayout.Landscape)
writer.setPageMargins(QtCore.QMarginsF(0,0,0,0))
writer.setResolution(254)
writer.setTitle('Anemometer — dimensioned sketch profiles')
painter=QtGui.QPainter(writer)
for i,path in enumerate(paths):
    if i: writer.newPage()
    renderer=QtSvg.QSvgRenderer(str(path))
    assert renderer.isValid()
    renderer.render(painter,QtCore.QRectF(0,0,writer.width(),writer.height()))
painter.end()
App.closeDocument(doc.Name)
print(f'Created {len(paths)} SVG sheets and anemometer-drawings.pdf')
