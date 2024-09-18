import threading

from injector import Injector

from app.ClockApp import ClockApp
from app.DebugApp import DebugApp
from app.EnvironmentApp import EnvironmentApp
from app.FileManagerApp import FileManagerApp
from app.MapApp import MapApp
from app.RadioApp import RadioApp
from app.UpdateApp import UpdateApp
from environment import Environment
from interaction.SelfManagedTkInteraction import SelfManagedTkInteraction
from piboy import AppModule, AppState

"""
This pi-boy script uses the SelfManagedTkInteraction, which follows the usual mainloop approach. This makes it
compatible with MacOS and maybe other desktop environments that require UI draw calls from a main thread only. Other
systems may continue to use the other script, that is also made for the raspberry pi.
"""
if __name__ == '__main__':
    module = AppModule()
    injector = Injector([module])

    env = injector.get(Environment)
    app_state = injector.get(AppState)

    __tk = SelfManagedTkInteraction(app_state.on_key_left, app_state.on_key_right,
                                    app_state.on_key_up, app_state.on_key_down,
                                    app_state.on_key_a, app_state.on_key_b,
                                    app_state.on_rotary_increase, app_state.on_rotary_decrease, lambda _: None,
                                    env.app_config.resolution, env.app_config.background, env.app_config.accent_dark)

    module.register_external_tk_interaction(__tk)
    app_state.add_app(injector.get(FileManagerApp)) \
        .add_app(injector.get(UpdateApp)) \
        .add_app(injector.get(EnvironmentApp)) \
        .add_app(injector.get(RadioApp)) \
        .add_app(injector.get(DebugApp)) \
        .add_app(injector.get(ClockApp)) \
        .add_app(injector.get(MapApp))

    # initial draw
    app_state.update_display(__tk)
    app_state.active_app.on_app_enter()

    # watch function has to run in the background, because Tkinter mainloop must be in the main thread
    threading.Thread(target=app_state.watch_function, args=(__tk, ), daemon=True).start()

    try:
        # blocking run function
        __tk.run()
    except KeyboardInterrupt:
        pass
    finally:
        __tk.close()
