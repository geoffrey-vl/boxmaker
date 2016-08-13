from my_edge import Edge

import inkex

def appendScript(parent,x,y, text):
    super = inkex.etree.SubElement(parent, inkex.addNS('text', 'svg'), 
            {'style':'font-size:200%' , 'fill':'red' , 'x':'{}'.format(x) , 'y':'{}'.format(y)})
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

        self.bottom_edge = Edge(name + '_bottom_edge', 'B',   x_coord ,     y_coord , ( d, a),(-b, a ), a ,1- 2*a , x, my_dict)

        self.right_edge = Edge(name + '_right_edge','R', x_coord + x,  y_coord ,    (-b, a),(-b,-c ),  b  , 2*b-1, y, my_dict)

        self.top_edge = Edge(name + '_top_edge','T',x_coord + x,  y_coord + y ,   (-d,-c),( d,-c ),  c , 2*c-1,  x, my_dict)

        self.left_edge = Edge(name + '_left_edge','L',  x_coord,      y_coord + y, ( d,-c),( d, a ), d , 1 -2*d,  y, my_dict)
         
        appendScript( my_dict['parent'],(x_coord + x/2), (-1 *(y_coord +y/2
            )), self.name)
        
        


    
    

# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 fileencoding=utf-8 textwidth=99
