
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


from ink_helper import *
import inkex

class Edge:
    '''
    an edge class to hold all information of an edge
    '''
    def side(self ):
    #       root startOffset endOffset self.tabVec1 length  direction  isTab
    
        if self.debug :
            inkex.errormsg(_('self.x{0} , self.y {1} , '.format(  self.x, self.y ),))
        
            '''
            inkex.errormsg(_('self.sox {0}'.format(  self.sox ), end=', '))
            inkex.errormsg(_('self.soy {0}'.format(  self.soy ), end=', '))
            inkex.errormsg(_('self.eox {0}'.format(  self.eox )))
            inkex.errormsg(_('self.eoy {0}'.format(  self.eoy )))
            inkex.errormsg(_('self.length {0}'.format(  self.length )))
            inkex.errormsg(_('self.dirV2[0] {0}'.format(  self.dirV2[0] )))
            inkex.errormsg(_('self.dirV2[1] {0}'.format(  self.dirV2[1] )))
            '''

        

        divs=int(self.length/self.nom_tab_width)  # divisions
        if not divs%2: divs-=1   # make divs odd
        divs=float(divs)
        tabs=(divs-1)/2          # tabs for side
        screw_r = self.screw_diameter / 2.

        if 'Fixed' == self.equalTabs :
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
            inkex.errormsg('Vx {0} , Vy {1} '.format(  Vx , Vy ))
    
            inkex.errormsg('self.dirV2[0] {0} , self.dirV2[1] {1} '.format(  self.dirV2[0] , self.dirV2[1] ))
        
            inkex.errormsg('dirxN {0} , diryN {1}'.format(  dirxN, diryN ))
        
            inkex.errormsg('self.inV2 {0} , '.format( self.inV2 ))
            inkex.errormsg('firstVec {0} , secondVec {1} ,  '.format(  firstVec, secondVec  ))
            inkex.errormsg('thickness  {0} , half_thickness {1} '.format( self.thickness ,
                half_thickness  ))
            inkex.errormsg('  \n\n ' )

        #setup for nut slots and holes
        s_h_flipflop = '0' # always skip the first hole or nut slot.

        if self.isTab  : 
            start_sequence = 'O'
        else :
            start_sequence = 'I'


        for n in range(1,int(divs)):
            if n == 1:
                Vx=Vx+(self.dirV2[0]*gapWidth+dirxN*firstVec+first*self.dirV2[0])
                Vy=Vy+(self.dirV2[1]*gapWidth+diryN*firstVec+first*self.dirV2[1])
                s+='L '+str(Vx)+','+str(-1*Vy)+' '
                Vx=Vx+dirxN*secondVec
                Vy=Vy+diryN*secondVec
                s+='L '+str(Vx)+','+str(-1*Vy)+' '
                s_h_flipflop = start_sequence 

            elif n%2:
                Vx=Vx+(self.dirV2[0]*gapWidth+dirxN*firstVec)/2
                Vy=Vy+(self.dirV2[1]*gapWidth+diryN*firstVec)/2
                s+='L '+str(Vx)+','+str(-1*Vy)+' '
                

                if s_h_flipflop == 'I':
                    if self.do_slots :
                        slot_path = t_slot((Vx,-1*Vy), self.inV2 ,self.thickness, self.screw_length,
                                self.screw_diameter, self.nut_diameter, self.nut_height )
                        drawS(slot_path.drawXY(), self.parent)
                    s_h_flipflop = 'O'
                elif s_h_flipflop == 'O' :
                    if self.do_holes :
                        drawCircle( screw_r, ((Vx+self.inV2[0] * half_thickness) , -1* (Vy -
                            self.inV2[1]*half_thickness )), self.parent  )
                    s_h_flipflop = 'I'
                else : s_h_flipflop = start_sequence 

                Vx=Vx+(self.dirV2[0]*gapWidth+dirxN*firstVec)/2
                Vy=Vy+(self.dirV2[1]*gapWidth+diryN*firstVec)/2
                s+='L '+str(Vx)+','+str(-1*Vy)+' '
 
                Vx=Vx+dirxN*secondVec
                Vy=Vy+diryN*secondVec
                s+='L '+str(Vx)+','+str(-1*Vy)+' '
            else:
                Vx=Vx+(self.dirV2[0]*tabWidth+dirxN*firstVec)/2
                Vy=Vy+(self.dirV2[1]*tabWidth+diryN*firstVec)/2
                s+='L '+str(Vx)+','+str(-1*Vy)+' '
 
                if s_h_flipflop == 'I':
                    if self.do_slots :
                        slot_path = t_slot((Vx,-1*Vy), self.inV2 ,self.thickness, self.screw_length,
                                self.screw_diameter, self.nut_diameter, self.nut_height )

                        drawS(slot_path.drawXY(), self.parent)
                    s_h_flipflop ='O'
                elif s_h_flipflop == 'O' :
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

        s+='L '+str(self.x+self.eox*self.thickness+self.dirV2[0]*self.length)+','+str(-1*(
            self.y+self.eoy*self.thickness+self.dirV2[1]*self.length))+' '

        return s




    def __init__(self, panel_name, name, x , y, (sox,soy),(eox,eoy), isTab ,tab_direction, length , my_dict):

        self.debug = my_dict['debug']

        #Knerf correction
        self.correction = my_dict['correction']

        if panel_name in (['left_panel','front_panel','right_panel','back_panel']) and name in (['right_edge', 'left_edge']) :
                self.nom_tab_width = my_dict['nom_depth_tab_width']
        elif panel_name in (['top_panel','front_panel','bottom_panel','back_panel','divider_panel']) and name in (['top_edge','bottom_edge']) :
                self.nom_tab_width = my_dict['nom_length_tab_width']
        elif panel_name in (['left_panel','right_panel']) and name in (['top_edge','bottom_edge']) :
                self.nom_tab_width = my_dict['nom_width_tab_width']
        elif panel_name in (['top_panel','bottom_panel','divider_panel']) and name in (['right_edge','left_edge']):
                self.nom_tab_width = my_dict['nom_width_tab_width']

 
#        self.nom_tab_width = my_dict['nom_tab_width']   

        self.equalTabs = my_dict['equalTabs']

        self.screw_diameter = my_dict['screw_diameter']
        self.screw_length = my_dict['screw_length']
        self.nut_diameter = my_dict['nut_diameter']
        self.nut_height = my_dict['nut_height']
        
        self.panel_name = panel_name
        self.name = name
        if not 'divider_panel' == panel_name :
            self.do_holes = my_dict[ self.panel_name + '_'+ self.name + '_screw_hole']
        else:  
            self.do_holes = False
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
            inkex.debug('wrong edge parameter {0} passed to edge class'.format(i))
            
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
    
