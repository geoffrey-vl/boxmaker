from my_panel import Panel
import inkex



class Box:
    '''
    a box class
    '''

    def __init__(self,  my_dict):
        '''
        all variables are passed in the dictionary my_dict. 
        
        "spacing" is the from zero to positive distance separating panels from 
        each other. It plays no other role.
        '''
        

        s = my_dict['spacing']


        '''
        Extract the dimensions of the 3d box.
        Length normally the longest side as the left to right dimension.
        
        Width normally next longest edge as front to back.

        Height as the shortest dimension from bottom to top.
        The user may choose differently.
        '''
        x = length = my_dict['length']
        y = width = my_dict['width']
        z = height = my_dict['height']

        inkex.errormsg('length = {} width = {} height = {} '.format( x , y , z))     
        inkex.errormsg('s = {}'.format(s))
        '''
        Here we transform to 2 dimensional space to have this layout when drawn 
        calculating absolute coordinates starting point in 2d space for each panel
                top
                s
        left s  front s  right s  back
                s
                bottom
        
        pass posX and posY as coordinates bottom left starting origin.

        Left to right is: 
        s z s x s z s

        Bottom to top is
        s
        y
        s
        z
        s
        '''
        left_x = s
        top_x = front_x = bottom_x = s + z + s
        right_x = s + z + s + x + s
        back_x = s + z + s + x + s + z + s

        top_y = s + z + s + y +s
        left_y = front_y = right_y = back_y = s + z + s
        bottom_y = s

        '''
        (a,b,c,d) hold information that gets translated to where edges start and end.
        '''

        (a,b,c,d) = 0,0,0,0

        self.front_panel = Panel( 'front_panel',  front_x,   front_y, (a,b,c,d),  length, width, my_dict)

        #if my_dict['debug'] : return
        
        self.back_panel = Panel(  'back_panel',   back_x,    back_y,  (a,b,c,d),  length, width, my_dict)


        (a,b,c,d) = 1,0,1,0
        self.top_panel = Panel(   'top_panel',    top_x,     top_y,   (a,b,c,d),  length, height, my_dict)
        self.bottom_panel = Panel('bottom_panel', bottom_x,  bottom_y,(a,b,c,d),  length, height, my_dict)

        (a,b,c,d) = 1,1,1,1
        self.left_panel = Panel ( 'left_panel',   left_x,    left_y,  (a,b,c,d),  height, width, my_dict)
        self.right_panel =Panel(  'right_panel',  right_x,   right_y, (a,b,c,d),  height, width, my_dict)


#        inkex.errormsg('  right_x = {},  right_y = {},  width= {},  height = {} '.format(  right_x,
#            right_y,  width,  height))
       
        if my_dict['front_panel_cutout'] : self.front_panel.do_cutout()
        if my_dict['back_panel_cutout'] : self.back_panel.do_cutout()
        if my_dict['right_panel_cutout'] : self.right_panel.do_cutout()
        if my_dict['left_panel_cutout'] : self.left_panel.do_cutout()
        if my_dict['top_panel_cutout'] : self.top_panel.do_cutout()
        if my_dict['bottom_panel_cutout'] : self.bottom_panel.do_cutout()
        


# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 fileencoding=utf-8 textwidth=99
