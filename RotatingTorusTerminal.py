import math
# A Torus is a 3d solid of revolution. We can rotate a cricle around an axis to draw the Torus.

# Equation of circle is (x-a)^2 + (y-b)^2 = r^2
# Recall Pythagorean Identity cos^2(theta) + sin^2(theta) = 1
# Which implies that r^2*cos^2(theta) + r^2*sin^2(theta) = r^2
# So x = r*cos(theta) + a, and y = r*sin(theta) + b

#If we sweep theta from 0 to 2pi we draw a circle.
#Let R2 be the distance from origin to the center of the circle we are sweeping,

#Our parametric equations for our circle centered at (R2, 0) is:
# x = R2 + R1*cos(theta), y = R1*sin(theta)

# Let's construct the torus by rotating the circle centered at (M1, 0) about the y-axis 
#We can do this using our parametric equations for the point on a circle by a rotation matrix about the y-axis.

#Let our vector equation for the circle in R^3 be [x, y, z] = [R2 + R1*cos(theta), R1*sin(theta), 0]
#After right multiplying our y-axis rotation matrix (using angle phi) by our vector equation for our circle we get:
#[x, y, z] = [(R2 + R1*cost(theta))*cos(phi), R1*sin(theta), -(R2 + R1*cos(theta))*sin(phi)]
#Now seeping theta and phi from 0 to 2pi we get our torus where the y-axis point through the hole.

#To rotate this torus about the x-axis by A and z-axis by B we right-multiply the appropriate rotation matrices by our point vector.

screen_width = 35
screen_height = 20
theta_spacing = 0.07 # we don't need as many point on our circle for each phi
phi_spacing = 0.02 # we need to sample more phis to create the illusion of the torus
illumination = [".",",","-","~",":",";","=","!","*","#","$","@"]

#To render a 3d point onto a 2d terminal we need to project it.

#using similar triangles  y'/z' = y/z => y' = z'*y/z where z' is assumed to be constant distnace from screen. Let's fix as as K1
#same for x, x'/z' = x/z => x' = z'*x/z
#we can choose K1 arbitrarily based on the field of view we want to show in the 2d window

#e.g. window is 100 x 100. View is centered at 50, 50. If we want to see an object which is 10 units wide, and 5 units back then K1 should be chosen so that the projection of the point x=10, z=5 is still on the screen
# ignoring y for now, x' must be less than 50 to be on the screen. so K1*10/5 < 50, so K1 < 25. 

#When we are plotting we might end up projecting a bunch of 3d points to the same 2d point. So we need to maintain a z-buffer.
#We initialize our z-buffer to 1/z as z of 0 indicates infinity for background. 

#As are rendering the donut in 3d we also need another constant K2 for distance from donut to viewer (assume camera is at origin). 

#So [x', y'] = [K1*x/(K2+z),K1*y/(K2+z)] is our projection equation.

#More constants

R1 = 1 #circle radius of 1 unit
R2 = 2 # torus radius (from origin to circle center) of 2 units
K2 = 8 #torus will be 8 units in front of origin

#Calculate K1 based on screen size: the maximum x-distance occurs
#roughly at the edge of the torus, which is at x=R1+R2, z=0.  we
#want that to be displaced 3/8ths of the width of the screen, which
#is 3/4th of the way from the center to the side of the screen.
#screen_width*3/8 = K1*(R1+R2)/(K2+0)
#screen_width*K2*3/(8*(R1+R2)) = K1
#there should be 1/8 the width of the screen on either side of the donut.

#we want the torus to be shown at 
#K1x = screen_width*(K2)*3/(8*(R1+R2))
#K1x = 30
#K1y = screen_height*(K2)*3/(8*(R1+R2))

K1 = screen_width*K2*3/(8*(R1+R2))
#K1y = screen_width*K2*3/(8*(R1+R2))

#need this as cannot use for loops with floats in python
def decimal_range(start, stop, increment):
    while start < stop: # and not math.isclose(start, stop): Py>3.5
        yield start
        start += increment

def render_frame():
    #cosA, cosB, sinA, sinB = math.cos(A), math.cos(B), math.sin(A), math.sin(B)
    output = [[' ']*screen_height for i in range(screen_width)] # width x height
    zbuffer = [[0]*screen_height for i in range(screen_width)] # width x height

    #print(len(output))
    #print(len(output[0]))

    #sweep over theta for the cross-sectional circle of the torus
    theta = 0
    while (theta < 2*math.pi):
    #for theta in np.arange(0,2*math.pi,theta_spacing):
        costheta, sintheta = math.cos(theta), math.sin(theta)

        #sweep over the phi to sweep the circle around the center of revolution for the torus
        phi = 0
        #for phi in np.arange(0,2*math.pi,phi_spacing):
        while (phi < 2*math.pi):
            cosphi, sinphi = math.cos(phi), math.sin(phi)

            #the x,y coordinate of the circle before revolving around the center of revolution.
            circlex = R2 + R1*costheta
            circley = R1*sintheta

            x = circlex*cosphi
            y = circley
            z = K2 -sinphi*circlex #Adding K2 so that our circle origin is K2 units in z-direction from screen.

            #calculate 1/z
            ooz = 1/z
            #in our terminal 0,0 will be top left corner and y-axis will point down.
            
            #we want to plot donut in the middle of the terminal so we will translate donut coordinates. Additionally, y axis will point down in screen space so we multiply y-coordinate by -1.
            xp = int(screen_width/2 + K1*ooz*x)
            yp = int(screen_height/2 - K1*ooz*y)

            #caculating luminance. We need to know the surface normal.
            #for a parametric surface this is the normalized cross product of the partial derivatives with respect to u and v. Ensure it is the outwards facing normal.
            #alternatively you can an outwards normal vector to a cirle can be derived. is is N = [cos(theta),sin(theta),0]. Then we can rotate this normal by the rotation matrices appropriately.
            #rotating it about the y-axis gives [cos(theta)cos(phi), sin(theta), -sin(phi)cos(theta)]

            #we will have the light vector point to (0,1,-1) so objects facing up and behind the viewer will be lit. 
            #this vector is usually normalized for dot product comparisons but we will compensate later.

            #We will take the dot product between our light vector and our Normal vector on our torus.
            L = sintheta + sinphi*costheta # L ranges from -sqrt(2) to sqrt(2) since our lighting vector had magnitude or sqrt(2) and is being dotted with unit vector.

            if xp == 30 and yp ==17:
                p=1

            if xp == 31 and yp ==17:
                p=1

            if xp == 32 and yp ==17:
                p=1

            if xp == 33 and yp ==17:
                p=1

            if L > 0:
                #if point is facing away from the light source does not need to be rendered.
                if ooz > zbuffer[xp][yp]:
                    #this means the 1/z1 > 1/z2 in other words z1 < z2. So our new point at this (x,y) location is closer to the screen.
                    zbuffer[xp][yp] = ooz
                    luminance_index = int(L*8) #this ranges from 0 to 11 since sqrt(2)*8 = 11.3
                    output[xp][yp] = illumination[luminance_index]

            phi += phi_spacing
        theta += theta_spacing    
    return output    


def pprint(frame_buffer):

    for y in range(len(frame_buffer[0])):
        for x in range(len(frame_buffer)):
            print(frame_buffer[x][y],end='')
        print("\n",end='')
    
    
    #print(*[" ".join(row) for row in frame_buffer], sep="\n")

if __name__ == "__main__":
    print('\x1b[2J') # clear the screen
    print(f"K1: {K1}")
    frame_buffer = render_frame()
    '''
    with open('my_donut.txt','w') as fp:
        for y in range(len(frame_buffer[0])):
            for x in range(len(frame_buffer)):
                fp.write(frame_buffer[x][y])
            fp.write("\n")'''
    pprint(frame_buffer)     

    #nots about first attempt