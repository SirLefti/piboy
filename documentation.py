import os.path
from typing import Callable, Collection

from injector import Injector, provider, singleton
from PIL import Image
from PIL.ImageFilter import GaussianBlur

from app.App import App
from app.ClockApp import ClockApp
from app.DebugApp import DebugApp
from app.EnvironmentApp import EnvironmentApp
from app.FileManagerApp import FileManagerApp
from app.MapApp import MapApp
from app.RadioApp import RadioApp
from app.UpdateApp import UpdateApp
from core.decorator import override
from environment import Environment
from piboy import AppModule, AppState, draw_base

target = './docs/apps'

class DefaultEnvironmentAppModule(AppModule):

    @singleton
    @provider
    @override
    def provide_environment(self) -> Environment:
        # make sure we have a default environment that is not loaded from file
        return Environment()

    @singleton
    @provider
    @override
    def provide_draw_callback(self, state: AppState) -> Callable[[bool], None]:
        # empty draw callback because it is not needed, and it also avoids that the display module is requested
        return lambda partial: None


def blur(image: Image.Image, bbox: tuple[int, int, int, int]) -> Image.Image:
    """Blurs the given area"""
    patch = image.crop(bbox)
    patch = patch.filter(GaussianBlur(radius=4))
    image.paste(patch, bbox)
    return image

def main():
    module = DefaultEnvironmentAppModule()
    injector = Injector([module])

    app_state = injector.get(AppState)

    app_state.add_app(injector.get(FileManagerApp)) \
        .add_app(injector.get(UpdateApp)) \
        .add_app(injector.get(EnvironmentApp)) \
        .add_app(injector.get(RadioApp)) \
        .add_app(injector.get(DebugApp)) \
        .add_app(injector.get(ClockApp)) \
        .add_app(injector.get(MapApp))

    app_state.active_app.on_app_enter()
    app_bbox = (app_state.environment.app_config.app_side_offset,
                app_state.environment.app_config.app_top_offset,
                app_state.environment.app_config.width - app_state.environment.app_config.app_side_offset,
                app_state.environment.app_config.height - app_state.environment.app_config.app_bottom_offset)
    x_offset, y_offset = app_bbox[0:2]

    # actions to perform on the app before drawing it
    pre_steps: dict[str, Collection[Callable[[App], None]]] = {
        'MAP': [lambda a: a.on_key_a() for _ in range(12)]
    }

    # actions to perform on the image after it was drawn
    post_steps: dict[str, Collection[Callable[[Image.Image], Image]]] = {
        'MAP': [lambda i: blur(i, (340, 30, 460, 90))]
    }

    for app in app_state.apps:
        app.on_app_enter()
        image = app_state.clear_buffer()
        for patch, x0, y0 in draw_base(image, app_state):
            image.paste(patch, (x0, y0))
        if app.title in pre_steps:
            for action in pre_steps[app.title]:
                action(app)
        for patch, x0, y0 in app.draw(app_state.image_buffer.crop(app_bbox), False):
            image.paste(patch, (x0 + x_offset, y0 + y_offset))
        if app.title in post_steps:
            for action in post_steps[app.title]:
                image = action(image)
        image.save(os.path.join(target, f'{app.title.lower()}.png'))
        print(f'drawn and saved {app.title} app')
        app.on_app_leave()
        app_state.next_app()

if __name__ == '__main__':
    main()
