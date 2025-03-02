#!c:/python310/python.exe
# -*-coding:utf-8 -*-
import tqdm
import whisper
import srt
from typing import List, Tuple
import srt_trans


def transcribe_audio(mp4_file: str, model_size: str = "medium", verbose=None, prompt=None) -> List[Tuple[float, float, str]]:
    model = whisper.load_model(model_size)
    result = model.transcribe(mp4_file, language='ja',
                              verbose=verbose, initial_prompt=prompt)
    return [(segment['start'], segment['end'], segment['text']) for segment in result['segments']]


def create_srt(subtitles: List[Tuple[float, float, str]], output_file: str):
    srt_entries = []
    for start, end, text in tqdm.tqdm(subtitles):
        srt_trans.process_translation(text)
    translations = srt_trans.get_translations()
    print(len(translations),len(subtitles))
    for i, (start, end, text) in tqdm.tqdm(enumerate(subtitles)):
        srt_entries.append(srt.Subtitle(index=len(srt_entries) + 1,
                                        start=srt.timedelta(seconds=start),
                                        end=srt.timedelta(seconds=end),
                                        content=srt_trans.trans(text, translations[i])))

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(srt.compose(srt_entries))


def mp4srt(mp4_file: str, output_srt_file: str, verbose=None, prompt=None):
    import json
    try:
        with open("temp_subtitles.json", "r", encoding="utf-8") as f:
            subtitles = json.load(f)
    except:
        subtitles = transcribe_audio(mp4_file, verbose=verbose, prompt=prompt)
    with open("temp_subtitles.json", "w", encoding="utf-8") as f:
        json.dump(subtitles, f, ensure_ascii=False, indent=4)
    create_srt(subtitles, output_srt_file)
    return subtitles


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python mp4srt.py <input_mp4> <output_srt>")
        exit()
    mp4_file = sys.argv[1]
    output_srt_file = sys.argv[2]
    prompt = sys.argv[3] if len(sys.argv) > 3 else None
    mp4srt(mp4_file, output_srt_file, True, prompt)
