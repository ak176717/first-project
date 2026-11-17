import subprocess
import os

font_cinzel = "/home/agent/workspace/assets/fonts/Cinzel.ttf"
font_playfair = "/home/agent/workspace/assets/fonts/PlayfairDisplay.ttf"

# Test rendering Scene 1 (10 seconds, 1280x720, 25fps)
cmd = [
    "ffmpeg", "-y",
    "-loop", "1", "-t", "10", "-i", "/home/agent/workspace/assets/scene1_meeting.jpg",
    "-filter_complex",
    f"""
    [0:v]scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,format=yuv420p[base];
    [base]split=2[color][gray];
    [gray]format=gray,edgedetect=low=0.08:high=0.25:mode=wires,negate,format=yuv420p[outline];
    [outline][color]blend=all_expr='if(lte(T,2.5), A, if(lte(T,4.5), A*(4.5-T)/2.0 + B*(T-2.5)/2.0, B))'[blended];
    [blended]zoompan=z='min(zoom+0.0006,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=250:s=1280x720:fps=25[zoomed];
    [zoomed]drawbox=y=ih-120:color=black@0.65:width=iw:height=120:t=fill[box];
    [box]drawtext=fontfile={font_cinzel}:text='SCENE I • THE SACRED MEETING AT RISHYAMUKHA':fontcolor=0xE8C170:fontsize=26:x=(w-text_w)/2:y=h-100:alpha='if(lt(t,1),t,1)',
    drawtext=fontfile={font_playfair}:text='Where Bhakti meets Divinity: Hanuman recognizes his eternal Lord Rama':fontcolor=0xF5F0E6:fontsize=20:x=(w-text_w)/2:y=h-65:alpha='if(lt(t,1.2),t-0.2,1)',
    drawtext=fontfile={font_cinzel}:text='00:00 - 00:10':fontcolor=0xA0A0A0:fontsize=14:x=w-text_w-30:y=h-35[outv]
    """,
    "-map", "[outv]",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
    "-r", "25",
    "/home/agent/workspace/assets/test_scene1.mp4"
]

print("Rendering test scene 1...")
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if res.returncode == 0:
    print("Success! Rendered test_scene1.mp4")
else:
    print("Error:", res.stderr[-1000:])
