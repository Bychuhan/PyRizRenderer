import math

easings = (
    lambda t: t, # linear - 0
    lambda t: 1 - math.cos((t * math.pi) / 2), # in sine - 1
    lambda t: math.sin((t * math.pi) / 2), # out sine - 2
    lambda t: -(math.cos(math.pi * t) - 1) / 2, # io sine - 3
    lambda t: t ** 2, # in quad - 4
    lambda t: 1 - (1 - t) * (1 - t), # out quad - 5
    lambda t: 2 * (t ** 2) if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2, # io quad - 6
    lambda t: t ** 3, # in cubic - 7
    lambda t: 1 - (1 - t) ** 3, # out cubic - 8
    lambda t: 4 * (t ** 3) if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2, # io cubic - 9
    lambda t: t ** 4, # in quart - 10
    lambda t: 1 - (1 - t) ** 4, # out quart - 11
    lambda t: 8 * (t ** 4) if t < 0.5 else 1 - (-2 * t + 2) ** 4 / 2, # io quart - 12
    lambda t: 0, # zero - 13
    lambda t: 1, # one - 14
)