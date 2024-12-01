import pygame
import sys
import time
import math
from fractions import Fraction

pygame.init()

screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
# screen = pygame.display.set_mode((0, 0), flags=pygame.FULLSCREEN)
# screen_width = screen.get_width()
# screen_height = screen.get_height()

clock = pygame.time.Clock()

dt = 1
last_time = time.time()
    
color_black = "#222222"

offset = [-screen_width/2, -screen_height/2]
smooth_offset = offset[:]

mouse_pos = [0, 0]
smooth_mouse_pos = [0, 0]
old_mouse_pos = [0, 0]

zoom = 2
smooth_zoom = zoom

smooth_world_mouse_pos = [0, 0]
world_mouse_pos = [0, 0]

unit = 10

inputting = False
input_circle = ["", "", ""]
input_index = 0

drawing = False
draw_dot_poses = []
draw_dot = False

line_start = [0, 0]
line_end = [0, 0]
line_active = False
line_complete = False

line_circle_intersect = False

font = pygame.font.Font("Galmuri11.ttf", 36)

def draw_text(screen, text, x, y, color=color_black, font=font):
    render = font.render(text, False, color)
    pygame.draw.rect(screen, "#eeeeee", render.get_rect().move(x, y))
    screen.blit(render, (x, y))
    
def sign(num):
    if num > 0:
        return 1
    elif num < 0:
        return -1   
    return 0

def remove_trailing_zeros(x):
    return ('%f' % x).rstrip('0').rstrip('.')

fps = 120

while True:
    screen.fill("#eeeeee")

    # dt = time.time() - last_time
    # dt *= 60
    # last_time = time.time() 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEWHEEL:
            if 10 > zoom + event.y/2 >= 1:
                before_zoom = [(mouse_pos[0]+offset[0])/zoom, (mouse_pos[1]+offset[1])/zoom]
                zoom += event.y/2*dt
                after_zoom = [(mouse_pos[0]+offset[0])/zoom, (mouse_pos[1]+offset[1])/zoom]

                offset[0] += before_zoom[0]*zoom-after_zoom[0]*zoom
                offset[1] += before_zoom[1]*zoom-after_zoom[1]*zoom 
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if not line_complete:
                    if line_active == False:
                        line_active = True
                        line_start = [world_mouse_pos[0], -world_mouse_pos[1]]
                    else:
                        line_end = [world_mouse_pos[0], -world_mouse_pos[1]]
                        line_complete = True
            elif event.button == 2:
                line_active = False
                line_complete = False
                line_start = [0, 0]
                line_end = [0, 0]
                line_circle_intersect = False
    
        if event.type == pygame.KEYDOWN:
            if inputting:   
                if event.unicode.isnumeric() or event.key == pygame.K_MINUS:
                    input_circle[input_index] += event.unicode
                if event.key == pygame.K_BACKSPACE:
                    input_circle[input_index] = input_circle[input_index][:-1]
                if event.key == pygame.K_LEFT:
                    if input_index > 0:
                        input_index -= 1
                if event.key == pygame.K_RIGHT:
                    if input_index+1 < len(input_circle):
                        input_index += 1
            else:
                if event.key == pygame.K_0:
                    offset = [-screen_width/2, -screen_height/2]
                if event.key == pygame.K_9:
                    if drawing:
                        offset = [int(input_circle[0])*unit*smooth_zoom-screen_width/2, -int(input_circle[1])*unit*smooth_zoom-screen_height/2]
                if event.key == pygame.K_1:
                    draw_dot = not draw_dot
            if event.key == pygame.K_RETURN:
                if inputting:
                    if input_circle[input_index] != "":
                        if "-" in input_circle[input_index]:
                            negative = False
                            if input_circle[input_index].startswith("-"):
                                negative = True
                            input_circle[input_index] = input_circle[input_index].replace("-", "")
                            if negative:
                                input_circle[input_index] = "-"+input_circle[input_index]
                        if input_index+1 < len(input_circle):
                            input_index += 1
                        else:
                            inputting = False
                            drawing = True
                            offset = [int(input_circle[0])*unit*smooth_zoom-screen_width/2, -int(input_circle[1])*unit*smooth_zoom-screen_height/2]
                            draw_dot_poses = []
                            for x in range(int(input_circle[0])-int(input_circle[2]), int(input_circle[0])+int(input_circle[2])+1):
                                for y in range(int(input_circle[1])-int(input_circle[2]), int(input_circle[1])+int(input_circle[2])+1):
                                    if 0 <= (int(input_circle[0])-x)**2 + (int(input_circle[1])-y)**2 <= int(input_circle[2])**2:
                                        pos = [x*unit, -y*unit]
                                        draw_dot_poses.append(pos)
                else:
                    inputting = True
                    drawing = False
                    input_index = 0
                    input_circle = ["", "", ""]

    # draw

    pygame.draw.line(screen, color_black, [0, -smooth_offset[1]], [screen_width, -smooth_offset[1]], 3)
    pygame.draw.line(screen, color_black, [-smooth_offset[0], 0], [-smooth_offset[0], screen_height], 3)

    for i in range(int(smooth_offset[0]/unit/smooth_zoom), int((screen_width+smooth_offset[0])/unit/smooth_zoom)+1):
        pygame.draw.line(screen, "#666666", [i*unit*smooth_zoom-smooth_offset[0], 0], [i*unit*smooth_zoom-smooth_offset[0], screen_height])
    for i in range(int(smooth_offset[1]/unit/smooth_zoom), int((screen_height+smooth_offset[1])/unit/smooth_zoom)+1):
        pygame.draw.line(screen, "#666666", [0, i*unit*smooth_zoom-smooth_offset[1]], [screen_width, i*unit*smooth_zoom-smooth_offset[1]])

    if drawing:
        pygame.draw.circle(screen, "#ee2222", [int(input_circle[0])*unit*smooth_zoom-smooth_offset[0], -int(input_circle[1])*unit*smooth_zoom-smooth_offset[1]], int(int(input_circle[2])*unit*smooth_zoom), 2)
        if draw_dot:
            for pos in draw_dot_poses:
                draw_pos = [
                    pos[0]*smooth_zoom-smooth_offset[0],
                
                    pos[1]*smooth_zoom-smooth_offset[1]
                ]
                if screen_width-0 > draw_pos[0] > 0 and screen_height-0 > draw_pos[1] > 0:
                    pygame.draw.circle(screen, "#2222aa", draw_pos, 3)
        pygame.draw.circle(screen, "#ee2222", [int(input_circle[0])*unit*smooth_zoom-smooth_offset[0], -int(input_circle[1])*unit*smooth_zoom-smooth_offset[1]], 4)

    if line_active:
        line_start_world = [
            line_start[0]*unit*smooth_zoom-smooth_offset[0],
            line_start[1]*unit*smooth_zoom-smooth_offset[1]
        ]
        line_end_world = [
            line_end[0]*unit*smooth_zoom-smooth_offset[0],
            line_end[1]*unit*smooth_zoom-smooth_offset[1]
        ]
        if not line_complete:
            pygame.draw.line(screen, color_black, line_start_world, [smooth_world_mouse_pos[0]*unit*smooth_zoom-smooth_offset[0], -smooth_world_mouse_pos[1]*unit*smooth_zoom-smooth_offset[1]], 4)
        else:
            line_color = color_black
            if line_circle_intersect:
                line_color = "#22cc22"
            pygame.draw.line(screen, line_color, line_start_world, line_end_world, 4)

    if line_complete:
        denominator = line_start[1]-line_end[1]
        numerator = -(line_start[0]-line_end[0])
        inc = 0
        frac = 0
        if numerator != 0:
            inc = denominator/numerator
            frac = Fraction(denominator, numerator)
        if f"{frac}" == "1":
            frac = ""
        elif f"{frac}" == "-1":
            frac = "-"
        y_intercept = -(inc*line_start[0]+line_start[1])
        y_intercept_frac = 0
        if numerator != 0:
            y_intercept_frac = Fraction(denominator*line_start[0]+line_start[1]*numerator, -numerator)
        y_intercept_str = f"+ {y_intercept_frac}"
        if y_intercept < 0:
            y_intercept_str = f"- {str(y_intercept_frac).replace('-', '')}"
        if y_intercept == 0:
            y_intercept_str = ""

        if denominator == 0:
            draw_text(screen, f"y = {remove_trailing_zeros(-line_start[1])}", 100, 200)
        elif numerator == 0:
            draw_text(screen, f"x = {remove_trailing_zeros(line_start[0])}", 100, 200)
        else:
            draw_text(screen, f"y = {frac}x {y_intercept_str}", 100, 200)
        
        if drawing:            
            ax = line_start[0]
            ay = line_start[1]  
            bx = line_end[0]
            by = line_end[1]
            cx = int(input_circle[0])
            cy = -int(input_circle[1])
            r = int(input_circle[2])

            ax -= cx
            ay -= cy
            bx -= cx
            by -= cy
            a = (bx - ax)**2 + (by - ay)**2
            b = 2*(ax*(bx - ax) + ay*(by - ay))
            c = ax**2 + ay**2 - r**2
            disc = b**2 - 4*a*c
            if disc > 0:
                sqrtdisc = math.sqrt(disc)
                t1 = (-b + sqrtdisc)/(2*a)
                t2 = (-b - sqrtdisc)/(2*a)
                if ((0 < t1 and t1 < 1) or (0 < t2 and t2 < 1)):
                    line_circle_intersect = True

    input_circle_text = input_circle[:] 
    if input_circle_text[input_index] == "" and inputting:
        input_circle_text[input_index] = "_"
    for i, text in enumerate(input_circle_text):
        if text.startswith("-"):    
            input_circle_text[i] = f"({text})"
    draw_text(screen, f"(x-{input_circle_text[0]})^2 + (y-{input_circle_text[1]})^2 = {input_circle_text[2]}^2", 100, 100)

    pygame.draw.circle(screen, "#ee2222", [smooth_world_mouse_pos[0]*unit*smooth_zoom-smooth_offset[0], -smooth_world_mouse_pos[1]*unit*smooth_zoom-smooth_offset[1]], 6)
    draw_text(screen, f"{world_mouse_pos[0]}, {world_mouse_pos[1]}", smooth_mouse_pos[0]+20, smooth_mouse_pos[1]+20)
    
    # update

    smooth_zoom += (zoom-smooth_zoom)/3*dt
    
    smooth_offset[0] += (offset[0]-smooth_offset[0])/3*dt
    smooth_offset[1] += (offset[1]-smooth_offset[1])/3*dt

    smooth_mouse_pos[0] += (mouse_pos[0]-smooth_mouse_pos[0])/3*dt
    smooth_mouse_pos[1] += (mouse_pos[1]-smooth_mouse_pos[1])/3*dt

    mouse_pos = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[2]:
        offset[0] -= (mouse_pos[0]-old_mouse_pos[0])
        offset[1] -= (mouse_pos[1]-old_mouse_pos[1])
    old_mouse_pos = pygame.mouse.get_pos()
    
    smooth_world_mouse_pos[0] += (world_mouse_pos[0]-smooth_world_mouse_pos[0])/2*dt
    smooth_world_mouse_pos[1] += (world_mouse_pos[1]-smooth_world_mouse_pos[1])/2*dt
    world_mouse_pos = [
        int((mouse_pos[0]+offset[0])/zoom/unit+sign(mouse_pos[0]+offset[0])/2),
        -int((mouse_pos[1]+offset[1])/zoom/unit+sign(mouse_pos[1]+offset[1])/2)
    ]

    dt = clock.tick(fps)*60/1000
    pygame.display.update()