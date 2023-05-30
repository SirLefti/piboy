from app.ClockApp import ClockApp
from app.DebugApp import DebugApp
from app.FileManagerApp import FileManagerApp
from app.UpdateApp import UpdateApp
from app.MapApp import MapApp
from app.NullApp import NullApp
from data.IPLocationProvider import IPLocationProvider
from data.OSMTileProvider import OSMTileProvider
from interface import Interface, Input
from interface.SelfManagedTkInterrface import SelfManagedTkInterface
from piboy import AppState, load_environment
import threading

"""
This pi-boy script uses the SelfManagedTkInterface, which follows the usual mainloop approach. This makes it compatible
with MacOS and maybe other desktop environments that require UI draw calls from a main thread only. Other systems may
continue to use the other script, that is also made for the raspberry pi.
"""
if __name__ == '__main__':
    INTERFACE: Interface
    INPUT: Input

    env = load_environment()
    app_state = AppState(env.app_config.resolution, env.app_config.background)

    # wrapping key functions with local interface instance
    def on_key_left():
        app_state.on_key_left(INTERFACE)

    def on_key_right():
        app_state.on_key_right(INTERFACE)

    def on_key_up():
        app_state.on_key_up(INTERFACE)

    def on_key_down():
        app_state.on_key_down(INTERFACE)

    def on_key_a():
        app_state.on_key_a(INTERFACE)

    def on_key_b():
        app_state.on_key_b(INTERFACE)

    def on_rotary_increase():
        app_state.on_rotary_increase(INTERFACE)

    def on_rotary_decrease():
        app_state.on_rotary_decrease(INTERFACE)

    def update_display(partial=False):
        app_state.update_display(INTERFACE, partial)

    app_state.add_app(FileManagerApp()) \
        .add_app(UpdateApp()) \
        .add_app(NullApp('STAT')) \
        .add_app(NullApp('RAD')) \
        .add_app(DebugApp()) \
        .add_app(ClockApp(update_display)) \
        .add_app(MapApp(update_display, IPLocationProvider(apply_inaccuracy=True), OSMTileProvider()))

    __tk = SelfManagedTkInterface(on_key_left, on_key_right, on_key_up, on_key_down, on_key_a, on_key_b,
                                  on_rotary_increase, on_rotary_decrease,
                                  env.app_config.resolution, env.app_config.background, env.app_config.accent_dark)
    INTERFACE = __tk
    INPUT = __tk

    # initial draw
    app_state.update_display(INTERFACE)
    app_state.active_app.on_app_enter()

    # watch function has to run in the background, because Tkinter mainloop must be in the main thread
    threading.Thread(target=app_state.watch_function, args=(INTERFACE, ), daemon=True).start()

    try:
        # blocking run function
        __tk.run()
        # blocking function that updates the clock
        app_state.watch_function(INTERFACE)
    except KeyboardInterrupt:
        pass
    finally:
        INTERFACE.close()
        INPUT.close()
