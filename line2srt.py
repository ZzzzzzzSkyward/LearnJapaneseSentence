import tqdm
import srt_trans
import srt
from datetime import timedelta
from typing import List, Tuple


def parse_subtitle_line(file_path: str) -> List[Tuple[float, float, str]]:
    subtitles = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # 解析行格式: [00:33.000 --> 00:34.000] 又见面了。
            line = line.strip()
            if line:
                time_part, text = line.split(']', 1)
                time_part = time_part.strip('[')
                start_time_str, end_time_str = time_part.split(' --> ')

                start_time = convert_to_seconds(start_time_str)
                end_time = convert_to_seconds(end_time_str)

                subtitles.append((start_time, end_time, text.strip()))

    return subtitles


def convert_to_seconds(time_str: str) -> float:
    """ Convert time string format 'MM:SS.sss' to seconds. """
    minutes, seconds = time_str.split(':')
    total_seconds = int(minutes) * 60 + float(seconds)
    return total_seconds


def create_srt(subtitles: List[Tuple[float, float, str]], output_file: str):
    srt_entries = []
    for index, (start, end, text) in tqdm.tqdm(enumerate(subtitles)):
        srt_entries.append(srt.Subtitle(index=index + 1,
                                        start=timedelta(seconds=start),
                                        end=timedelta(seconds=end),
                                        content=srt_trans.trans(text)))

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(srt.compose(srt_entries))


def line2srt(input_file: str, output_file: str):
    subtitles = parse_subtitle_line(input_file)
    create_srt(subtitles, output_file)
    return subtitles


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python line2srt.py <input_file> <output_file>")
        exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    line2srt(input_file, output_file)
