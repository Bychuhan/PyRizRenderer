import random
import data
from func import *
from const import *
from easings import *
from texture import *
from dxsound import *
from core import *

NOTE_SOUNDS = (
    directSound(".\\Resources\\sounds\\tap.ogg"),
    directSound(".\\Resources\\sounds\\drag.ogg"),
)

HIT_TEXTURES: tuple[Texture] = tuple(Texture.from_path(f".\\Resources\\textures\\hits\\{i}.png") for i in range(40))

particle_easing = lambda x: 9 * x / (8.3 * x + 1)
particle_size_easing = lambda x: (((0.2078 * x - 1.6524) * x + 1.6399) * x + 0.4988)

class Canvas:
    def __init__(self, data: dict, bpm_list):
        self.index = data["index"]
        self.xmove_event = data["xPositionKeyPoints"]
        self.speed_event = data["speedKeyPoints"]
        self.bpm_list = bpm_list
        self.x = 0
        self.fp = 0
        #self.text = Text(str(self.index), FONT)
        self.preload()

    def preload(self):
        for i in self.xmove_event:
            i["time"] = to_real_time(self.bpm_list, i["time"])
            i["value"] = x_to_px(i["value"])
        for i in enumerate(self.xmove_event):
            if i[0] >= len(self.xmove_event) - 1:
                i[1]["endTime"] = 9999999
                i[1]["end"] = i[1]["value"]
            else:
                i[1]["endTime"] = self.xmove_event[i[0]+1]["time"]
                i[1]["end"] = self.xmove_event[i[0]+1]["value"]
        self.x = self.xmove_event[0]["value"]
        for i in self.speed_event:
            i["time"] = to_real_time(self.bpm_list, i["time"])
            i["value"] *= HEIGHT * (215 / 32 + SPEED) * (10 / 129)
        for i in enumerate(self.speed_event):
            if i[0] >= len(self.speed_event) - 1:
                i[1]["endTime"] = 9999999
                i[1]["end"] = i[1]["value"]
            else:
                i[1]["endTime"] = self.speed_event[i[0]+1]["time"]
                i[1]["end"] = i[1]["value"]#self.speed_event[i[0]+1]["value"]
        for i in enumerate(self.speed_event):
            i[1]["fp"] = (i[1]["value"] + i[1]["end"]) / 2 * (i[1]["endTime"] - i[1]["time"])
            if i[0] == 0:
                i[1]["lfp"] = 0
            else:
                i[1]["lfp"] = self.speed_event[i[0]-1]["lfp"] + self.speed_event[i[0]-1]["fp"]

    def get_fp(self, time):
        for i in self.speed_event:
            if time < i["endTime"]:
                p = (time - i["time"]) / (i["endTime"] - i["time"])
                #return i["lfp"] + (i["value"] + (i["value"] + (i["end"] - i["value"]) * p)) * (time - i["time"]) / 2
                return i["lfp"] + i["fp"] * p
        return None

    def update_x(self, time, event):
        if time < event[0]["endTime"]:
            return event[0]["value"] + (event[0]["end"]-event[0]["value"]) * easings[event[0]["easeType"]]((time - event[0]["time"]) / (event[0]["endTime"] - event[0]["time"]))
        else:
            event.pop(0)
            return self.update_x(time, event)

    def update_fp(self, time, event):
        if time < event[0]["endTime"]:
            p = (time - event[0]["time"]) / (event[0]["endTime"] - event[0]["time"])
            #return event[0]["lfp"] + (event[0]["value"] + (event[0]["value"] + (event[0]["end"] - event[0]["value"]) * p)) * (time - event[0]["time"]) / 2
            #搞半天才发现是瞬变。这个入是不会写匀变speed吗。
            return event[0]["lfp"] + event[0]["fp"] * p
        else:
            event.pop(0)
            return self.update_fp(time, event)

    def update(self, time):
        self.x = self.update_x(time, self.xmove_event)
        self.fp = self.update_fp(time, self.speed_event)

    def dindex(self):
        pass#self.text.render(self.x, 50*HEIGHT_SCALE, 0.2, 0.2, 0, 1, (0.5, 0.5), (0, 0, 0))

class LinePoint:
    def __init__(self, data, canvas: Canvas, endcanvas: Canvas):
        self.is_end = data["isEnd"]
        self.time = data["time"]
        self.canvas = canvas
        self.endtime = data["endTime"]
        self.position = data["xPosition"]
        self.endposition = data["end"]
        self.color, self.alpha = color_to_rgb_a(data["color"])
        self.endcolor, self.endalpha = color_to_rgb_a(data["endColor"])
        self.ease = data["easeType"]
        self.endcanvas = endcanvas
        self.fp = self.canvas.get_fp(self.time)
        self.endfp = self.endcanvas.get_fp(self.endtime)
        self.nowfp = self.fp
        self.endnowfp = self.endfp
        self.ny = Y + self.nowfp
        self.endy = Y + self.endnowfp
        self.x = 0.5
        self.endx = 0.5
        self.nowcolor = self.color
        self.nowendcolor = self.endcolor

    def update(self, time, linecolor, linealpha, scale):
        if self.is_end: return True
        if time > self.endtime and self.ny < 80 and self.endy < 80:
            return True
        self.nowfp = self.fp - self.canvas.fp
        self.endnowfp = self.endfp - self.endcanvas.fp
        self.ny = scale_position(Y + self.nowfp, scale, 1)
        self.endy = scale_position(Y + self.endnowfp, scale, 1)
        self.x = scale_position(self.position + self.canvas.x, scale, 0)
        self.endx = scale_position(self.endposition + self.endcanvas.x, scale, 0)
        if self.ny > HEIGHT and self.endy > HEIGHT: return
        if self.ny < 80 and self.endy < 80: return
        if self.x < 0 and self.endx < 0: return
        if self.x > WIDTH and self.endx > WIDTH: return
        self.nowcolor = linear_color(self.color, linecolor, linealpha)
        self.nowendcolor = linear_color(self.endcolor, linecolor, linealpha)
        self.render(scale)

    def render(self, scale):
        if self.alpha+self.endalpha <= 0: return
        draw_easings_line(self.x, self.ny, self.endx, self.endy, max(min(LINEWIDTH*scale, 10), 1), self.nowcolor, self.alpha, self.nowendcolor, self.endalpha, self.ease)

class Line:
    def __init__(self, data: dict, bpm_list, canvaslist: list[Canvas]):
        self.points = data["linePoints"]
        self.notes = data["notes"]
        self.bpm_list = bpm_list
        self.lcolor = (1, 1, 1)
        self.lalpha = 0
        self.rcolor = (1, 1, 1)
        self.ralpha = 0
        self.color_event = data["lineColor"]
        self.ring_color_event = data["judgeRingColor"]
        self.x = -999999
        self.notes = data["notes"]
        self.hits = []
        self.start_time = 0
        self.end_time = 0
        self.preload(canvaslist)

    def preload(self, canvaslist: list[Canvas]):
        for i in self.points:
            i["time"] = to_real_time(self.bpm_list, i["time"])
            i["xPosition"] *= WIDTH
        for i in enumerate(self.points):
            if i[0] >= len(self.points) - 1:
                i[1]["isEnd"] = True
                i[1]["endTime"] = i[1]["time"]
                i[1]["end"] = i[1]["xPosition"]
                i[1]["endCanvas"] = i[1]["canvasIndex"]
                i[1]["endColor"] = i[1]["color"]
            else:
                i[1]["isEnd"] = False
                i[1]["endTime"] = self.points[i[0]+1]["time"]
                i[1]["end"] = self.points[i[0]+1]["xPosition"]
                i[1]["endCanvas"] = self.points[i[0]+1]["canvasIndex"]
                i[1]["endColor"] = self.points[i[0]+1]["color"]
        for i in enumerate(self.color_event):
            i[1]["time"] = to_real_time(self.bpm_list, i[1]["time"])
            self.color_event[i[0]]["startColor"] = color_to_rgb_a(i[1]["startColor"], 1)
            self.color_event[i[0]]["endColor"] = color_to_rgb_a(i[1]["endColor"], 1)
        for i in enumerate(self.color_event):
            if i[0] >= len(self.color_event) - 1:
                i[1]["endTime"] = 9999999
            else:
                i[1]["endTime"] = self.color_event[i[0]+1]["time"]
        self.color_event = [i for i in self.color_event if i["endTime"]-i["time"]>0]
        for i in enumerate(self.ring_color_event):
            i[1]["time"] = to_real_time(self.bpm_list, i[1]["time"])
            self.ring_color_event[i[0]]["startColor"] = color_to_rgb_a(i[1]["startColor"], 1)
            self.ring_color_event[i[0]]["endColor"] = color_to_rgb_a(i[1]["endColor"], 1)
        for i in enumerate(self.ring_color_event):
            if i[0] >= len(self.ring_color_event) - 1:
                i[1]["endTime"] = 9999999
            else:
                i[1]["endTime"] = self.ring_color_event[i[0]+1]["time"]
        self.ring_color_event = [i for i in self.ring_color_event if i["endTime"]-i["time"]>0]
        self.points = [LinePoint(i, canvaslist[i["canvasIndex"]], canvaslist[i["endCanvas"]]) for i in self.points]
        self.start_time = self.points[0].time
        self.end_time = self.points[-1].time
        for i in self.notes:
            i["time"] = to_real_time(self.bpm_list, i["time"])
            i["point"] = None
            for p in self.points:
                if i["time"] >= p.time and i["time"] <= p.endtime:
                    i["point"] = p
                    break
            if i["point"] is None:
                i["point"] = self.points[0]
            if i["type"] == 2:
                i["otherInformations"][0] = to_real_time(self.bpm_list, i["otherInformations"][0])
                i["otherInformations"][1] = canvaslist[int(i["otherInformations"][1])]
        self.notes = [Note(i) for i in self.notes]

    def update_color_alpha(self, time, event):
        if time < event[0]["endTime"]:
            if time < event[0]["time"]:
                return event[0]["startColor"][:3], event[0]["startColor"][3]
            else:
                p = (time - event[0]["time"]) / (event[0]["endTime"] - event[0]["time"])
                return linear_color(event[0]["startColor"], event[0]["endColor"], p, 1)
        else:
            event.pop(0)
            return self.update_color_alpha(time, event)

    def update(self, time, scale):
        if self.color_event:
            self.lcolor, self.lalpha = self.update_color_alpha(time, self.color_event)
        if self.ring_color_event:
            self.rcolor, self.ralpha = self.update_color_alpha(time, self.ring_color_event)
        for i in self.points.copy():
            if i.update(time, self.lcolor, self.lalpha, scale):
                self.points.remove(i)
            if i.ny > HEIGHT and i.endy > HEIGHT:
                break
        if self.points:
            if time > self.points[0].time:
                p = min((time - self.points[0].time) / (self.points[0].endtime - self.points[0].time) if self.points[0].endtime - self.points[0].time > 0 else 0, 1)
                self.x = self.points[0].x + (self.points[0].endx - self.points[0].x) * easings[self.points[0].ease](p)
            else:
                self.x = self.points[0].x

    def update_note(self, time, color, scale):
        nowp = None
        for p in self.points:
            if time >= p.time and time <= p.endtime:
                nowp = p
                break
        for i in self.notes.copy():
            if i.update(time, color, nowp, scale):
                if i.type != 2:
                    self.hits.append(Hit(self.x, i.endtime))
                self.notes.remove(i)
            if i.play_hit:
                self.hits.append(Hit(self.x, i.htime))
                i.play_hit=False
            if i.y > HEIGHT+10:
                break

    def update_hit(self, time, color, scale):
        for i in self.hits.copy():
            if i.update(time, color, scale):
                self.hits.remove(i)

    def draw(self, time, scale):
        if self.ralpha > 0 and self.start_time <= time <= self.end_time:
            draw_circle(self.x, Y, 26 * WIDTH_SCALE * scale, 22 * WIDTH_SCALE * scale, self.ralpha, self.rcolor)

class Note:
    def __init__(self, data):
        self.type = data["type"]
        self.time = data["time"]
        self.point: LinePoint = data["point"]
        self.fp = self.point.canvas.get_fp(self.time)
        self.endtime = self.time
        self.endcanvas: Canvas = None
        self.endfp = 0
        self.length = 0
        if self.type == 2:
            self.endtime = data["otherInformations"][0]
            self.endcanvas = data["otherInformations"][1]
            self.endfp = self.endcanvas.get_fp(self.endtime)
            self.length = self.endfp-self.fp
        self.nowfp = self.fp
        self.nowendfp = self.endfp
        self.y = Y+self.nowfp
        self.endy = Y+self.nowendfp
        self.x = -99999
        self.play_hit = False
        self.click = False
        self.hsize = 1
        self.isend = False
        self.htime = 0
        self.p = min((self.time - self.point.time) / (self.point.endtime - self.point.time) if self.point.endtime - self.point.time > 0 else 0, 1)

    def update(self, time, color, nowpoint: LinePoint, scale):
        self.nowfp = self.fp-self.point.canvas.fp
        if self.type == 2:
            self.nowendfp = self.endfp-self.endcanvas.fp
        if time >= self.time:
            if not self.click:
                self.click = True
                if self.type == 2:
                    self.play_hit = True
                    self.htime = self.time
                NOTE_SOUNDS[1 if self.type == 1 else 0].play()
            if self.type == 2 and time < self.endtime:
                if not nowpoint is None:
                    self.point = nowpoint
                    self.p = min((time - self.point.time) / (self.point.endtime - self.point.time) if self.point.endtime - self.point.time > 0 else 0, 1)
                self.length = self.nowendfp
                self.nowfp = 0
            else:
                if not self.isend:
                    data.judges.hit += 1
                    self.isend = True
                    if self.type == 2:
                        self.play_hit = True
                        self.htime = self.endtime
                if self.type == 2 and time < self.endtime+0.25:
                    if not nowpoint is None:
                        self.point = nowpoint
                        self.p = min((time - self.point.time) / (self.point.endtime - self.point.time) if self.point.endtime - self.point.time > 0 else 0, 1)
                    self.length = 0
                    self.nowfp = 0
                    self.hsize = 1 - easings[4]((time-self.endtime)/0.25)
                else:
                    return True
        else:
            self.length = self.nowendfp-self.nowfp
        self.length *= scale
        self.x = self.point.x + (self.point.endx - self.point.x) * easings[self.point.ease](self.p)
        self.y = scale_position(Y+self.nowfp, scale, 1)
        self.endy = scale_position(Y+self.nowendfp, scale, 1)
        if not HEIGHT+10 >= self.y >= -10: return
        self.draw(color, scale)

    def draw(self, color, scale):
        _s = WIDTH_SCALE * scale
        if self.type == 1:
            draw_circle(self.x, self.y, 16 * _s, 0, 1, (0, 0, 0))
            draw_circle(self.x, self.y, 12 * _s, 0, 1, (1, 1, 1))
        else:
            if self.type == 2:
                draw_rect(self.x, self.y, 16 * _s, self.length/2, 0, 1, (0.5, 0), color)
                draw_rect(self.x, self.y+self.length/2, 16 * _s, self.length/2, 0, 1, (0.5, 0), color, (*color, 0))
                draw_rect(self.x+9 * _s, self.y, 4 * _s, self.length*0.8, 0, 1, (0.5, 0), (0, 0, 0))
                draw_rect(self.x-9 * _s, self.y, 4 * _s, self.length*0.8, 0, 1, (0.5, 0), (0, 0, 0))
                draw_rect(self.x+9 * _s, self.y+self.length*0.8, 4 * _s, self.length*0.2, 0, 1, (0.5, 0), (0, 0, 0), (0, 0, 0, 0))
                draw_rect(self.x-9 * _s, self.y+self.length*0.8, 4 * _s, self.length*0.2, 0, 1, (0.5, 0), (0, 0, 0), (0, 0, 0, 0))
            draw_circle(self.x, self.y, 20 * _s * self.hsize, 0, 1, (0, 0, 0))
            if self.type == 2:
                draw_circle(self.x, self.y, 12 * _s * self.hsize, 0, 1, (1, 1 ,1))
            else:
                draw_circle(self.x, self.y, 12 * _s, 0, 1, color)

class Hit:
    def __init__(self, x: float, startTime: float) -> None:
        self.x: float = x
        self.y: float = Y
        self.start_time: float = startTime
        self.now_time: float = self.start_time
        self.progress: float = 0.
        self.hit_i: int = 0
        self.num = random.randint(2, 4)
        self.rot = tuple(math.radians(random.uniform(0, 360)) for i in range(self.num))
        self.distance = tuple(random.uniform(100, 120) * WIDTH_SCALE for i in range(self.num))
        self.size = tuple(random.uniform(10, 20) * WIDTH_SCALE for i in range(self.num))

    def update(self, time: float, color, scale) -> None:
        self.now_time = time - self.start_time
        if self.now_time > 0.5 or self.now_time < 0:
            return True
        self.progress = self.now_time / 0.5
        self.hit_i = max(min(math.floor(self.progress * 39), 39), 0)
        self.draw(color, scale)

    def draw(self, color, scale) -> None:
        if self.progress <= 1:
            draw_texture(HIT_TEXTURES[self.hit_i], self.x, self.y, HIT_SCALE * scale, HIT_SCALE * scale, 0, 1, (0.5, 0.5), color)
        n = 0
        for r, d, s in zip(self.rot, self.distance, self.size):
            p = self.progress
            if p >= 0 and p <= 1:
                px = self.x + math.cos(r) * d * particle_easing(p) * scale
                py = self.y + math.sin(r) * d * particle_easing(p) * scale
                a = min((1 - p)*2, 1)
                size = s * particle_size_easing(p) * scale
                draw_circle(px, py, size, 0, a, color)