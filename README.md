# Automatic Timelapse Exposure Adjustment [(中文)](#自动调整延时摄影的曝光补偿)
If you've ever tried to take a timelapse photo sequence during sunset like [this one](https://youtu.be/ScAM-XXEeHk), you'll need to adjust the exposure settings
on the fly to compensate for the fading sunlight. This will cause jumps in the exposure and result in an unnatural video without postprocessing.
Although I've used plugins to smooth out the exposure in After Effect, it still doesn't result in a perfectly smooth change of exposure throughout the sunset.

Therefore, I usually take the sequence in RAW and do postprocessing in Capture One. To smooth out the exposure curve, I devised an approach by incrementally adjust each photo's
exposure compensation, which I'll probably write about in another occasion. The
[notebook](https://github.com/Chen-Zhe/auto-timelapse-adjustment/blob/main/Auto%20Timelapse%20Adjustment.ipynb) should provide a basic guide to how to use it.
You'll need to locate the pixel-level location:
- The exposure adjustment text box (a single clickable point that selects the existing value and allow for overwrite)
- The exposure info text area (top left and bottom right) that shows something like `400 1/125s f/4.5` (the preceding text "ISO" in front should not be included) 

Since this process is too laborious and error-prone for human, I wrote this piece of code to automate the process.
Unfortunately, as Capture One do not support scripting on Windows, I have to use this cluncky and not-so-reliable approach of Robotic Process Automation.

Requires Python 3 and above with [`rpa`](https://github.com/tebelorg/RPA-Python)


# 自动调整延时摄影的曝光补偿

拍日落的延时摄影（比如我自己拍的[这段](https://www.bilibili.com/video/BV1wr4y1F7QH/)）一直是挺有挑战性的一件事。
拍摄的时候需要随时根据光线的变化调整曝光参数，后期则需要想着如何将以1/3档调节参数的照片做成一段曝光平滑变化的视频。
我原来用过一个After Effect的插件，但是总觉得效果没有那么令我满意.

所以我自己开发了一个日的延时摄影的后期流程。这个流程首先是基于RAW片（很奢侈，但是为了最大限度保留动态范围，效果还是很好的），然后在后期平滑缓慢地更改序列里每张照片的曝光补偿以达到
最平滑的曝光过度。但是逐张照片修改曝光补偿是个费时费力的过程，Capture One的Windows版又不支持脚本，所以我就只能用Robotic Process Automation来实现自动修改序列曝光补偿啦。这样做虽然慢，
但至少在运行的时候我可以刷手机，而且也不用担心调错参数了。

这个[notebook](https://github.com/Chen-Zhe/auto-timelapse-adjustment/blob/main/Auto%20Timelapse%20Adjustment.ipynb)可以作为简易的参考。你需要指定在自己屏幕上Capture One的这两个位置：
- 曝光补偿数值输入框（单击时可以选中所有内容，然后直接覆写）
- 照片曝光信息区（左上和右下）。显示的信息应为`400 1/125s f/4.5`(前面的ISO不能在框内) 

需要Python 3或以上以及[`rpa`](https://github.com/tebelorg/RPA-Python)库
