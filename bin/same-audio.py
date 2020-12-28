import sys
from pydub import AudioSegment
p1 = sys.argv[1]
p2 = sys.argv[2]
s1 = AudioSegment.from_mp3(p1)
s2 = AudioSegment.from_mp3(p2)
sys.exit(0 if s1 == s2 else 1)
