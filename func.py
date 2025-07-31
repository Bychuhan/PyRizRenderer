import sys
from OpenGL.GL import *
from OpenGL.GLU import gluDisk
from OpenGL.GLU import gluNewQuadric
from texture import *
from easings import *
from const import *

def draw_line(x1:float, y1:float, x2:float, y2:float,width:float,color:tuple[float,float,float,float],color2,xoffset=0):
    glColor4f(*color)
    glLineWidth(width)
    glBegin(GL_LINES)
    glVertex2f(x1+xoffset, y1)
    glColor4f(*color2)
    glVertex2f(x2+xoffset, y2)

    glEnd()

def yshh(sc, ec, h):
    sr = sc[0]
    er = ec[0]
    sg = sc[1]
    eg = ec[1]
    sb = sc[2]
    eb = ec[2]
    r = er*h+sr*(1-h)
    g = eg*h+sg*(1-h)
    b = eb*h+sb*(1-h)
    return (r, g, b)

def linear_color(scolor, ecolor, p, type=0):
    sr = scolor[0]
    er = ecolor[0]
    sg = scolor[1]
    eg = ecolor[1]
    sb = scolor[2]
    eb = ecolor[2]
    r = sr+(er-sr)*p
    g = sg+(eg-sg)*p
    b = sb+(eb-sb)*p
    if type == 0:
        return (r, g, b)
    else:
        sa = scolor[3]
        ea = ecolor[3]
        a = sa+(ea-sa)*p
        return (r, g, b), a

def draw_easings_line(x1, y1, x2, y2, width, color, alpha, endcolor, endalpha, easingtype, q=32):
    o = 1/q
    ux = x1
    uy = y1
    ua = alpha
    uc = color
    for i in range(q):
        lp = o*(i+1)
        p = easings[easingtype](lp)
        x = x1+(x2-x1)*p
        y = y1+(y2-y1)*lp
        a = alpha+(endalpha-alpha)*lp
        c = linear_color(color, endcolor, lp)
        draw_line(ux, uy, x, y, width, (*uc, ua), (*c, a))
        ux = x
        uy = y
        ua = a
        uc = c

def draw_quad(a:tuple[float,float],b:tuple[float,float],c:tuple[float,float],d:tuple[float,float],color:tuple[float,float,float,float],c2=None):
    glColor4f(*color)
    glBegin(GL_QUADS)
    glVertex2f(*a)
    glVertex2f(*b)
    if not c2 is None:
        glColor4f(*c2)
    glVertex2f(*c)
    glVertex2f(*d)

    glEnd()

def draw_rect(x, y, w, h, r, a, anchor:tuple[float] | list[float]=(0, 0), color:tuple[float] | list[float]=(1., 1., 1.), c2=None, xoffset=0):
    x_offset, y_offset = -anchor[0]*w, -anchor[1]*h
    glColor(*color, a)
    glPushMatrix()
    glTranslatef(x+xoffset, y, 0)
    glRotate(r, 0., 0., 1.)
    glBegin(GL_QUADS)
    glTexCoord2f(0.,0.)
    glVertex2f(x_offset, y_offset)
    glTexCoord2f(1.,0.)
    glVertex2f(w+x_offset, y_offset)
    if not c2 is None:
        glColor4f(*c2)
    glTexCoord2f(1.,1.)
    glVertex2f(w+x_offset, h+y_offset)
    glTexCoord2f(0.,1.)
    glVertex2f(x_offset, h+y_offset)
    glEnd()
    glPopMatrix()

def draw_texture(texture: Texture, x, y, sw, sh, r, a, anchor:tuple[float] | list[float]=(0, 0), color:tuple[float] | list[float]=(1., 1., 1.), clip:tuple[tuple[float]]=((0., 0.), (1., 0.), (1., 1.), (0., 1.)),xoffset=0):
    w, h = texture.width*sw, texture.height*sh
    x_offset, y_offset = -anchor[0]*w, -anchor[1]*h
    glColor(*color, a)
    glPushMatrix()
    glTranslatef(x+xoffset, y, 0)
    glRotate(r, 0., 0., 1.)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture.texture_id)
    glBegin(GL_QUADS)
    glTexCoord2f(*clip[0])
    glVertex2f(w * clip[0][0]+x_offset, h * clip[0][1]+y_offset)
    glTexCoord2f(*clip[1])
    glVertex2f(w * clip[1][0]+x_offset, h * clip[1][1]+y_offset)
    glTexCoord2f(*clip[2])
    glVertex2f(w * clip[2][0]+x_offset, h * clip[2][1]+y_offset)
    glTexCoord2f(*clip[3])
    glVertex2f(w * clip[3][0]+x_offset, h * clip[3][1]+y_offset)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()

def draw_text_texture(texture: Texture, x, y, sw, sh, r, a, anchor:tuple[float] | list[float]=(0, 0), color:tuple[float] | list[float]=(1., 1., 1.),xoffset=0):
    w, h = texture.width*sw, texture.height*sh
    x_offset, y_offset = -anchor[0]*w, -anchor[1]*h
    y_offset -= (texture.height-75) * sh * (1 - anchor[1])
    glColor(*color, a)
    glPushMatrix()
    glTranslatef(x+xoffset, y, 0)
    glRotate(r, 0., 0., 1.)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture.texture_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0., 0.)
    glVertex2f(x_offset, y_offset)
    glTexCoord2f(1., 0.)
    glVertex2f(w+x_offset, y_offset)
    glTexCoord2f(1., 1.)
    glVertex2f(w+x_offset, h+y_offset)
    glTexCoord2f(0., 1.)
    glVertex2f(x_offset, h+y_offset)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()

def draw_circle(x, y, r, lr, a, color, xoffset=0):
    glColor(*color, a)
    glPushMatrix()
    glTranslatef(x+xoffset, y, 0)
    gluDisk(gluNewQuadric(), lr, r, 32, 1)
    glPopMatrix()

def get_value(name, default):
    try:
        index = sys.argv.index(name)
        return sys.argv[index+1]
    except ValueError:
        return default

def tick_to_time(tick, bpm):
    return 60 / bpm * tick

def to_real_time(bpmlist, tick):
    _t = 0
    if len(bpmlist) > 1:
        for i in enumerate(bpmlist):
            if i[0] >= len(bpmlist) - 1 or bpmlist[i[0] + 1]['time'] > tick:
                _t += tick_to_time(tick - i[1]["time"], i[1]["value"])
                return _t
            else:
                _t += tick_to_time(bpmlist[i[0] + 1]['time'] - i[1]['time'], i[1]["value"])
    else:
        return tick_to_time(tick, bpmlist[0]["value"])

def x_to_px(x):
    return (x+0.5)*WIDTH

def color_to_rgb_a(color, mode=0):
    if mode == 0:
        return (color["r"]/255, color["g"]/255, color["b"]/255), color["a"]/255
    else:
        return (color["r"]/255, color["g"]/255, color["b"]/255, color["a"]/255)

def scale_position(pos, scale, type):
    o = WIDTH/2
    if type == 1:
        o = Y
    return (pos-o)*scale+o