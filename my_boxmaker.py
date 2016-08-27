#! /usr/bin/env python
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
__version__ = "0.91" ### please report bugs, suggestions etc to j.apple.muncy@gmail.com ###

from ink_helper import *

_ = gettext.gettext

import inkex 
inkex.localize()
  
class TSlotBoxMaker(inkex.Effect):
    """Top level class to handle setup and parse options. 

    """
    def __init__(self):

        # Call the base class constructor.
        inkex.Effect.__init__(self)

        panels = ['front_panel','back_panel','left_panel','right_panel','top_panel','bottom_panel',
                'divider_panel']
        edge = ['bottom_edge','right_edge','top_edge','left_edge']
        ns_h  = ['nutslot','screw_hole']

        # Define options
        
        for a in panels :
            for b in edge :
                for c in ns_h :
                    d = a + '_'+ b + '_'+ c
                    self.OptionParser.add_option(('--' + d) ,action='store', type="inkbool",
                        dest= d ,default=True,help='Draw nut slots / screw holes')

        cutout_options =['center_X','center_Y','dim_X','dim_Y','corner_R']

        for a in panels :
            for b in cutout_options :
                d = a + '_' + b
                self.OptionParser.add_option(('--'+d) , action='store', type='float',
                        dest = d , default = 0.0 , help ='cutout options')
            e = a + '_cutout'
            self.OptionParser.add_option(('--' + e) ,action='store', type="inkbool",
                        dest= e ,default=True,help='Draw cutout, True/False')

        self.OptionParser.add_option(('--has_divider' ) ,action='store', type="inkbool",
                        dest= 'has_divider' ,default=True,help='has_divider ? True/False')
        self.OptionParser.add_option('--divider_distance_from_top',action='store',type='float',
            dest='divider_distance_from_top',default=100,help='Divider distance from top panel')


        self.OptionParser.add_option('--unit',action='store',type='string',
            dest='unit',default='mm',help='Measure Units')
        self.OptionParser.add_option('--inside',action='store',type='int',
            dest='inside',default=0,help='Int/Ext Dimension')

        self.OptionParser.add_option('--length',action='store',type='float',
            dest='length' ,default=100,help='Length of Box')
        self.OptionParser.add_option('--width',action='store',type='float',
            dest='width',default=100,help='Width of Box')
        self.OptionParser.add_option('--depth',action='store',type='float',
            dest='depth',default=100,help='Depth of Box')

        self.OptionParser.add_option('--length_tab_width',action='store',type='float',
            dest='length_tab_width',default=25,help='Lengthwise Nominal Tab Width ')

        self.OptionParser.add_option('--width_tab_width',action='store',type='float',
            dest='width_tab_width',default=25,help='Widthwize Nominal Tab Width')

        self.OptionParser.add_option('--depth_tab_width',action='store',type='float',
            dest='depth_tab_width',default=25,help='Depthwize Nominal Tab Width')



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


        self.OptionParser.add_option('--debug',action='store',type='inkbool',
            dest='debug',default=False,help='Debug mode On/Off')



        # here so we can have tabs - but we do not use it directly - else error
        self.OptionParser.add_option("", "--active-tab",
                                        action="store", type="string",
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
        
        box_dict['divider_panel_bottom_edge_nutslot'] = self.options.divider_panel_bottom_edge_nutslot
        box_dict['divider_panel_front_panel_screw_hole'] = self.options.divider_panel_bottom_edge_screw_hole
        box_dict['divider_panel_right_edge_nutslot'] = self.options.divider_panel_right_edge_nutslot
        box_dict['divider_panel_right_panel_screw_hole'] = self.options.divider_panel_right_edge_screw_hole
        box_dict['divider_panel_top_edge_nutslot'] = self.options.divider_panel_top_edge_nutslot
        box_dict['divider_panel_back_panel_screw_hole'] = self.options.divider_panel_top_edge_screw_hole
        box_dict['divider_panel_left_edge_nutslot'] = self.options.divider_panel_left_edge_nutslot
        box_dict['divider_panel_left_panel_screw_hole'] = self.options.divider_panel_left_edge_screw_hole


        box_dict['bottom_panel_bottom_edge_nutslot'] = self.options.bottom_panel_bottom_edge_nutslot
        box_dict['bottom_panel_bottom_edge_screw_hole'] = self.options.bottom_panel_bottom_edge_screw_hole
        box_dict['bottom_panel_right_edge_nutslot'] = self.options.bottom_panel_right_edge_nutslot
        box_dict['bottom_panel_right_edge_screw_hole'] = self.options.bottom_panel_right_edge_screw_hole
        box_dict['bottom_panel_top_edge_nutslot'] = self.options.bottom_panel_top_edge_nutslot
        box_dict['bottom_panel_top_edge_screw_hole'] = self.options.bottom_panel_top_edge_screw_hole
        box_dict['bottom_panel_left_edge_nutslot'] = self.options.bottom_panel_left_edge_nutslot
        box_dict['bottom_panel_left_edge_screw_hole'] = self.options.bottom_panel_left_edge_screw_hole


        box_dict['front_panel_cutout'] = self.options.front_panel_cutout
        box_dict['left_panel_cutout'] = self.options.left_panel_cutout
        box_dict['right_panel_cutout'] = self.options.right_panel_cutout
        box_dict['back_panel_cutout'] = self.options.back_panel_cutout
        box_dict['top_panel_cutout'] = self.options.top_panel_cutout

        box_dict['has_divider'] = self.options.has_divider
        box_dict['divider_panel_cutout'] = self.options.divider_panel_cutout

        box_dict['bottom_panel_cutout'] = self.options.bottom_panel_cutout







        box_dict['debug'] = self.options.debug
    



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

        box_dict['right_panel_center_X'] = self.unittouu( str(self.options.right_panel_center_X) + unit )
        box_dict['right_panel_center_Y'] = self.unittouu( str(self.options.right_panel_center_Y)  + unit )
        box_dict['right_panel_dim_X'] = self.unittouu( str(self.options.right_panel_dim_X)  + unit )
        box_dict['right_panel_dim_Y'] = self.unittouu( str(self.options.right_panel_dim_Y)  + unit )
        box_dict['right_panel_corner_R'] = self.unittouu( str(self.options.right_panel_corner_R)  + unit )

        box_dict['left_panel_center_X'] = self.unittouu( str(self.options.left_panel_center_X) + unit )
        box_dict['left_panel_center_Y'] = self.unittouu( str(self.options.left_panel_center_Y)  + unit )
        box_dict['left_panel_dim_X'] = self.unittouu( str(self.options.left_panel_dim_X)  + unit )
        box_dict['left_panel_dim_Y'] = self.unittouu( str(self.options.left_panel_dim_Y)  + unit )
        box_dict['left_panel_corner_R'] = self.unittouu( str(self.options.left_panel_corner_R)  + unit )

        box_dict['back_panel_center_X'] = self.unittouu( str(self.options.back_panel_center_X) + unit )
        box_dict['back_panel_center_Y'] = self.unittouu( str(self.options.back_panel_center_Y)  + unit )
        box_dict['back_panel_dim_X'] = self.unittouu( str(self.options.back_panel_dim_X)  + unit )
        box_dict['back_panel_dim_Y'] = self.unittouu( str(self.options.back_panel_dim_Y)  + unit )
        box_dict['back_panel_corner_R'] = self.unittouu( str(self.options.back_panel_corner_R)  + unit )

        box_dict['top_panel_center_X'] = self.unittouu( str(self.options.top_panel_center_X) + unit )
        box_dict['top_panel_center_Y'] = self.unittouu( str(self.options.top_panel_center_Y)  + unit )
        box_dict['top_panel_dim_X'] = self.unittouu( str(self.options.top_panel_dim_X)  + unit )
        box_dict['top_panel_dim_Y'] = self.unittouu( str(self.options.top_panel_dim_Y)  + unit )
        box_dict['top_panel_corner_R'] = self.unittouu( str(self.options.top_panel_corner_R)  + unit )


        box_dict['divider_distance_from_top'] = self.unittouu(
                str(self.options.divider_distance_from_top)  + unit )
        box_dict['divider_panel_center_X'] = self.unittouu( str(self.options.divider_panel_center_X) + unit )
        box_dict['divider_panel_center_Y'] = self.unittouu( str(self.options.divider_panel_center_Y)  + unit )
        box_dict['divider_panel_dim_X'] = self.unittouu( str(self.options.divider_panel_dim_X)  + unit )
        box_dict['divider_panel_dim_Y'] = self.unittouu( str(self.options.divider_panel_dim_Y)  + unit )
        box_dict['divider_panel_corner_R'] = self.unittouu( str(self.options.divider_panel_corner_R)  + unit )

        box_dict['bottom_panel_center_X'] = self.unittouu( str(self.options.bottom_panel_center_X) + unit )
        box_dict['bottom_panel_center_Y'] = self.unittouu( str(self.options.bottom_panel_center_Y)  + unit )
        box_dict['bottom_panel_dim_X'] = self.unittouu( str(self.options.bottom_panel_dim_X)  + unit )
        box_dict['bottom_panel_dim_Y'] = self.unittouu( str(self.options.bottom_panel_dim_Y)  + unit )
        box_dict['bottom_panel_corner_R'] = self.unittouu( str(self.options.bottom_panel_corner_R)  + unit )



        thickness = self.unittouu( str(self.options.thickness)  + unit )
        inside=self.options.inside
        X = self.unittouu( str(self.options.length)  + unit )
        
        Y = self.unittouu( str(self.options.width) + unit )
        
        Z = self.unittouu( str(self.options.depth)  + unit )
        
        
        box_dict['nom_length_tab_width']=self.unittouu( str(self.options.length_tab_width) + unit )
        box_dict['nom_width_tab_width']=self.unittouu( str(self.options.width_tab_width) + unit )
        box_dict['nom_depth_tab_width']=self.unittouu( str(self.options.depth_tab_width) + unit )
        





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

        box_dict['length']= X
        box_dict['width']=Y
        box_dict['depth']=Z
        box_dict['thickness']= thickness


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
        if  X < 3*box_dict['nom_length_tab_width']:
            inkex.errormsg(_('Error: Length Tab size too large'))
            error=1
        if  Y < 3*box_dict['nom_width_tab_width']:
            inkex.errormsg(_('Error: Width Tab size too large'))
            error=1
        if  Z < 3*box_dict['nom_depth_tab_width']:
            inkex.errormsg(_('Error: Depth Tab size too large'))
            error=1

        if min(box_dict['nom_length_tab_width'],box_dict['nom_width_tab_width'],box_dict['nom_depth_tab_width']) <thickness:
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
        if box_dict['debug'] :
            inkex.errormsg('length = {0} width = {1} depth = {2} '.format( X,Y,Z))          
        from my_box import Box

        box = Box(box_dict)

# Create effect instance and apply it.
e = TSlotBoxMaker()
e.affect()
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 fileencoding=utf-8 textwidth=99
