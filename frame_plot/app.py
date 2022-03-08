import bisect
from typing import List

import kivy
import numpy as np
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget

from frame_plot.frame_extractor import extract_frames
from frame_plot.utils import overlay

kivy.require('2.1.0')


class CurrentFrameWidget(RelativeLayout):
    selected_frame_ids = ListProperty([])
    current_frame = NumericProperty(0)
    all_frames = ListProperty([])

    def __init__(self, frames, **kwargs):
        super(CurrentFrameWidget, self).__init__(**kwargs)
        Window.bind(on_key_down=self.key_action)

        self.register_event_type('on_selected_frames_change')

        self.all_frames = frames

        frame = self.all_frames[self.current_frame]

        w, h, _ = frame.shape

        self.texture = Texture.create(size=(h, w), colorfmt='bgra')
        self.texture.blit_buffer(frame.flatten())

        self.current_frame_label = Label(
            text='Current Frame: 0',
            color=(255, 255, 255),
            pos_hint={'top': 1.4}
        )

        self.add_widget(widget=Image(size=(h, w), texture=self.texture))
        self.add_widget(widget=self.current_frame_label)

    def on_selected_frames_change(self, frames: List[int]):
        pass

    def key_action(self, _, keyboard, keycode, text, modifiers):
        if keycode == 79 and self.current_frame < len(self.all_frames) - 1:
            self.current_frame += 1

        elif keycode == 80 and self.current_frame > 0:
            self.current_frame -= 1

        curr_frame_selected = self.current_frame in self.selected_frame_ids

        if keycode == 44:
            if not curr_frame_selected:
                bisect.insort(self.selected_frame_ids, self.current_frame)

            else:
                self.selected_frame_ids.remove(self.current_frame)

            self.dispatch('on_selected_frames_change', self.selected_frame_ids)

            curr_frame_selected = not curr_frame_selected

        self.current_frame_label.text = f'Current Frame: {self.current_frame}'

        if curr_frame_selected:
            self.current_frame_label.text += ' [x]'
        else:
            self.current_frame_label.text += ' [ ]'

        self.texture.blit_buffer(
            self.all_frames[self.current_frame].flatten(),
            colorfmt='rgba'
        )


class MergedFramesWidget(RelativeLayout):
    all_frames = ListProperty([])

    def __init__(self, frames, **kwargs):
        super(MergedFramesWidget, self).__init__(**kwargs)

        self.all_frames = frames

        self.add_widget(
            widget=Label(
                text='Merged Frames',
                color=(255, 255, 255),
                pos_hint={'top': 1.4}
            )
        )

        frame = self.all_frames[0]
        self.w, self.h, _ = frame.shape

        self.texture = Texture.create(
            size=(self.h, self.w),
            colorfmt='rgba'
        )

        self.add_widget(
            widget=Image(
                size=(self.h, self.w),
                texture=self.texture
            )
        )

    def merge_frame(self, origin: Widget, frames: List[int]):
        final_image = np.ones((self.w, self.h, 4), np.uint8) * 255

        for frame_id in frames:
            frame = self.all_frames[frame_id]

            final_image = overlay(final_image, frame)

        self.texture.blit_buffer(
            final_image.flatten(),
            colorfmt='rgba'
        )


class FramePlotWidget(GridLayout):
    def __init__(self, **kwargs):
        super(FramePlotWidget, self).__init__(rows=2, **kwargs)

        Window.clearcolor = (1, 1, 1, 1)

        frames = extract_frames(
            video_path='../sac_experiments/nao_videos/fcn_baseline'
            '/fcn_baseline.mpg'
        )

        current_frame_widget = CurrentFrameWidget(frames=frames)
        merged_frames_widget = MergedFramesWidget(frames=frames)

        current_frame_widget.bind(
            on_selected_frames_change=merged_frames_widget.merge_frame
        )

        self.add_widget(widget=current_frame_widget)
        self.add_widget(widget=merged_frames_widget)


class FramePlotApp(App):
    def build(self):
        return FramePlotWidget()
