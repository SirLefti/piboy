import os
from PIL import Image


resources_path = 'resources'

# file manager app icons
file_icon = Image.open(os.path.join(resources_path, 'file.png')).convert('1')
directory_icon = Image.open(os.path.join(resources_path, 'directory.png')).convert('1')


# radio app icons
stop_icon = Image.open(os.path.join(resources_path, 'stop.png')).convert('1')
previous_icon = Image.open(os.path.join(resources_path, 'previous.png')).convert('1')
play_icon = Image.open(os.path.join(resources_path, 'play.png')).convert('1')
pause_icon = Image.open(os.path.join(resources_path, 'pause.png')).convert('1')
skip_icon = Image.open(os.path.join(resources_path, 'skip.png')).convert('1')
order_icon = Image.open(os.path.join(resources_path, 'order.png')).convert('1')
random_icon = Image.open(os.path.join(resources_path, 'random.png')).convert('1')
volume_decrease_icon = Image.open(os.path.join(resources_path, 'volume_decrease.png')).convert('1')
volume_increase_icon = Image.open(os.path.join(resources_path, 'volume_increase.png')).convert('1')

# environment app icons
temperature_icon = Image.open(os.path.join(resources_path, 'temperature.png')).convert('1')
pressure_icon = Image.open(os.path.join(resources_path, 'pressure.png')).convert('1')
humidity_icon = Image.open(os.path.join(resources_path, 'humidity.png')).convert('1')

# map app icons
minus_icon = Image.open(os.path.join(resources_path, 'minus.png')).convert('1')
plus_icon = Image.open(os.path.join(resources_path, 'plus.png')).convert('1')
move_icon = Image.open(os.path.join(resources_path, 'move.png')).convert('1')
focus_icon = Image.open(os.path.join(resources_path, 'focus.png')).convert('1')

# status icons
network_icon = Image.open(os.path.join(resources_path, 'network.png')).convert('1')
gps_icon = Image.open(os.path.join(resources_path, 'gps.png')).convert('1')
