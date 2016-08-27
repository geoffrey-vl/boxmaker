
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

from my_edge import Edge

import inkex
import ink_helper

def appendScript(parent,x,y, text):
    super = inkex.etree.SubElement(parent, inkex.addNS('text', 'svg'), 
            {'style':'font-size:200%' , 'fill':'red' , 'x':'{0}'.format(x) , 'y':'{0}'.format(y)})
    super.text = text

class Panel:
    '''
    A 6 panel class to represent one of six panels of a box.

    A panel has 4 edges.

    And defining the start point as the lower left hand corned 
    as (x,y) in a Cartesian coordinate system.  

    Mean while both svg and inkscape use an (x, -y) system. 
    There for in each call to drawS we will set -1 * y to account for this.

    Drawing around the panel starting at the bottom lower left corner,
    drawing to the right the bottom edge, then up the right edge,
    then the top edge to the left, and finally down the left edge to
    the beginning.
    Translating the appropriate x or y to be the length of the drawn edge.

    a,b,c,d hold vales of 0 or 1 and get tanslated here into what becomes (sox,soy) and
    (eox,eoy) in the Edge object

    '''

    def __init__(self, name, x_coord, y_coord, (a,b,c,d) , x , y, my_dict):

        self.name = name
        self.x_coord = x_coord
        self.y_coord = y_coord 
        self.x = x
        self.y = y
        self.a, self.b,self.c,self.d =(a,b,c,d)



        self.my_dict = my_dict

        self.bottom_edge = Edge(self.name, 'bottom_edge' , x_coord ,    y_coord , ( d, a),(-b, a ), a, 1- 2*a , x, my_dict)

        self.right_edge = Edge(self.name , 'right_edge' , x_coord + x,  y_coord , (-b, a),(-b,-c ), b, 2*b-1, y, my_dict)

        self.top_edge = Edge(self.name ,'top_edge',x_coord + x,  y_coord + y ,    (-d,-c),( d,-c ), c, 2*c-1,  x, my_dict)

        self.left_edge = Edge(self.name , 'left_edge',  x_coord,      y_coord + y,( d,-c),( d, a ), d, 1 -2*d,  y, my_dict)
         
        appendScript( my_dict['parent'],(x_coord + x/2), (-1 *(y_coord +y/2
            )), self.name)
        
        
    def do_cutout(self):
        ink_helper.cutoutArea( (self.x_coord + self.x/2 + self.my_dict[self.name + '_center_X'] ,
                                self.y_coord + self.y/2 + self.my_dict[self.name + '_center_Y']) ,
                               ((self.my_dict[self.name + '_dim_X'])/2 ,
                                 (self.my_dict[self.name + '_dim_Y'])/2 ),
                                self.my_dict['parent'],
                                self.my_dict[self.name + '_corner_R'])

    def do_divider_slots(self):
        ink_helper.do_slots(self.name, 'divider_panel',self.x_coord ,  self.y_coord + self.y
                -self.my_dict['divider_distance_from_top'] ,
                (- self.d,- self.c),(  self.d,- self.c ),  self.c, 2* self.c-1,   self.x,  self.my_dict)


    
    

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 fileencoding=utf-8 textwidth=99
