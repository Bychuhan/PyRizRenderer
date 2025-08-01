import pygame
import sys
import time
import subprocess
import os
import win32gui
import tqdm
import data
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import gluOrtho2D
from const import *
from func import *
from tkinter.filedialog import askopenfilename
from dxsmixer import *
from easings import *

if not pygame.get_init():
    pygame.init()

pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
pygame.display.set_caption("PyRizRenderer")
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
gluOrtho2D(0, WIDTH, 0, HEIGHT)
glViewport(0, 0, WIDTH, HEIGHT)

hwnd = pygame.display.get_wm_info()['window']
clock = pygame.Clock()

if "--render" in sys.argv and "--preview" not in sys.argv:
    win32gui.ShowWindow(hwnd, False)

chart_path = (
    get_value("--chart", "") if "--chart" in sys.argv else
    askopenfilename(defaultextension=".json", filetypes=(("JSON文件", "*.json"), ("所有文件", "*.*")), title="请选择谱面文件")
)
from parse_chart import *
chart, version, themes, challenge_times, bpm, bpm_list, offset, lines, canvass, camera_move, camera_scale = parse_chart(chart_path)
glClearColor(*themes[0]["colorsList"][0])

music_path = (
    get_value("--music", "") if "--music" in sys.argv else
    askopenfilename(defaultextension=".mp3", filetypes=(("音频文件", "*.mp3 *.wav *.ogg"), ("所有文件", "*.*")), title="请选择音乐文件")
)
music = musicCls()
music.load(music_path)

theme = 0

def debug(): ...

def update_camera(time, event):
    if time < event[0]["endTime"]:
        if time < event[0]["time"]:
            return event[0]["value"]
        p = (time - event[0]["time"]) / (event[0]["endTime"] - event[0]["time"])
        return event[0]["value"] + (event[0]["end"] - event[0]["value"]) * easings[event[0]["easeType"]](p)
    else:
        event.pop(0)
        return update_camera(time, event)

def update_data():
    data.judges.combo = (
        data.judges.hit if data.judges.hit <= 5 else
        data.judges.hit * 2 - 5 if 5 <= data.judges.hit <= 8 else
        data.judges.hit * 3 - 13 if 8 <= data.judges.hit <= 11 else
        data.judges.hit * 4 - 24
    )

camerax = 0
camerascale = 1

if not "--render" in sys.argv:
    music.play()
    start_time = time.time()
    while True:
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    pygame.quit()
                    sys.exit()

        clock.tick()
        print(round(clock.get_fps()), "    \r", end="")

        now_time = time.time() - start_time

        theme = 0
        glClearColor(*themes[theme]["colorsList"][0])
        for i in enumerate(challenge_times.copy()):
            if now_time > i[1]["end"]:
                challenge_times.remove(i[1])
            elif now_time > i[1]["start"]:
                theme = i[0]+1
                glClearColor(*themes[theme]["colorsList"][0])
                break

        glClear(GL_COLOR_BUFFER_BIT)

        camerax = update_camera(now_time, camera_move)
        camerascale = update_camera(now_time, camera_scale)
        glPushMatrix()
        glTranslatef(camerax, 0, 0)

        for canvas in canvass:
            canvas.update(now_time)
        for line in lines:
            line.update(now_time, camerascale)
        draw_quad((0, 0), (WIDTH, 0), (WIDTH, 60*HEIGHT_SCALE), (0, 60*HEIGHT_SCALE), themes[theme]["colorsList"][0])
        draw_quad((0, 60*HEIGHT_SCALE), (WIDTH, 60*HEIGHT_SCALE), (WIDTH, 105*HEIGHT_SCALE), (0, 105*HEIGHT_SCALE), themes[theme]["colorsList"][0], (*themes[theme]["colorsList"][0][:3], 0))

        for line in lines:
            line.update_note(now_time, themes[theme]["colorsList"][1][:3], camerascale)
        for line in lines:
            line.draw(now_time, camerascale)
        for line in lines:
            line.update_hit(now_time, themes[theme]["colorsList"][2][:3], camerascale)
        for canvas in canvass:
            canvas.dindex()
        glPopMatrix()

        pygame.display.flip()
else:
    ispreview = "--preview" in sys.argv
    fps = int(get_value("fps", 60))
    output = get_value("output", f"{time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())}.mp4")
    delta = 1 / fps
    bitrate = int(get_value("bitrate", 15000))
    import hitsound
    try:
        hitsound.summon(chart, music_path, ".\\sound.wav")
    except TypeError:# 我不知道为什么在某些情况下pydub会炸掉。
        subprocess.run(["ffmpeg", "-i", music_path, "-ac", "2", ".\\temp.wav"])
        hitsound.summon(chart, ".\\temp.wav", ".\\sound.wav")
        if os.path.exists(".\\temp.wav"):
            os.remove(".\\temp.wav")

    ffmpeg_command = [
        "ffmpeg", "-y", "-f", "rawvideo", "-vcodec", "rawvideo", "-s", f"{WIDTH}x{HEIGHT}", "-pix_fmt", "rgb24",
        "-r", str(fps), "-i", "-", "-i", ".\\sound.wav", "-c:v", "libx264", "-b:v", f"{bitrate}k", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-strict", "experimental", "-vf", "vflip", output
    ]
    frame = int(fps * music.get_length())
    process = subprocess.Popen(ffmpeg_command, stdin = subprocess.PIPE, stderr = subprocess.DEVNULL)
    print("已开始渲染，按下 Ctrl+C 停止...")
    now_time = 0
    for i in tqdm.tqdm(range(frame), desc = "Rendering video", unit = "frames"):
        if ispreview:
            clock.tick()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                    break

        theme = 0
        glClearColor(*themes[theme]["colorsList"][0])
        for i in enumerate(challenge_times.copy())[::-1]:
            if now_time > i[1]["end"]:
                challenge_times.remove(i[1])
            elif now_time > i[1]["start"]:
                theme = i[0]+1
                glClearColor(*themes[theme]["colorsList"][0])
                break

        glClear(GL_COLOR_BUFFER_BIT)

        camerax = update_camera(now_time, camera_move)
        camerascale = update_camera(now_time, camera_scale)
        glPushMatrix()
        glTranslatef(camerax, 0, 0)

        for canvas in canvass:
            canvas.update(now_time)
        for line in lines:
            line.update(now_time, camerascale)
        draw_quad((0, 0), (WIDTH, 0), (WIDTH, 60*HEIGHT_SCALE), (0, 60*HEIGHT_SCALE), themes[theme]["colorsList"][0])
        draw_quad((0, 60*HEIGHT_SCALE), (WIDTH, 60*HEIGHT_SCALE), (WIDTH, 105*HEIGHT_SCALE), (0, 105*HEIGHT_SCALE), themes[theme]["colorsList"][0], (*themes[theme]["colorsList"][0][:3], 0))

        for line in lines:
            line.update_note(now_time, themes[theme]["colorsList"][1][:3], camerascale)
        for line in lines:
            line.draw(now_time, camerascale)
        for line in lines:
            line.update_hit(now_time, themes[theme]["colorsList"][2][:3], camerascale)
        glPopMatrix()

        if ispreview:
            pygame.display.flip()

        frame_image = glReadPixels(0, 0, WIDTH, HEIGHT, GL_RGB, GL_UNSIGNED_BYTE)
        process.stdin.write(frame_image)
        now_time += delta

    process.stdin.close()
    process.wait()

    if os.path.exists(".\\sound.wav"):
        os.remove(".\\sound.wav")

    pygame.quit()
    exit()