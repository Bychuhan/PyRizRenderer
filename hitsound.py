import time

from pydub import AudioSegment
from const import *

import audio_utils

def summon(Chart,audio,output):
    NoteClickAudios: dict[int, AudioSegment] = {
        0: AudioSegment.from_file(f'./Resources/sounds/tap.wav'),
        1: AudioSegment.from_file(f'./Resources/sounds/drag.wav'),
        2: AudioSegment.from_file(f'./Resources/sounds/tap.wav'),
    }

    delay = 0

    mainMixer = audio_utils.AudioMixer(AudioSegment.from_file(audio))
    notesNum = sum(len(line['notes']) for line in Chart['lines'])

    getprogresstext = lambda n: f'\rprogress: {(n / notesNum * 100):.2f}%    {n}/{notesNum}'
    print_once = lambda n, end='': print((text := getprogresstext(n)) + ' ' * (maxlength - len(text)), end=end)
    maxlength = len(getprogresstext(notesNum))

    st = time.perf_counter()
    processed = 0
    printtime = 1 / 15
    lastprint = time.time() - printtime

    for line_index, line in enumerate(Chart['lines']):
        notes = line['notes']
        for note_index, note in enumerate(notes):
            nt = note['time'] + delay
            mainMixer.mix(NoteClickAudios[note['type']], nt)
            processed += 1
            
            if time.time() - lastprint >= printtime:
                print_once(processed)
                lastprint = time.time()

    print_once(processed, end='\n')
        
    print(f'Usage time: {(time.perf_counter() - st):.2f}s')
    print('Exporting...')
    mainMixer.get().export(output)
    print('Done.')