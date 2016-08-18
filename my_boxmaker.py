#! /usr/bin/env python
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
__version__ = "0.9" ### please report bugs, suggestions etc to j.apple.muncy@gmail.com ###

from ink_helper import *

_ = gettext.gettext

import inkex 
inkex.localize()

#DEBUG = True

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
  
def t_slot(center, orient, my_dict ):
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
    orient = Vec2(orient)
    out = orient / orient.norm()
    up = Vec2([out[1], -out[0]])
    center = Vec2(center)
    screw_r = my_dict['screw_diameter'] / 2.
    nut_r = my_dict['nut_diameter'] / 2.
    nut_w = my_dict['screw_diameter']
    #nut_w = nut_height
    path = Path([center + up * screw_r])
    path.append_from_last(orient)
    path.append_from_last(up * (nut_r - screw_r))
    path.append_from_last(out * ( my_dict['nut_height']  ))
    path.append_from_last(-up * (nut_r - screw_r))
    path.append_from_last(out * (my_dict['nut_height']))
    path.append_from_last(-up * screw_r)
    path.extend(path.reflect(center, up).reverse())
    return path

def t_slots((rx,ry),(sox,soy),(eox,eoy),tabVec,length,(dirx,diry),isTab, do_holes, my_dict):
    #       root startOffset endOffset tabVec length  direction  isTab

    divs=int(length/my_dict['nom_tab_width'])  # divisions
    if not divs%2: divs-=1   # make divs odd
    divs=float(divs)
    tabs=(divs-1)/2          # tabs for side
  
    if my_dict['equalTabs']=='Fixed':
        gapWidth=tabWidth=length/divs
    else:
        tabWidth=my_dict['nom_tab_width']
        gapWidth=(length-tabs*my_dict['nom_tab_width'])/(divs-tabs)
    
    if isTab:                 # kerf correction
        gapWidth-=my_dict['correction']
        tabWidth+=my_dict['correction']
        first=my_dict['correction']/2
    else:
        gapWidth+=my_dict['correction']
        tabWidth-=my_dict['correction']
        first=-my_dict['correction']/2
    
    s=[] 
    firstVec=0; secondVec=tabVec
    dirxN=0 if dirx else 1 # used to select operation on x or y
    diryN=0 if diry else 1
    (Vx,Vy)=(rx+sox*my_dict['thickness'],ry+soy*my_dict['thickness'])
    #nut_diameter = 3.25 * screw_diameter
  
    step = Vec2([dirx * (tabWidth + gapWidth + firstVec * 2), diry * (tabWidth + gapWidth + firstVec * 2)])
    orient = Vec2([-diry * (my_dict['screw_length'] - my_dict['thickness'] ), dirx * (my_dict['screw_length'] - my_dict['thickness'] )])

    if my_dict['debug'] :
        inkex.errormsg(_('orient is {}'.format(  orient)))
        inkex.errormsg(_('orient is {}'.format(  orient / orient.norm())))
      

    center = Vec2(Vx + dirx* (gapWidth + tabWidth/2.),
            Vy + diry* (gapWidth + tabWidth/2.)) + (orient / orient.norm()) * my_dict['thickness']
    slot = t_slot(center, orient, my_dict )
    hole = drill(center - (orient / orient.norm()) * (my_dict['thickness'] * 1.5 + my_dict['spacing']), 
               my_dict['screw_diameter'], 45)
  
    slots = []
    holes = []
    for i in range(0,(int(divs)) / 2, 1):
        slots.append(slot.translate(step * i))
        if do_holes:
            holes.append(hole.translate(step * i))
            holes.append(hole.translate(step * i - orient / orient.norm() * (my_dict['height'] - my_dict['thickness']) ))

    out = [s.drawXY() for s in slots]
    out.extend([h.drawXY() for h in holes])

    #if DEBUG : inkex.errormsg(_('out {}'.format( out)))

    return out
  
def side((rx,ry),(sox,soy),(eox,eoy),tabVec,length,(dirx,diry),isTab, my_dict):
    #       root startOffset endOffset tabVec length  direction  isTab
    '''    if DEBUG :
        inkex.errormsg(_('rx{}'.format(  rx ), end=', '))
        inkex.errormsg(_('ry {}'.format(  ry ), end=', '))
        inkex.errormsg(_('sox {}'.format(  sox ), end=', '))
        inkex.errormsg(_('soy {}'.format(  soy ), end=', '))
        inkex.errormsg(_('eox {}'.format(  eox )))
        inkex.errormsg(_('eoy {}'.format(  eoy )))
        inkex.errormsg(_('length {}'.format(  length )))
        inkex.errormsg(_('dirx {}'.format(  dirx )))
        inkex.errormsg(_('diry {}'.format(  diry )))
    '''

    divs=int(length/my_dict['nom_tab_width'])  # divisions
    if not divs%2: divs-=1   # make divs odd
    divs=float(divs)
    tabs=(divs-1)/2          # tabs for side
  
    if my_dict['equalTabs']:
        gapWidth=tabWidth=length/divs
    else:
        tabWidth=my_dict['nom_tab_width']
        gapWidth=(length-tabs*my_dict['nom_tab_width'])/(divs-tabs)
    
    if isTab:                 # kerf correction
        gapWidth-=my_dict['correction']
        tabWidth+=my_dict['correction']
        first=my_dict['correction']/2
    else:
        gapWidth+=my_dict['correction']
        tabWidth-=my_dict['correction']
        first=-my_dict['correction']/2
    
    firstVec=0; secondVec=tabVec
    dirxN=0 if dirx else 1 # used to select operation on x or y
    diryN=0 if diry else 1
    (Vx,Vy)=(rx+sox*my_dict['thickness'],ry+soy*my_dict['thickness'])
    s='M '+str(Vx)+','+str(Vy)+' '

    if dirxN: Vy=ry # set correct line start
    if diryN: Vx=rx

    # generate line as tab or hole using:
    #   last co-ord:Vx,Vy ; tab dir:tabVec  ; direction:dirx,diry ; thickness:thickness
    #   divisions:divs ; gap width:gapWidth ; tab width:tabWidth

    for n in range(1,int(divs)):
        if n%2:
            Vx=Vx+dirx*gapWidth+dirxN*firstVec+first*dirx
            Vy=Vy+diry*gapWidth+diryN*firstVec+first*diry
            s+='L '+str(Vx)+','+str(Vy)+' '
            Vx=Vx+dirxN*secondVec
            Vy=Vy+diryN*secondVec
            s+='L '+str(Vx)+','+str(Vy)+' '
        else:
            Vx=Vx+dirx*tabWidth+dirxN*firstVec
            Vy=Vy+diry*tabWidth+diryN*firstVec
            s+='L '+str(Vx)+','+str(Vy)+' '
            Vx=Vx+dirxN*secondVec
            Vy=Vy+diryN*secondVec
            s+='L '+str(Vx)+','+str(Vy)+' '

        (secondVec,firstVec)=(-secondVec,-firstVec) # swap tab direction
        first=0
    s+='L '+str(rx+eox*my_dict['thickness']+dirx*length)+','+str(ry+eoy*my_dict['thickness']+diry*length)+' '
    return s

  
class TSlotBoxMaker(inkex.Effect):
    def __init__(self):

        # Call the base class constructor.
        inkex.Effect.__init__(self)

        panels = ['front_panel','back_panel','left_panel','right_panel','top_panel','bottom_panel']
        edge = ['bottom_edge','right_edge','top_edge','left_edge']
        ns_h  = ['nutslot','screw_hole']

        # Define options
        
        for a in panels :
            for b in edge :
                for c in ns_h :
                    d = a + '_'+ b + '_'+ c
                    self.OptionParser.add_option(('--' + d) ,action='store', type="inkbool",
                        dest= d ,default=True,help='Draw nut slots / screw holes')

                

        self.OptionParser.add_option('--unit',action='store',type='string',
            dest='unit',default='mm',help='Measure Units')
        self.OptionParser.add_option('--inside',action='store',type='int',
            dest='inside',default=0,help='Int/Ext Dimension')
        self.OptionParser.add_option('--length',action='store',type='float',
            dest='length' ,default=100,help='Length of Box')
        self.OptionParser.add_option('--width',action='store',type='float',
            dest='width',default=100,help='Width of Box')
        self.OptionParser.add_option('--depth',action='store',type='float',
            dest='height',default=100,help='Height of Box')
        self.OptionParser.add_option('--tab_width',action='store',type='float',
            dest='tab_width',default=25,help='Nominal Tab Width')
        self.OptionParser.add_option('--equal',action='store',type='string',
            dest='equal',default='Fixed',help='Equal/Prop Tabs')
        self.OptionParser.add_option('--thickness',action='store',type='float',
            dest='thickness',default=10,help='Thickness of Material')
        self.OptionParser.add_option('--kerf',action='store',type='float',
            dest='kerf',default=0.5,help='Kerf (width) of cut')
        self.OptionParser.add_option('--clearance',action='store',type='float',
            dest='clearance',default=0.01,help='Clearance of joints')
        self.OptionParser.add_option('--style',action='store',type='int',
            dest='style',default=25,help='Layout/Style')
        self.OptionParser.add_option('--spacing',action='store',type='float',
            dest='spacing',default=25,help='Part Spacing')
        self.OptionParser.add_option('--screw_length',action='store',type='float',
            dest='screw_length',default=25,help='Screw Length')
        self.OptionParser.add_option('--screw_diameter',action='store',type='float',
            dest='screw_diameter',default=25,help='Screw Diameter')  
        self.OptionParser.add_option('--nut_height',action='store',type='float',
            dest='nut_height',default=25,help='Nut Height')
        self.OptionParser.add_option('--nut_diameter',action='store',type='float',
            dest='nut_diameter',default=25,help='Nut Diameter')


        self.OptionParser.add_option('--debug',action='store',type='int',
            dest='debug',default=0,help='Debug mode On/Off')

        self.OptionParser.add_option('--draw_original',action='store', type="inkbool",
            dest='draw_original',default=False,help='Draw original part')


        self.OptionParser.add_option('--front_panel_cutout',action='store',type='inkbool',
            dest='front_panel_cutout',default=True,help='Draw cutout True/False')

        self.OptionParser.add_option('--front_panel_center_X',action='store',type='float',
            dest='front_panel_center_X' ,default=40.0,help='Center Line of cutout side to side')
        self.OptionParser.add_option('--front_panel_center_Y',action='store',type='float',
            dest='front_panel_center_Y',default=40.0,help='Center Line of cutout up/down')
        self.OptionParser.add_option('--front_panel_dim_X',action='store',type='float',
            dest='front_panel_dim_X',default=10.0,help='Witdh of cutout')
        self.OptionParser.add_option('--front_panel_dim_Y',action='store',type='float',
            dest='front_panel_dim_Y',default=10.0,help='Height of cutout')
        self.OptionParser.add_option('--front_panel_corner_R',action='store',type='float',
            dest='front_panel_corner_R',default=5.0,help='Cutout corner radius')

        # here so we can have tabs - but we do not use it directly - else error
        self.OptionParser.add_option("", "--active-tab",action="store", type="string",
                                    dest="active_tab", default='title', # use a legitmate default
                                    help="Active tab.")



        
    def effect(self):
        
        box_dict ={}
        '''
        stuff all options inside a dictionary to avoid using global variables
        '''
        box_dict['front_panel_bottom_edge_nutslot'] = self.options.front_panel_bottom_edge_nutslot
        box_dict['front_panel_bottom_edge_screw_hole'] = self.options.front_panel_bottom_edge_screw_hole
        box_dict['front_panel_right_edge_nutslot'] = self.options.front_panel_right_edge_nutslot
        box_dict['front_panel_right_edge_screw_hole'] = self.options.front_panel_right_edge_screw_hole
        box_dict['front_panel_top_edge_nutslot'] = self.options.front_panel_top_edge_nutslot
        box_dict['front_panel_top_edge_screw_hole'] = self.options.front_panel_top_edge_screw_hole
        box_dict['front_panel_left_edge_nutslot'] = self.options.front_panel_left_edge_nutslot
        box_dict['front_panel_left_edge_screw_hole'] = self.options.front_panel_left_edge_screw_hole
        box_dict['back_panel_bottom_edge_nutslot'] = self.options.back_panel_bottom_edge_nutslot
        box_dict['back_panel_bottom_edge_screw_hole'] = self.options.back_panel_bottom_edge_screw_hole
        box_dict['back_panel_right_edge_nutslot'] = self.options.back_panel_right_edge_nutslot
        box_dict['back_panel_right_edge_screw_hole'] = self.options.back_panel_right_edge_screw_hole
        box_dict['back_panel_top_edge_nutslot'] = self.options.back_panel_top_edge_nutslot
        box_dict['back_panel_top_edge_screw_hole'] = self.options.back_panel_top_edge_screw_hole
        box_dict['back_panel_left_edge_nutslot'] = self.options.back_panel_left_edge_nutslot
        box_dict['back_panel_left_edge_screw_hole'] = self.options.back_panel_left_edge_screw_hole
        box_dict['left_panel_bottom_edge_nutslot'] = self.options.left_panel_bottom_edge_nutslot
        box_dict['left_panel_bottom_edge_screw_hole'] = self.options.left_panel_bottom_edge_screw_hole
        box_dict['left_panel_right_edge_nutslot'] = self.options.left_panel_right_edge_nutslot
        box_dict['left_panel_right_edge_screw_hole'] = self.options.left_panel_right_edge_screw_hole
        box_dict['left_panel_top_edge_nutslot'] = self.options.left_panel_top_edge_nutslot
        box_dict['left_panel_top_edge_screw_hole'] = self.options.left_panel_top_edge_screw_hole
        box_dict['left_panel_left_edge_nutslot'] = self.options.left_panel_left_edge_nutslot
        box_dict['left_panel_left_edge_screw_hole'] = self.options.left_panel_left_edge_screw_hole
        box_dict['right_panel_bottom_edge_nutslot'] = self.options.right_panel_bottom_edge_nutslot
        box_dict['right_panel_bottom_edge_screw_hole'] = self.options.right_panel_bottom_edge_screw_hole
        box_dict['right_panel_right_edge_nutslot'] = self.options.right_panel_right_edge_nutslot
        box_dict['right_panel_right_edge_screw_hole'] = self.options.right_panel_right_edge_screw_hole
        box_dict['right_panel_top_edge_nutslot'] = self.options.right_panel_top_edge_nutslot
        box_dict['right_panel_top_edge_screw_hole'] = self.options.right_panel_top_edge_screw_hole
        box_dict['right_panel_left_edge_nutslot'] = self.options.right_panel_left_edge_nutslot
        box_dict['right_panel_left_edge_screw_hole'] = self.options.right_panel_left_edge_screw_hole
        box_dict['top_panel_bottom_edge_nutslot'] = self.options.top_panel_bottom_edge_nutslot
        box_dict['top_panel_bottom_edge_screw_hole'] = self.options.top_panel_bottom_edge_screw_hole
        box_dict['top_panel_right_edge_nutslot'] = self.options.top_panel_right_edge_nutslot
        box_dict['top_panel_right_edge_screw_hole'] = self.options.top_panel_right_edge_screw_hole
        box_dict['top_panel_top_edge_nutslot'] = self.options.top_panel_top_edge_nutslot
        box_dict['top_panel_top_edge_screw_hole'] = self.options.top_panel_top_edge_screw_hole
        box_dict['top_panel_left_edge_nutslot'] = self.options.top_panel_left_edge_nutslot
        box_dict['top_panel_left_edge_screw_hole'] = self.options.top_panel_left_edge_screw_hole
        box_dict['bottom_panel_bottom_edge_nutslot'] = self.options.bottom_panel_bottom_edge_nutslot
        box_dict['bottom_panel_bottom_edge_screw_hole'] = self.options.bottom_panel_bottom_edge_screw_hole
        box_dict['bottom_panel_right_edge_nutslot'] = self.options.bottom_panel_right_edge_nutslot
        box_dict['bottom_panel_right_edge_screw_hole'] = self.options.bottom_panel_right_edge_screw_hole
        box_dict['bottom_panel_top_edge_nutslot'] = self.options.bottom_panel_top_edge_nutslot
        box_dict['bottom_panel_top_edge_screw_hole'] = self.options.bottom_panel_top_edge_screw_hole
        box_dict['bottom_panel_left_edge_nutslot'] = self.options.bottom_panel_left_edge_nutslot
        box_dict['bottom_panel_left_edge_screw_hole'] = self.options.bottom_panel_left_edge_screw_hole


        box_dict['front_panel_cutout'] = self.options.front_panel_cutout







        box_dict['debug'] = self.options.debug
        box_dict['draw_original'] = self.options.draw_original
    



        # Get access to main SVG document element and get its dimensions.
        svg = self.document.getroot()
    
        # Get the attibutes:
        box_dict['widthDoc']  = self.unittouu(svg.get('width'))
        box_dict['heightDoc'] = self.unittouu(svg.get('height'))

        # Create a new layer.
        layer = inkex.etree.SubElement(svg, 'g')
        layer.set(inkex.addNS('label', 'inkscape'), 'newlayer')
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')

        box_dict['parent']=self.current_layer
        #parent=self.current_layer
    
        # Get script's option values.
        unit=self.options.unit

        box_dict['front_panel_center_X'] = self.unittouu( str(self.options.front_panel_center_X) + unit )
        box_dict['front_panel_center_Y'] = self.unittouu( str(self.options.front_panel_center_Y)  + unit )

        box_dict['front_panel_dim_X'] = self.unittouu( str(self.options.front_panel_dim_X)  + unit )

        box_dict['front_panel_dim_Y'] = self.unittouu( str(self.options.front_panel_dim_Y)  + unit )

        box_dict['front_panel_corner_R'] = self.unittouu( str(self.options.front_panel_corner_R)  + unit )


        thickness = self.unittouu( str(self.options.thickness)  + unit )
        inside=self.options.inside
        X = self.unittouu( str(self.options.length)  + unit )
        
        Y = self.unittouu( str(self.options.width) + unit )
        
        Z = self.unittouu( str(self.options.height)  + unit )
        
        
        box_dict['nom_tab_width']=self.unittouu( str(self.options.tab_width) + unit )
        #nom_tab_width = self.unittouu( str(self.options.tab_width) + unit )
        
        box_dict['equalTabs']=self.options.equal
        kerf = self.unittouu( str(self.options.kerf)  + unit )
        clearance = self.unittouu( str(self.options.clearance)  + unit )
        layout=self.options.style
        box_dict['spacing'] = self.unittouu( str(self.options.spacing)  + unit )
        box_dict['screw_length'] = self.unittouu( str(self.options.screw_length)  + unit )
        box_dict['screw_diameter'] = self.unittouu( str(self.options.screw_diameter)  + unit )
        box_dict['nut_height'] = self.unittouu( str(self.options.nut_height)  + unit )
        box_dict['nut_diameter'] = self.unittouu( str(self.options.nut_diameter)  + unit )

        if inside: # if inside dimension selected correct values to outside dimension
            X+=thickness*2
            Y+=thickness*2
            Z+=thickness*2

        box_dict['correction']=kerf-clearance
        '''
        Be careful to add all dictionary enteries before instanciating the box
        '''
    # check input values mainly to avoid python errors
    # TODO restrict values to *correct* solutions
        error=0
    
        if min(X,Y,Z)==0:
            inkex.errormsg(_('Error: Dimensions must be non zero'))
            error=1
        if max(X,Y,Z)>max(box_dict['widthDoc'],box_dict['heightDoc'])*10: # crude test
            inkex.errormsg(_('Error: Dimensions Too Large'))
            error=1
        if min(X,Y,Z)<3*box_dict['nom_tab_width']:
            inkex.errormsg(_('Error: Tab size too large'))
            error=1

        if box_dict['nom_tab_width']<thickness:
            inkex.errormsg(_('Error: Tab size too small'))
            error=1	  
        if thickness==0:
            inkex.errormsg(_('Error: Thickness is zero'))
            error=1	  
        if thickness>min(X,Y,Z)/3: # crude test
            inkex.errormsg(_('Error: Material too thick'))
            error=1	  
        if box_dict['correction']>min(X,Y,Z)/3: # crude test
            inkex.errormsg(_('Error: Kerf/Clearence too large'))
            error=1	  
        if box_dict['spacing']>max(X,Y,Z)*10: # crude test
            inkex.errormsg(_('Error: Spacing too large'))
            error=1	  
        if box_dict['spacing']<kerf:
            inkex.errormsg(_('Error: Spacing too small'))
            error=1	  

        if error: exit()
        box_dict['length']= X
        box_dict['width']=Y
        box_dict['height']=Z
        box_dict['thickness']= thickness
        inkex.errormsg('length = {} width = {} height = {} '.format( X,Y,Z))          
        from my_box import Box

        box = Box(box_dict)
        
        if not box_dict['draw_original'] : return
   
    # layout format:(rootx),(rooty),Xlength,Ylength,tabInfo
    # root= (spacing,X,Y,Z) * values in tuple
    # tabInfo= <abcd> 0=holes 1=tabs
        if   layout==1: # Diagramatic Layout
            pieces=[[(2,0,0,1),(3,0,1,1),X,Z,0b1010, False, False],
                   [(1,0,0,0),(2,0,0,1),Z,Y,0b1111, False, False],
                   [(2,0,0,1),(2,0,0,1),X,Y,0b0000,  True,  True],
                   [(3,1,0,1),(2,0,0,1),Z,Y,0b1111, False, False],
                   [(4,1,0,2),(2,0,0,1),X,Y,0b0000,  True, False],
                   [(2,0,0,1),(1,0,0,0),X,Z,0b1010, False, False]]
        elif layout==2: # 3 Piece Layout
            pieces=[[(2,0,0,1),(2,0,1,0),X,Z,0b1010, False, False],
                   [(1,0,0,0),(1,0,0,0),Z,Y,0b1111, False, False],
                   [(2,0,0,1),(1,0,0,0),X,Y,0b0000,  True, False]]
        elif layout==3: # Inline(compact) Layout
            pieces=[[(1,0,0,0),(1,0,0,0),X,Y,0b0000, False, False],
                   [(2,1,0,0),(1,0,0,0),X,Y,0b0000, False, False],
                   [(3,2,0,0),(1,0,0,0),Z,Y,0b0101,  True,  True],
                   [(4,2,0,1),(1,0,0,0),Z,Y,0b0101, False, False],
                   [(5,2,0,2),(1,0,0,0),X,Z,0b1111,  True, False],
                   [(6,3,0,2),(1,0,0,0),X,Z,0b1111, False, False]]
        elif layout==4: # Diagramatic Layout with Alternate Tab Arrangement
            pieces=[[(2,0,0,1),(3,0,1,1),X,Z,0b1001, False, False],
                   [(1,0,0,0),(2,0,0,1),Z,Y,0b1100, False, False],
                   [(2,0,0,1),(2,0,0,1),X,Y,0b1100,  True, False],
                   [(3,1,0,1),(2,0,0,1),Z,Y,0b0110, False,  True],
                   [(4,1,0,2),(2,0,0,1),X,Y,0b0110,  True, False],
                   [(2,0,0,1),(1,0,0,0),X,Z,0b1100, False, False]]

        for piece in pieces: # generate and draw each piece of the box
            (xs,xx,xy,xz)=piece[0]
            (ys,yx,yy,yz)=piece[1]
            x=xs*box_dict['spacing']+xx*X+xy*Y+xz*Z  # root x co-ord for piece
            y=ys*box_dict['spacing']+yx*X+yy*Y+yz*Z  # root y co-ord for piece
            dx=piece[2]
            dy=piece[3]
            tabs=piece[4]
            slots = piece[5]
            holes = piece[6]
            if box_dict['debug']:
                inkex.errormsg(_('tabs {}'.format(  tabs )))

                inkex.errormsg(_('slots {}'.format(  slots )))

                inkex.errormsg(_('holes {}'.format(  holes )))
            #def side((rx,ry),(sox,soy),(eox,eoy),tabVec,length,(dirx,diry),isTab, my_dict):
            #       root startOffset endOffset tabVec length  direction  isTab


            a=tabs>>3&1; b=tabs>>2&1; c=tabs>>1&1; d=tabs&1 # extract tab status for each side
      # generate and draw the sides of each piece
            drawS(side((x,y),(d,a),(-b,a),-box_dict['thickness'] if a else box_dict['thickness'],dx,(1,0),a, box_dict), box_dict['parent'])          # side a
            drawS(side((x+dx,y),(-b,a),(-b,-c),box_dict['thickness'] if b else -box_dict['thickness'],dy,(0,1),b, box_dict), box_dict['parent'])     # side b
            drawS(side((x+dx,y+dy),(-b,-c),(d,-c),box_dict['thickness'] if c else -box_dict['thickness'],dx,(-1,0),c, box_dict), box_dict['parent']) # side c
            drawS(side((x,y+dy),(d,-c),(d,a),-box_dict['thickness'] if d else box_dict['thickness'],dy,(0,-1),d, box_dict), box_dict['parent'])      # side d

# side((rx,ry),(sox,soy),(eox,eoy),tabVec,length,(dirx,diry),isTab):
    #       root startOffset endOffset tabVec length  direction  isTab

            if slots:
                
                if box_dict['debug'] :
                    inkex.errormsg(_('slots {}'.format(  slots )))

                [drawS(slot, box_dict['parent']) for slot in t_slots((x,y),(d,a),(-b,a),-box_dict['thickness'] if a else
                        box_dict['thickness'],dx,(1,0),a, holes, box_dict)]          # slot a
                [drawS(slot, box_dict['parent']) for slot in t_slots((x+dx,y),(-b,a),(-b,-c), box_dict['thickness'] if b
                        else -box_dict['thickness'],dy,(0,1),b, holes, box_dict)]   # slot b
                [drawS(slot, box_dict['parent']) for slot in t_slots((x+dx,y+dy),(-b,-c),(d,-c),box_dict['thickness'] if c
                        else -box_dict['thickness'],dx,(-1,0),c, holes, box_dict)] # slot c
                [drawS(slot, box_dict['parent']) for slot in t_slots((x,y+dy),(d,-c),(d,a),-box_dict['thickness'] if d
                        else box_dict['thickness'],dy,(0,-1),d, holes, box_dict)]      # slot d

# Create effect instance and apply it.
e = TSlotBoxMaker()
e.affect()
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 fileencoding=utf-8 textwidth=99
