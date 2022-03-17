#!/usr/bin/env python
import os
for target in ['result']:
    os.system('rm out/frames*png {}.mp4'.format(target))
    os.system('convert -density 400 {}.pdf -background white -alpha remove out/frames-%06d.png'.format(target))
    os.system('ffmpeg -r 30 -i out/frames-%06d.png -vcodec libx264 -b:v 1M -preset veryslow {}.mp4'.format(target))
    os.system('rm out/frames*png')
