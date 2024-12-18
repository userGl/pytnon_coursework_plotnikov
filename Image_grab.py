# pip install pillow
from PIL import ImageGrab

img = ImageGrab.grabclipboard()
# or ImageGrab.grab() to grab the whole screen!
img.show()
print(img)
img.save('test1.png')
# <PIL.BmpImagePlugin.DibImageFile image mode=RGB size=380x173 at 0x16A43064DA0>