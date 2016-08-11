from ink_helper import *



import inkex 



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


def side((rx,ry),(sox,soy),(eox,eoy),tabVec,length,(dirx,diry),isTab,lS_up, my_dict):
    #       root startOffset endOffset tabVec length  direction  isTab
    if my_dict['debug'] :
        inkex.errormsg(_('rx{} , '.format(  rx ),))
        inkex.errormsg(_('ry {} , '.format(  ry ) ))
        '''
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
    
    s='M '+str(Vx)+','+str( -1 * Vy)+' '

    if dirxN: Vy=ry # set correct line start
    if diryN: Vx=rx

    # generate line as tab or hole using:
    #   last co-ord:Vx,Vy ; tab dir:tabVec  ; direction:dirx,diry ; thickness:thickness
    #   divisions:divs ; gap width:gapWidth ; tab width:tabWidth




    if my_dict['debug'] :
        inkex.errormsg('Vx {} , '.format(  Vx ))
        inkex.errormsg('Vy {} , '.format(  Vy ))
        inkex.errormsg('dirx {} , '.format(  dirx ))
        inkex.errormsg('diry {} , '.format(  diry ))
        inkex.errormsg('dirxN {} , '.format(  dirxN ))
        inkex.errormsg('diryN {} , '.format(  diryN ))
        inkex.errormsg('firstVec {} , '.format(  firstVec ))
        inkex.errormsg('secondVec {} , '.format(  secondVec ))



    for n in range(1,int(divs)):
        if n%2:
            Vx=Vx+(dirx*gapWidth+dirxN*firstVec+first*dirx)/2
            Vy=Vy+(diry*gapWidth+diryN*firstVec+first*diry)/2
            s+='L '+str(Vx)+','+str(-1*Vy)+' '

            slot_path = t_slot((Vx,-1*Vy), lS_up , my_dict)
            drawS(slot_path.drawXY(), my_dict['parent'])

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

            slot_path = t_slot((Vx,-1*Vy), lS_up , my_dict)
            drawS(slot_path.drawXY(), my_dict['parent'])

            Vx=Vx+(dirx*tabWidth+dirxN*firstVec)/2
            Vy=Vy+(diry*tabWidth+diryN*firstVec)/2
            s+='L '+str(Vx)+','+str(-1*Vy)+' '

            Vx=Vx+dirxN*secondVec
            Vy=Vy+diryN*secondVec
            s+='L '+str(Vx)+','+str(-1*Vy)+' '


        (secondVec,firstVec)=(-secondVec,-firstVec) # swap tab direction
        first=0

    s+='L '+str(rx+eox*my_dict['thickness']+dirx*length)+','+str(-1*(
        ry+eoy*my_dict['thickness']+diry*length))+' '
    return s


class Edge:
    '''
    an edge class to hold all information of an edge
    '''
    def __init__(self, i, x , y, (sox,soy),(eox,eoy), isTab ,td, length , my_dict):
        self.length = length

        if i == 'T':
            self.name = 'top_edge'             
            directionV2 = Vec2(-1 , 0) 
            S_up = Vec2(0,1)
            tab_direction = td
            
        elif i == 'R' :
            self.name = 'right_edge' 
            directionV2 = Vec2(0, 1)
            S_up = Vec2(-1,0)
            tab_direction = td
        elif i == 'B' :
            self.name = 'bottom_edge' 
            directionV2 = Vec2(1, 0)
            S_up = Vec2(0,-1)
            tab_direction = td
        elif i == 'L' :
            self.name = 'left_edge'             
            directionV2 = Vec2(0, -1)
            S_up = Vec2(1,0)
            tab_direction = td
        else :
            inkex.debug('wrong edge parameter {} passed to edge class'.format(i))
            
        #(Vx,Vy)=(rx+sox*my_dict['thickness'],ry+soy*my_dict['thickness'])
        from ink_helper import drawS
        if my_dict['debug'] :
            S='M '+str(x)+','+str(-1*y)+' '

            S+='L '+str(x + self.length * directionV2[0])+','+str( -1*(y + self.length*directionV2[1]))+' '
 
            drawS(S, my_dict['parent'])
# def side((rx,ry),(sox,soy),(eox,eoy),tabVec,length,(dirx,diry),isTab, my_dict):
#       root startOffset endOffset tabVec length  direction  isTab
    
        if i == i :
            S = side( (x , y ), (sox,soy) , (eox,eoy) , tab_direction * my_dict['thickness'],length ,
                directionV2, isTab  ,S_up, my_dict)


            drawS(S, my_dict['parent'])
  
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 fileencoding=utf-8 textwidth=99
    
