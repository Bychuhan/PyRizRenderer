import json
from func import *
from objs import *

def parse_chart(chart_path):
    with open(chart_path, "r", encoding="utf-8") as f:
        chart = json.load(f)
        file_version = chart["fileVersion"]
        themes = chart["themes"]
        challenge_times = chart["challengeTimes"]
        bpm = chart["bPM"]
        bpm_shifts = chart["bpmShifts"]
        offset = chart["offset"]
        lines = chart["lines"]
        canvas_moves = chart["canvasMoves"]
        camera_scale = chart["cameraMove"]["scaleKeyPoints"]
        camera_move = chart["cameraMove"]["xPositionKeyPoints"]
        for i in enumerate(themes):
            for c in enumerate(i[1]["colorsList"]):
                themes[i[0]]["colorsList"][c[0]] = color_to_rgb_a(c[1], 1)
        for i in enumerate(bpm_shifts):
            if i[0] >= len(bpm_shifts)-1:
                i[1]["endTime"] = 999999999
            else:
                i[1]["endTime"] = bpm_shifts[i[0]+1]["time"]
            i[1]["value"] *= bpm
        if not bpm_shifts:
            bpm_shifts.append({"time": 0, "value": bpm, "endTime": 999999999})
        for i in challenge_times:
            i["start"] = to_real_time(bpm_shifts, i["start"])
            i["end"] = to_real_time(bpm_shifts, i["end"])
        for i in camera_move:
            i["time"] = to_real_time(bpm_shifts, i["time"])
            i["value"] *= WIDTH
        for i in enumerate(camera_move):
            if i[0] >= len(camera_move)-1:
                i[1]["endTime"] = 99999999
                i[1]["end"] = i[1]["value"]
            else:
                i[1]["endTime"] = camera_move[i[0]+1]["time"]
                i[1]["end"] = camera_move[i[0]+1]["value"]
        for i in camera_scale:
            i["time"] = to_real_time(bpm_shifts, i["time"])
        for i in enumerate(camera_scale):
            if i[0] >= len(camera_scale)-1:
                i[1]["endTime"] = 99999999
                i[1]["end"] = i[1]["value"]
            else:
                i[1]["endTime"] = camera_scale[i[0]+1]["time"]
                i[1]["end"] = camera_scale[i[0]+1]["value"]
        canvass = [Canvas(i, bpm_shifts) for i in canvas_moves]
        lines = [Line(i, bpm_shifts, canvass) for i in lines]
        return chart, file_version, themes, challenge_times, bpm, bpm_shifts, offset, lines, canvass, camera_move, camera_scale