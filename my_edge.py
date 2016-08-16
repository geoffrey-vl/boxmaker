from ink_helper import *



import inkex 
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


class Edge:
    '''
    an edge class to hold all information of an edge
    '''
    def side(self ):
    #       root startOffset endOffset self.tabVec1 length  direction  isTab
    
        if self.debug :
            inkex.errormsg(_('self.x{} , self.y {} , '.format(  self.x, self.y ),))
        
            '''
            inkex.errormsg(_('self.sox {}'.format(  self.sox ), end=', '))
            inkex.errormsg(_('self.soy {}'.format(  self.soy ), end=', '))
            inkex.errormsg(_('self.eox {}'.format(  self.eox )))
            inkex.errormsg(_('self.eoy {}'.format(  self.eoy )))
            inkex.errormsg(_('self.length {}'.format(  self.length )))
            inkex.errormsg(_('self.dirV2[0] {}'.format(  self.dirV2[0] )))
            inkex.errormsg(_('self.dirV2[1] {}'.format(  self.dirV2[1] )))
            '''

        divs=int(self.length/self.nom_tab_width)  # divisions
        if not divs%2: divs-=1   # make divs odd
        divs=float(divs)
        tabs=(divs-1)/2          # tabs for side
        screw_r = self.screw_diameter / 2.

        if self.equalTabs :
            gapWidth=tabWidth=self.length/divs
        else:
            tabWidth=self.nom_tab_width
            gapWidth=(self.length-tabs*self.nom_tab_width)/(divs-tabs)
    
        if self.isTab:                 # kerf correction
            gapWidth-=self.correction
            tabWidth+=self.correction
            first=self.correction/2
        else:
            gapWidth+=self.correction
            tabWidth-=self.correction
            first=-self.correction/2
    
        firstVec=0; secondVec=self.tabVec1

        dirxN=0 if self.dirV2[0] else 1 # used to select operation on x or y
        diryN=0 if self.dirV2[1] else 1
    
        half_thickness = self.thickness/2

        (Vx,Vy)=(self.x+self.sox*self.thickness,self.y+self.soy*self.thickness)
    
        s='M '+str(Vx)+','+str( -1 * Vy)+' '

        if dirxN: Vy=self.y
        if diryN: Vx=self.x

        # generate line as tab or hole using:
        #   last co-ord:Vx,Vy ; tab dir:self.tabVec1  ; direction:self.dirV2 ; thickness:thickness
        #   divisions:divs ; gap width:gapWidth ; tab width:tabWidth


        if self.debug :
            inkex.errormsg('Vx {} ,optparseVy {} '.format(  Vx , Vy ))
    
            inkex.errormsg('self.dirV2[0] {} , self.dirV2[1] {} '.format(  self.dirV2[0] , self.dirV2[1] ))
        
            inkex.errormsg('dirxN {} , diryN {}'.format(  dirxN, diryN ))
        
            inkex.errormsg('self.inV2 {} , '.format( self.inV2 ))
            inkex.errormsg('firstVec {} , secondVec {} ,  '.format(  firstVec, secondVec  ))
            inkex.errormsg('thickness  {} , half_thickness {} '.format( self.thickness , half_thickness  ))
            inkex.errormsg('  \n\n ' )

        #setup for nut slots and holes
        s_h_flipflop = '0' # always skip the first hole or nut slot.

        if self.isTab  : 
            start_sequence = 'O'
        else :
            start_sequence = 'I'


        for n in range(1,int(divs)):
            if n%2:
                Vx=Vx+(self.dirV2[0]*gapWidth+dirxN*firstVec+first*self.dirV2[0])/2
                Vy=Vy+(self.dirV2[1]*gapWidth+diryN*firstVec+first*self.dirV2[1])/2
                s+='L '+str(Vx)+','+str(-1*Vy)+' '
                if s_h_flipflop == 'I':
                    if self.debug :
                        inkex.errormsg('first slot maker')
                    if self.do_slots :
                        slot_path = t_slot((Vx,-1*Vy), self.inV2 ,self.thickness, self.screw_length,
                                self.screw_diameter, self.nut_diameter, self.nut_height )
                        drawS(slot_path.drawXY(), self.parent)
                    s_h_flipflop = 'O'
                elif s_h_flipflop == 'O' :
                    if self.debug :
                        inkex.errormsg('first hole maker')
                    if self.do_holes :
                        drawCircle( screw_r, ((Vx+self.inV2[0] * half_thickness) , -1* (Vy -
                            self.inV2[1]*half_thickness )), self.parent  )
                    s_h_flipflop = 'I'
                else : s_h_flipflop = start_sequence 

                Vx=Vx+(self.dirV2[0]*gapWidth+dirxN*firstVec+first*self.dirV2[0])/2
                Vy=Vy+(self.dirV2[1]*gapWidth+diryN*firstVec+first*self.dirV2[1])/2
                s+='L '+str(Vx)+','+str(-1*Vy)+' '

                Vx=Vx+dirxN*secondVec
                Vy=Vy+diryN*secondVec
                s+='L '+str(Vx)+','+str(-1*Vy)+' '
            else:
                Vx=Vx+(self.dirV2[0]*tabWidth+dirxN*firstVec)/2
                Vy=Vy+(self.dirV2[1]*tabWidth+diryN*firstVec)/2
                s+='L '+str(Vx)+','+str(-1*Vy)+' '

                if s_h_flipflop == 'I':
                    if self.debug :
                        inkex.errormsg('second slot maker')
                    if self.do_slots :
                        slot_path = t_slot((Vx,-1*Vy), self.inV2 ,self.thickness, self.screw_length,
                                self.screw_diameter, self.nut_diameter, self.nut_height )

                        drawS(slot_path.drawXY(), self.parent)
                    s_h_flipflop ='O'
                elif s_h_flipflop == 'O' :
                    if self.debug :
                        inkex.errormsg('second hole maker')
                    if self.do_holes :
                        drawCircle( screw_r, (Vx +self.inV2[0]*half_thickness  , -1* (Vy
                            -self.inV2[1]*half_thickness )), self.parent  )
                    s_h_flipflop = 'I'
                else : s_h_flipflop = start_sequence 


                Vx=Vx+(self.dirV2[0]*tabWidth+dirxN*firstVec)/2
                Vy=Vy+(self.dirV2[1]*tabWidth+diryN*firstVec)/2
                s+='L '+str(Vx)+','+str(-1*Vy)+' '

                Vx=Vx+dirxN*secondVec
                Vy=Vy+diryN*secondVec
                s+='L '+str(Vx)+','+str(-1*Vy)+' '


            (secondVec,firstVec)=(-secondVec,-firstVec) # swap tab direction
            first=0

        s+='L '+str(self.x+self.eox*self.thickness+self.dirV2[0]*self.length)+','+str(-1*(
            self.y+self.eoy*self.thickness+self.dirV2[1]*self.length))+' '
        return s




    def __init__(self, panel_name, name, x , y, (sox,soy),(eox,eoy), isTab ,tab_direction, length , my_dict):

        self.debug = my_dict['debug']

        #Knerf correction
        self.correction = my_dict['correction']
        
        self.nom_tab_width = my_dict['nom_tab_width']   

        self.equalTabs = my_dict['equalTabs']

        self.screw_diameter = my_dict['screw_diameter']
        self.screw_length = my_dict['screw_length']
        self.nut_diameter = my_dict['nut_diameter']
        self.nut_height = my_dict['nut_height']
        
        self.panel_name = panel_name
        self.name = name

        self.do_holes = my_dict[ self.panel_name + '_'+ self.name + '_screw_hole']
        self.do_slots = my_dict[ self.panel_name + '_'+ self.name +  '_nutslot']

        self.parent = my_dict['parent']
        #x, y are absolute position coordinate  
        self.x = x
        self.y = y

        #sox,soy,eox,eoy contain correction of where edge starts and ends
        self.sox, self.soy = (sox,soy)
        self.eox, self.eoy = (eox,eoy)

        #isTab controls the mesh pattern of of the box where panels meet.
        #That is to say isTab is True of and edge then its mating edge must have 
        # have isTab False.
        self.isTab = isTab

        #tab_direction is 1 or -1 according to how this edge
        #is to mate with the adjoining edge. 
        self.tab_direction = tab_direction 
        self.thickness = my_dict['thickness']
        #tab_direction times thickness becomes the distance and direction 
        #to draw the tab side.
        self.tabVec1 = self.tab_direction * self.thickness 

        #length in one direction of this edge
        self.length = length

        #self.dirV2 holds the unit 2 dimention vector of  this edge
        self.dirV2 = None
        
        #inV2 holds the direction in , that is to say direction from
        #the edge toward the inside of the panel
        self.inV2 = None 

        

        if self.name == 'top_edge' :          
            self.dirV2 = Vec2(-1 , 0) 
            self.inV2 = Vec2(0,1)    

        elif self.name == 'right_edge' : 
            self.dirV2 = Vec2(0, 1)
            self.inV2 = Vec2(-1,0)

        elif self.name == 'bottom_edge': 
            self.dirV2 = Vec2(1, 0)
            self.inV2 = Vec2(0,-1)

        elif self.name == 'left_edge':              
            self.dirV2 = Vec2(0, -1)
            self.inV2 = Vec2(1,0)

        else :
            inkex.debug('wrong edge parameter {} passed to edge class'.format(i))
            
        #(Vx,Vy)=(self.x+sox*self.thickness,self.y+soy*self.thickness)
        from ink_helper import drawS
        if self.debug :
            S='M '+str(x)+','+str(-1*y)+' '

            S+='L '+str(x + self.length * self.dirV2[0])+','+str( -1*(y +
                self.length*self.dirV2[1]))+' '
 
            drawS(S, self.parent)
# def side((self.x,self.y),(sox,soy),(eox,self.eoy),self.tabVec1,length,(dirx,diry),isTab, my_dict):
#       root startOffset endOffset self.tabVec1 length  direction  isTab
    
        if True :
            S = self.side()


            drawS(S, self.parent)
  
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 fileencoding=utf-8 textwidth=99
    
