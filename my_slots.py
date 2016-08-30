
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
class Slot_row:
    '''
    an Slot_row class to hold all information of an row of slots. 
    '''
    def row(self ):

        
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
    
        s=''
         
        if dirxN: Vy=self.y
        if diryN: Vx=self.x

        # generate line as tab or hole using:
        #   last co-ord:Vx,Vy ; tab dir:self.tabVec1  ; direction:self.dirV2 ; thickness:thickness
        #   divisions:divs ; gap width:gapWidth ; tab width:tabWidth



        #setup for nut slots and holes
        s_h_flipflop = '0' # always skip the first hole .

        if self.isTab  : 
            start_sequence = 'O'
        else :
            start_sequence = 'I'

        Ox,Oy = None,None
        for n in range(1,int(divs)):
            if n == 1:
                Vx=Vx+(self.dirV2[0]*gapWidth+dirxN*firstVec+first*self.dirV2[0])
                Vy=Vy+(self.dirV2[1]*gapWidth+diryN*firstVec+first*self.dirV2[1])
                s+='M '+str(Vx)+','+str(-1*Vy)+' '
                Ox,Oy=Vx,Vy


                Vx=Vx+dirxN*secondVec
                Vy=Vy+diryN*secondVec
                s+='L '+str(Vx)+','+str(-1*Vy)+' '
                s_h_flipflop = start_sequence 

            elif n%2:
                Vx=Vx+(self.dirV2[0]*gapWidth+dirxN*firstVec)/2
                Vy=Vy+(self.dirV2[1]*gapWidth+diryN*firstVec)/2
                

                if s_h_flipflop == 'I':
                    
                    #s+='L '+str(Vx)+','+str(-1*Vy)+' '
                    s_h_flipflop = 'O'

                elif s_h_flipflop == 'O' :
                    if self.do_holes :
                        drawCircle( screw_r, ((Vx+self.inV2[0] * half_thickness) , -1* (Vy -
                            self.inV2[1]*half_thickness )), self.parent  )
                    s_h_flipflop = 'I'
                else : s_h_flipflop = start_sequence 

                Vx=Vx+(self.dirV2[0]*gapWidth+dirxN*firstVec)/2
                Vy=Vy+(self.dirV2[1]*gapWidth+diryN*firstVec)/2
                #moves to right and below hole 
                s+='M '+str(Vx)+','+str(-1*Vy)+' '
                #this should grab the beginning of the box.
                Ox,Oy=Vx,Vy
                Vx=Vx+dirxN*secondVec
                Vy=Vy+diryN*secondVec
                #draws the first vertical line
                s+='L '+str(Vx)+','+str(-1*Vy)+' '

            else:
                Vx=Vx+(self.dirV2[0]*tabWidth+dirxN*firstVec)
                Vy=Vy+(self.dirV2[1]*tabWidth+diryN*firstVec)
                s+='L '+str(Vx)+','+str(-1*Vy)+' '
                #Ox , Oy = Vx, Vy

                if s_h_flipflop == 'I':
                    s_h_flipflop ='O'
                    
                elif s_h_flipflop == 'O' :
                    s_h_flipflop = 'I'
                else : s_h_flipflop = start_sequence 


                Vx=Vx+dirxN*secondVec
                Vy=Vy+diryN*secondVec
                s+='L '+str(Vx)+','+str(-1*Vy)+' '
                #close the box.
                s+='L '+str(Ox)+','+str(-1*Oy)+' '

            

            (secondVec,firstVec)=(-secondVec,-firstVec) # swap tab direction


        return s




    def __init__(self, panel_name, name, x , y, (sox,soy),(eox,eoy), isTab ,tab_direction, length , my_dict):
        '''
        grab all values to draw slots.
        '''
        self.debug = my_dict['debug']

        #Knerf correction
        self.correction = my_dict['correction']


        if panel_name in(['front_panel','back_panel']):
                self.nom_tab_width = my_dict['nom_length_tab_width']

        elif panel_name in (['left_panel','right_panel']): 
                self.nom_tab_width = my_dict['nom_width_tab_width']
        

        self.equalTabs = my_dict['equalTabs']

        self.screw_diameter = my_dict['screw_diameter']
        
        self.panel_name = panel_name
        self.name = name
        if not 'divider_panel' == panel_name :
            self.do_holes = my_dict[ self.panel_name + '_'  + self.name + '_screw_hole']
        else:  
            self.do_holes = False

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

        
        if self.name == 'slot_row': 
            self.dirV2 = Vec2(1, 0)
            self.inV2 = Vec2(0,-1)
        else :
            inkex.debug('wrong slot_row parameter {0} passed to Slot_row class'.format(i))

            
        S = self.row()


        drawS(S, self.parent)
  
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 fileencoding=utf-8 textwidth=99
    
