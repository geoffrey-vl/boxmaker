import math
import sys,inkex,simplestyle,gettext
import math


def drawS(XYstring, parent):         # Draw lines from a list
    name='part'
    style = { 'stroke': '#000000', 'fill': 'none' }
    drw = {'style':simplestyle.formatStyle(style),inkex.addNS('label','inkscape'):name,'d':XYstring}
    inkex.etree.SubElement(parent, inkex.addNS('path','svg'), drw )
    return

# jslee - shamelessly adapted from sample code on below Inkscape wiki page 2015-07-28
# http://wiki.inkscape.org/wiki/index.php/Generating_objects_from_extensions
def drawCircle(r, (cx, cy), parent):
#    log("putting circle at (%d,%d)" % (cx,cy))
    style = { 'stroke': '#000000', 'stroke-width': '1', 'fill': 'none' }
    ell_attribs = {'style':simplestyle.formatStyle(style),
        inkex.addNS('cx','sodipodi')        :str(cx),
        inkex.addNS('cy','sodipodi')        :str(cy),
        inkex.addNS('rx','sodipodi')        :str(r),
        inkex.addNS('ry','sodipodi')        :str(r),
        inkex.addNS('start','sodipodi')     :str(0),
        inkex.addNS('end','sodipodi')       :str(2*math.pi),
        inkex.addNS('open','sodipodi')      :'true', #all ellipse sectors we will draw are open
        inkex.addNS('type','sodipodi')      :'arc',
        'transform'                         :'' }
    inkex.etree.SubElement(parent, inkex.addNS('path','svg'), ell_attribs )


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
# jslee - shamelessly adapted from sample code on below Inkscape wiki page 2015-07-28
# http://wiki.inkscape.org/wiki/index.php/Generating_objects_from_extensions
def drawCircle(r, (cx, cy), parent):
#    log("putting circle at (%d,%d)" % (cx,cy))
    style = { 'stroke': '#000000', 'stroke-width': '1', 'fill': 'none' }
    ell_attribs = {'style':simplestyle.formatStyle(style),
        inkex.addNS('cx','sodipodi')        :str(cx),
        inkex.addNS('cy','sodipodi')        :str(cy),
        inkex.addNS('rx','sodipodi')        :str(r),
        inkex.addNS('ry','sodipodi')        :str(r),
        inkex.addNS('start','sodipodi')     :str(0),
        inkex.addNS('end','sodipodi')       :str(2*math.pi),
        inkex.addNS('open','sodipodi')      :'true', #all ellipse sectors we will draw are open
        inkex.addNS('type','sodipodi')      :'arc',
        'transform'                         :'' }
    inkex.etree.SubElement(parent, inkex.addNS('path','svg'), ell_attribs )


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
    print ('out is {}'.format(out))
    print ('center is {}'.format(center))
    print ('up is {}'.format(up))
    up=Vec2([-up[0],up[1]])
    print ('up is {}'.format(up))

    rest = path.reflect(center, up).reverse()
    path.extend(rest)
    path.plot()
    rest.plot('o-')
    axis('equal')
    show()

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 fileencoding=utf-8 textwidth=99
