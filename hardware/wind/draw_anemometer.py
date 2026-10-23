"""Regenerate drawings: QT_QPA_PLATFORM=offscreen FreeCADCmd hardware/wind/draw_anemometer.py
Requires FreeCAD and PySide6. Source model is opened read-only (never saved).
"""
from pathlib import Path
from html import escape
import FreeCAD as App
from PySide6 import QtCore, QtGui, QtSvg

ROOT = Path(__file__).resolve().parent
SCALE = 4

class Sheet:
    def __init__(self, title, number, ox, oy, z0=0):
        self.ox, self.oy, self.z0 = ox, oy, z0
        self.items = ['<svg xmlns="http://www.w3.org/2000/svg" width="297mm" height="210mm" viewBox="0 0 297 210">',
            '<rect width="297" height="210" fill="white"/>',
            '<defs><marker id="arrow" markerWidth="3" markerHeight="2" refX="0" refY="1" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M3,0 L0,1 L3,2 Z" fill="#222"/></marker></defs>',
            '<style>text{font-family:DejaVu Sans,sans-serif;font-size:3.2px;fill:#111} .dim{stroke:#333;stroke-width:.18;fill:none} .edge{stroke:#111;stroke-width:.5;fill:none} .axis{stroke:#267296;stroke-width:.25;stroke-dasharray:6,1.5,1,1.5;fill:none}</style>']
        self.items.append('<rect x="8" y="8" width="281" height="194" fill="none" stroke="#333" stroke-width=".25"/>')
        self.text(14,16,'ANEMOMETER / '+title, size=5)
        self.text(14,23,'XZ plane • viewed along −Y • positive X half-profile')
        self.line(8,193,289,193)
        self.text(14,199,'Source: anemometer.FCStd | Dimensions: mm | Scale 4:1 at A4 landscape')
        self.text(280,199,f'{number} / 2',anchor='end')
    def xy(self,x,z): return self.ox+SCALE*x,self.oy-SCALE*(z-self.z0)
    def line(self,x1,y1,x2,y2,cls='dim',extra=''):
        self.items.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="{cls}" {extra}/>')
    def text(self,x,y,text,size=3.2,anchor='start',rotate=None):
        trans='' if rotate is None else f' transform="rotate({rotate},{x},{y})"'
        self.items.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" style="font-size:{size}px"{trans}>{escape(text)}</text>')
    def h(self,a,b,y,label):
        x1,y1=self.xy(*a);x2,y2=self.xy(*b)
        for x,yy in [(x1,y1),(x2,y2)]: self.line(x,yy,x,y+(-2 if y<yy else 2))
        self.line(x1,y,x2,y,extra='marker-start="url(#arrow)" marker-end="url(#arrow)"')
        self.text((x1+x2)/2,y-1.5,label,anchor='middle')
    def v(self,a,b,x,label):
        x1,y1=self.xy(*a);x2,y2=self.xy(*b)
        for xx,y in [(x1,y1),(x2,y2)]: self.line(xx,y,x+(-2 if x<xx else 2),y)
        self.line(x,y1,x,y2,extra='marker-start="url(#arrow)" marker-end="url(#arrow)"')
        self.text(x-1.5,(y1+y2)/2,label,anchor='middle',rotate=-90)
    def leader(self,p,x,y,label):
        px,py=self.xy(*p)
        self.line(px,py,x-3,y-1,extra='marker-start="url(#arrow)"')
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
a=doc.getObject('Sketch'); b=doc.getObject('Sketch001')
z=min(g.StartPoint.y for g in a.Geometry)
s=Sheet(a.Label,1,90,160,z)
s.profile(a);s.axis(50,174)
s.h((0,z+25),(4,z+25),48,'4')
s.h((0,z+25),(11,z+7.9),36,'11')
s.h((4,z+15),(7,z+15),88,'3')
s.v((0,z),(0,z+25),62,'25')
s.v((7,z+8),(7,z+15),133,'7')
s.v((4,z),(4,z+8),146,'8')
s.v((11,z+.9),(11,z+7.9),158,'7')
s.leader((2,z+20),184,66,'SHAFT')
s.leader((5.5,z+12),184,82,'COLLAR')
s.leader((8,z+4),184,98,'BEARING')
s.leader((6,z+7.95),184,120,'0.1 axial gap')
s.notes(['All horizontal dimensions are radial,', 'measured from Z or between edges.', 'Shown geometry only; no solid inferred.', f'Lower end: Z = {z:.3f} (REF).', 'Axial position is unconstrained in source.', 'No tolerances specified in source.'])
paths=[s.save('anemometer-collar-bearing.svg')]
s=Sheet(b.Label,2,80,178)
s.profile(b);s.axis(39,185)
s.h((0,3),(11.2,34),32,'11.2')
s.h((11.2,34),(15.2,34),32,'4')
s.h((0,0),(15.2,0),188,'15.2 (REF)')
s.h((9.7,5),(11.2,5),149,'1.5')
s.v((15.2,0),(15.2,34),163,'34')
s.v((0,0),(0,3),59,'3')
s.v((9.7,3),(9.7,5),110,'2')
s.notes(['All horizontal dimensions are radial,', 'not diameters.', 'Base lies at Z = 0.', 'REF = derived/reference dimension.', 'No tolerances specified in source.'])
paths.append(s.save('anemometer-hub.svg'))
# Render the same vector sheets into a two-page, full-size PDF.
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
print('Created two SVG sheets and anemometer-drawings.pdf')
