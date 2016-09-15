
# -*- coding: utf-8 -*-
'''
Generates Inkscape SVG file containing box components needed to 
laser cut a tabbed construction box taking kerf and clearance into account

Copyright (C) 2016 Apple Muncy j.apple.muncy@gmail.com

Copyright (C) 2011 elliot white   elliot@twot.eu
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import math
import sys,inkex,simplestyle,gettext
import math


def drawS(XYstring, parent):         # Draw lines from a list
    name='part'
    style = { 'stroke': '#000000', 'fill': 'none' }
    drw = {'style':simplestyle.formatStyle(style),inkex.addNS('label','inkscape'):name,'d':XYstring}
    inkex.etree.SubElement(parent, inkex.addNS('path','svg'), drw )
    return

def drawArc(r, (cx , cy ), start , end, parent):


# http://wiki.inkscape.org/wiki/index.php/Generating_objects_from_extensions
#   
    style = { 'stroke': '#000000', 'stroke-width': '1', 'fill': 'none' }
    ell_attribs = {'style':simplestyle.formatStyle(style),
        inkex.addNS('cx','sodipodi')        :str(cx),
        inkex.addNS('cy','sodipodi')        :str(cy),
        inkex.addNS('rx','sodipodi')        :str(r),
        inkex.addNS('ry','sodipodi')        :str(r),
        inkex.addNS('start','sodipodi')     :str(start),
        inkex.addNS('end','sodipodi')       :str(end),
        inkex.addNS('open','sodipodi')      :'true', #all ellipse sectors we will draw are open
        inkex.addNS('type','sodipodi')      :'arc',
        'transform'                         :'' }
    inkex.etree.SubElement(parent, inkex.addNS('path','svg'), ell_attribs )

def drawCircle(r, (cx, cy), parent):
    drawArc(r, (cx,cy), 0 , 2*math.pi, parent)

def appendScript(parent,x,y, text):
    super = inkex.etree.SubElement(parent, inkex.addNS('text', 'svg'), 
            {'style':'font-size:200%' , 'fill':'red' , 'x':'{0}'.format(x) , 'y':'{0}'.format(y)})
    super.text = text

def cutoutArea(  (centerLnX , centerLnY) , ( dX , dY) ,parent,  cornerR = 0.0 ):
    ''' draws a cutout opening given two centerlines, length and width, and corner radius)
    '''

    
    x0,y0 =  centerLnX -dX  , centerLnY -dY 
    x1,y1 = centerLnX -dX + cornerR  , centerLnY -dY +cornerR 
    x2,y2 = centerLnX + dX - cornerR  , centerLnY +dY -cornerR 
    x3,y3 = centerLnX + dX , centerLnY +dY

    S='M '+str(x1)+','+str(-y0)+' '
    S+='L '+str(x2) +','+str( -y0) +' '
    S+='M '+str(x3)+','+str(-y1)+' '
    S+='L '+str(x3) +','+str( -y2) +' '
    S+='M '+str(x2)+','+str(-y3)+' '
    S+='L '+str(x1) +','+str( -y3) +' '
    S+='M '+str(x0)+','+str(-y2)+' '
    S+='L '+str(x0) +','+str( -y1) +' '

    drawS(S , parent)
    drawArc(cornerR, (x2 , -y1 ), 0 , math.pi/2, parent)
    drawArc(cornerR, (x1 , -y1 ), math.pi/2 , math.pi, parent)
    drawArc(cornerR, (x1 , -y2 ), math.pi , 3*math.pi/2, parent)
    drawArc(cornerR, (x2 , -y2 ), 3*math.pi/2 , 0, parent)

def draw_nema((x,y), my_dict):
    bearing_diameter = my_dict['bearing_diameter']
    slot_length = my_dict['slot_length']
    parent = my_dict['parent']
    screw_offset = my_dict['screw_offset']
    screw_r = my_dict['screw_diameter']/2
    cutoutArea((x,y), (bearing_diameter/2 , slot_length + bearing_diameter/2) , parent , bearing_diameter/2)
    cutoutArea((x+screw_offset ,y+screw_offset ), (screw_r  , slot_length + screw_r ) , parent ,screw_r )
    cutoutArea((x-screw_offset ,y+screw_offset ), (screw_r  , slot_length + screw_r ) , parent
            ,screw_r )   
    cutoutArea((x+screw_offset ,y-screw_offset ), (screw_r  , slot_length +
                screw_r ) , parent ,screw_r )    
    cutoutArea((x-screw_offset ,y-screw_offset ), (screw_r  , slot_length + screw_r ) , parent ,screw_r )    

def draw_bearing((x,y), my_dict):
        drawCircle(my_dict['bearing_diameter']/2,(x,-y),my_dict['parent'])
        drawCircle(my_dict['screw_diameter']/2,(x - my_dict['screw_offset'],-y),my_dict['parent'])
        drawCircle(my_dict['screw_diameter']/2,(x + my_dict['screw_offset'],-y),my_dict['parent'])



def drill(center, diameter, n_pt):
    from math import sin, cos, pi
    center = Vec2(center)
    radius = diameter / 2.
    out = Vec2([1, 0])
    up = Vec2([0, 1])
    path = Path([center + out * radius])
    dtheta = (2 * pi) / n_pt
    for k in range(n_pt + 1):
        path.append(center + out * radius * cos(k * dtheta) + up * radius * sin(k * dtheta))
    return path
  
def t_slot(center, orient, thickness, screw_length, screw_diameter, nut_diameter, nut_height ):
    '''
    make one t-slot starting 
              __
             |  |
  -----------+  +-----+      ------
                      |        ^
  x center            |   screw_diameter  x----------------------> orient
                      |        v

  -----------+  +-----+      ------
             |  |
              --
    '''
 
    orient = orient*(screw_length - thickness -nut_height  )


    orient = Vec2(orient)
    out = orient / orient.norm() 
    up = Vec2([out[1], -out[0]])
    center = Vec2(center)
    screw_r = screw_diameter / 2.
    nut_r = nut_diameter / 2.
    nut_w = screw_diameter
    #nut_w = nut_height
    path = Path([center + up * screw_r])
    path.append_from_last(orient  )
    path.append_from_last(up * (nut_r - screw_r))
    path.append_from_last(out *  nut_height  )
    path.append_from_last(-up * (nut_r - screw_r))
    path.append_from_last(out * (nut_height/4))
    path.append_from_last(-up * screw_r)
    path.extend(path.reflect(center, up).reverse())
    return path


class Vec2:
    '''
    There be dragons here!
    A class providing a 2 dimensional vector space.

    '''
    def __init__(self, x, y=None):
        if y is None:
            y = x[1]

            x = x[0]
        self.x = x
        self.y = y

    def norm(self):
        '''
        returns the scaler of Vec2.self
        '''
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __getitem__(self, idx):
        return [self.x, self.y][idx]
    def __neg__(self):
        return Vec2(-self.x, -self.y)
    def __add__(self, other):
        return Vec2(self.x + other[0], self.y + other[1])
    def __sub__(self, other):
        return self + [-other[0], -other[1]]
    def __mul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)
    def __div__(self, scalar):
        return Vec2(self.x / scalar, self.y / scalar)
    def dot(self, other):
        return self.x * other[0] + self.y * other[1]
    def inner(self, other):
        return self.dot(other)
    def outer(self, other):
        return [[self[0] * other[0], self[0] * other[1]],
                [self[1] * other[0], self[1] * other[1]]]
    def __repr__(self):
        return 'Vec2(%s, %s)' % (self.x, self.y)
    def toXY(self):
        return '%s,%s ' % (self.x, self.y)

def mat_x_vec(mat, vec):
    return Vec2(vec.dot(mat[0]), vec.dot(mat[1]))

def sign(x):
    return 1 if x > 0 else -1

class Path:
    def __init__(self, path=()):
        self.path = [Vec2(p) for p in path]
    def append(self, point):
        self.path.append(Vec2(point))
    def rotate(self, center, angle):
        '''
        angle in degrees
        '''
        from math import cos, sin
        angle *= math.pi / 180.
        R = [[cos(angle), -sin(angle)],
            [sin(angle),  cos(angle)]]
        out = [mat_x_vec(R, p - center) + center for p in self.path]
        return Path(out)
    def translate(self, vec):
        return Path([p + vec for p in self.path])
    def append_from_last(self, v):
        self.path.append(self.path[-1] + v)
    def extend(self, points):
        self.path.extend(points)
    def __getitem__(self, idx):
        return self.path[idx]
    def reflect(self, center, orient):
        out = self.translate(-center)
        R = Vec2(orient).outer(orient)
        R = [[1 - 2 * R[0][0], 2 * R[0][1]],
             [2 * R[1][0], 1 - 2 * R[1][1]]]
        out = Path([mat_x_vec(R, p) for p in out])
        out = out.translate(center)
        return out
    def reverse(self):
        return Path(self.path[::-1])
    def drawXY(self):
        XYstring = 'M ' + 'L '.join([p.toXY() for p in self.path])
        return XYstring
    def plot(self, lt='-'):
        from pylab import plot
        xs = [l.x for l in self.path]
        ys = [l.y for l in self.path]
        plot(xs, ys, lt)


      
      
def Vec2__test__():
    v1 = Vec2(1, 1)
    assert abs(v1.norm() - math.sqrt(2)) < 1e-8
    assert abs(-v1[0] + 1) < 1e-8
    assert abs((v1 + v1)[0] - 2) < 1e-8
    assert abs((v1 - v1)[0] - 0) < 1e-8
    assert abs((v1 + [1, 2]).x - 2) < 1e-8
    assert abs((v1 - [1, 2]).x - 0) < 1e-8
    assert (v1.dot(v1) - v1.norm() ** 2) < 1e-8
Vec2__test__()

if __name__ == '__main__':
    from pylab import plot, figure, clf, show, axis
    from numpy import array
    mm = 1.
    center = [0, 30]
    orient = [10,2]
    screw_diameter = 3 * mm
    nut_diameter = 5.5 * mm
    nut_w = 1.8 * mm
    screw_length = 16 * mm
    thickness = 6 * mm
    
    orient = Vec2(orient)

#   setup out and up as unit vectors

 
    
    out = orient / orient.norm()
    up = Vec2([-out[1], out[0]])
    center = Vec2(center)
    screw_r = screw_diameter / 2.
    nut_r = nut_diameter / 2.
    path = Path([center + up * screw_r])
    path.append_from_last(orient)
    path.append_from_last(up * (nut_r - screw_r))
    path.append_from_last(out * (nut_w))
    path.append_from_last(-up * (nut_r - screw_r))
    path.append_from_last(out * (screw_length - thickness))
    path.append_from_last(-up * screw_r)
    print ('out is {0}'.format(out))
    print ('center is {0}'.format(center))
    print ('up is {0}'.format(up))
    up=Vec2([-up[0],up[1]])
    print ('up is {0}'.format(up))

    rest = path.reflect(center, up).reverse()
    path.extend(rest)
    path.plot()
    rest.plot('o-')
    axis('equal')
    show()

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 fileencoding=utf-8 textwidth=99
