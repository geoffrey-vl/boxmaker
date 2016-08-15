from ink_helper import *



import inkex 
# jslee - shamelessly adapted from sample code on below Inkscape wiki page 2015-07-28
# http://wiki.inkscape.org/wiki/index.php/Generating_objects_from_extensions
def drawCircle(r, (cx, cy), my_dict):
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
    inkex.etree.SubElement(my_dict['parent'], inkex.addNS('path','svg'), ell_attribs )


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
    thickness = my_dict['thickness'] 
    screw_length = my_dict['screw_length']
    orient = orient*(screw_length - thickness )

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


class Edge:
    '''
    an edge class to hold all information of an edge
    '''
    def side(self, length,(dirx,diry),isTab,lS_up, my_dict):
    #       root startOffset endOffset self.tabVec1 length  direction  isTab
    
        if my_dict['debug'] :
            inkex.errormsg(_('self.x{} , self.y {} , '.format(  self.x, self.y ),))
        
            '''
            inkex.errormsg(_('self.sox {}'.format(  self.sox ), end=', '))
            inkex.errormsg(_('self.soy {}'.format(  self.soy ), end=', '))
            inkex.errormsg(_('self.eox {}'.format(  self.eox )))
            inkex.errormsg(_('self.eoy {}'.format(  self.eoy )))
            inkex.errormsg(_('length {}'.format(  length )))
            inkex.errormsg(_('dirx {}'.format(  dirx )))
            inkex.errormsg(_('diry {}'.format(  diry )))
            '''

        divs=int(length/my_dict['nom_tab_width'])  # divisions
        if not divs%2: divs-=1   # make divs odd
        divs=float(divs)
        tabs=(divs-1)/2          # tabs for side
        screw_r = my_dict['screw_diameter'] / 2.

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
    
        firstVec=0; secondVec=self.tabVec1

        dirxN=0 if dirx else 1 # used to select operation on x or y
        diryN=0 if diry else 1
        thickness = my_dict['thickness']
        half_thickness = thickness/2

        (Vx,Vy)=(self.x+self.sox*thickness,self.y+self.soy*thickness)
    
        s='M '+str(Vx)+','+str( -1 * Vy)+' '

        if dirxN: Vy=self.y
        if diryN: Vx=self.x

        # generate line as tab or hole using:
        #   last co-ord:Vx,Vy ; tab dir:self.tabVec1  ; direction:dirx,diry ; thickness:thickness
        #   divisions:divs ; gap width:gapWidth ; tab width:tabWidth


        if my_dict['debug'] :
            inkex.errormsg('Vx {} ,Vy {} '.format(  Vx , Vy ))
    
            inkex.errormsg('dirx {} , diry {} '.format(  dirx , diry ))
        
            inkex.errormsg('dirxN {} , diryN {}'.format(  dirxN, diryN ))
        
            inkex.errormsg('lS_up {} , '.format( lS_up ))
            inkex.errormsg('firstVec {} , secondVec {} ,  '.format(  firstVec, secondVec  ))
            inkex.errormsg('thickness  {} , half_thickness {} '.format( thickness , half_thickness  ))
            inkex.errormsg('  \n\n ' )

        #setup for nut slots and holes
        s_h_flipflop = '0' # always skip the first hole or nut slot.

        if isTab  : 
            start_sequence = 'O'
        else :
            start_sequence = 'I'
        do_holes = my_dict[ self.panel_name + '_'+ self.name + '_screw_hole']
        do_slots = my_dict[ self.panel_name + '_'+ self.name +  '_nutslot']


        for n in range(1,int(divs)):
            if n%2:
                Vx=Vx+(dirx*gapWidth+dirxN*firstVec+first*dirx)/2
                Vy=Vy+(diry*gapWidth+diryN*firstVec+first*diry)/2
                s+='L '+str(Vx)+','+str(-1*Vy)+' '
                if s_h_flipflop == 'I':
                    if my_dict['debug'] :
                        inkex.errormsg('first slot maker')
                    if do_slots :
                        slot_path = t_slot((Vx,-1*Vy), lS_up , my_dict)
                        drawS(slot_path.drawXY(), my_dict['parent'])
                    s_h_flipflop = 'O'
                elif s_h_flipflop == 'O' :
                    if my_dict['debug'] :
                        inkex.errormsg('first hole maker')
                    if do_holes :
                        drawCircle( screw_r, ((Vx+lS_up[0] * half_thickness) , -1* (Vy -
                            lS_up[1]*half_thickness )), my_dict )
                    s_h_flipflop = 'I'
                else : s_h_flipflop = start_sequence 

                Vx=Vx+(dirx*gapWidth+dirxN*firstVec+first*dirx)/2
                Vy=Vy+(diry*gapWidth+diryN*firstVec+first*diry)/2
                s+='L '+str(Vx)+','+str(-1*Vy)+' '

                Vx=Vx+dirxN*secondVec
                Vy=Vy+diryN*secondVec
                s+='L '+str(Vx)+','+str(-1*Vy)+' '
            else:
                Vx=Vx+(dirx*tabWidth+dirxN*firstVec)/2
                Vy=Vy+(diry*tabWidth+diryN*firstVec)/2
                s+='L '+str(Vx)+','+str(-1*Vy)+' '

                if s_h_flipflop == 'I':
                    if my_dict['debug'] :
                        inkex.errormsg('second slot maker')
                    if do_slots :
                        slot_path = t_slot((Vx,-1*Vy), lS_up , my_dict)
                        drawS(slot_path.drawXY(), my_dict['parent'])
                    s_h_flipflop ='O'
                elif s_h_flipflop == 'O' :
                    if my_dict['debug'] :
                        inkex.errormsg('second hole maker')
                    if do_holes :
                        drawCircle( screw_r, (Vx +lS_up[0]*half_thickness  , -1* (Vy
                            -lS_up[1]*half_thickness )), my_dict )
                    s_h_flipflop = 'I'
                else : s_h_flipflop = start_sequence 


                Vx=Vx+(dirx*tabWidth+dirxN*firstVec)/2
                Vy=Vy+(diry*tabWidth+diryN*firstVec)/2
                s+='L '+str(Vx)+','+str(-1*Vy)+' '

                Vx=Vx+dirxN*secondVec
                Vy=Vy+diryN*secondVec
                s+='L '+str(Vx)+','+str(-1*Vy)+' '


            (secondVec,firstVec)=(-secondVec,-firstVec) # swap tab direction
            first=0

        s+='L '+str(self.x+self.eox*my_dict['thickness']+dirx*length)+','+str(-1*(
            self.y+self.eoy*my_dict['thickness']+diry*length))+' '
        return s




    def __init__(self, panel_name, name, x , y, (sox,soy),(eox,eoy), isTab ,tab_direction, length , my_dict):

        self.panel_name = panel_name
        self.name = name
        self.x =x
        self.y = y
        self.sox, self.soy = (sox,soy)
        self.eox, self.eoy = (eox,eoy)
        self.isTab = isTab
        #tab_direction is 1 or -1 according to how this edge
        #is to mate with the adjoining edge. 
        self.tab_direction = tab_direction 
        self.thickness = my_dict['thickness']
        #tab_direction times thickness becomes the distance and direction 
        #to draw the tab side.
        self.tabVec1 = self.tab_direction * self.thickness 
        self.length = length

        if self.name == 'top_edge' :          
            directionV2 = Vec2(-1 , 0) 
            S_up = Vec2(0,1)            
        elif self.name == 'right_edge' : 
            directionV2 = Vec2(0, 1)
            S_up = Vec2(-1,0)
        elif self.name == 'bottom_edge': 
            directionV2 = Vec2(1, 0)
            S_up = Vec2(0,-1)
        elif self.name == 'left_edge':              
            directionV2 = Vec2(0, -1)
            S_up = Vec2(1,0)
        else :
            inkex.debug('wrong edge parameter {} passed to edge class'.format(i))
            
        #(Vx,Vy)=(self.x+sox*my_dict['thickness'],self.y+soy*my_dict['thickness'])
        from ink_helper import drawS
        if my_dict['debug'] :
            S='M '+str(x)+','+str(-1*y)+' '

            S+='L '+str(x + self.length * directionV2[0])+','+str( -1*(y + self.length*directionV2[1]))+' '
 
            drawS(S, my_dict['parent'])
# def side((self.x,self.y),(sox,soy),(eox,self.eoy),self.tabVec1,length,(dirx,diry),isTab, my_dict):
#       root startOffset endOffset self.tabVec1 length  direction  isTab
    
        if True :
            S = self.side(length , directionV2, isTab  ,S_up, my_dict)


            drawS(S, my_dict['parent'])
  
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 fileencoding=utf-8 textwidth=99
    
