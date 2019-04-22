#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Thu Apr 21 12:10:56 2005

# Papagayo-NG, a lip-sync tool for use with several different animation suites
# Original Copyright (C) 2005 Mike Clifton
# Contact information at http://www.lostmarble.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import math, random
import PySide2.QtCore as QtCore
import PySide2.QtGui as QtGui
import PySide2.QtWidgets as QtWidgets
#from PySide2.QtWidgets import QtGui, QtCore, QtWidgets

from anytree import Node
import anytree.util

from LipsyncDoc import *

fill_color = QtGui.QColor(162, 205, 242)
line_color = QtGui.QColor(30, 121, 198)
frame_col = QtGui.QColor(192, 192, 192)
frame_text_col = QtGui.QColor(64, 64, 64)
play_back_col = QtGui.QColor(255, 127, 127)
play_fore_col = QtGui.QColor(209, 102, 121)
play_outline_col = QtGui.QColor(128, 0, 0)
text_col = QtGui.QColor(64, 64, 64)
phrase_fill_col = QtGui.QColor(205, 242, 162)
phrase_outline_col = QtGui.QColor(121, 198, 30)
word_fill_col = QtGui.QColor(242, 205, 162)
word_outline_col = QtGui.QColor(198, 121, 30)
phoneme_fill_col = QtGui.QColor(231, 185, 210)
phoneme_outline_col = QtGui.QColor(173, 114, 146)
font = QtGui.QFont("Swiss", 6)

# default_sample_width = 2
# default_samples_per_frame = 4
default_sample_width = 4
default_samples_per_frame = 2


class SceneWithDrag(QtWidgets.QGraphicsScene):
    def dragEnterEvent(self, e):
        e.acceptProposedAction()

    def dropEvent(self, e):
        # find item at these coordinates
        item = self.itemAt(e.scenePos(), QtGui.QTransform())
        if item:
            if item.setAcceptDrops:
                # pass on event to item at the coordinates
                item.dropEvent(e)
                try:
                    item.dropEvent(e)
                except RuntimeError:
                    pass  # This will suppress a Runtime Error generated when dropping into a widget with no MyProxy

    def dragMoveEvent(self, e):
        e.acceptProposedAction()


class MovableButton(QtWidgets.QPushButton):
    def __init__(self, lipsync_object, style, wfv_parent,  phoneme_offset=None):
        super(MovableButton, self).__init__(lipsync_object.text, None)
        self.title = lipsync_object.text
        self.node = None
        self.phoneme_offset = phoneme_offset
        self.lipsync_object = lipsync_object
        self.setStyleSheet(style)
        self.is_resizing = False
        self.resize_origin = 0  # 0 = left 1 = right
        self.wfv_parent = wfv_parent
        self.hotspot = None
        # We need the parent element if it exists, and the previous and next element if they exist
        # When we move we need to check for the boundaries dictated by the parent and neighbours.
        # Inform our neighbours after we finished moving, should be automatic if references are used for that.
        # Getting new neighbours or loosing some is problematic.
        # Maybe a structure with all elements makes sense, it's a bit circular but should work.
        # It should somehow represent the actual data so that we can find our neighbours...
        # So the mov_widget_list should maybe be a list of lists instead
        # But to find our position in that we would have to parse through the whole list then...

    def is_phoneme(self):
        # voice = 0, phrase = 1, word = 2, phoneme = 3
        if self.node.depth == 3:
            return True
        else:
            return False

    def is_word(self):
        # voice = 0, phrase = 1, word = 2, phoneme = 3
        if self.node.depth == 2:
            return True
        else:
            return False

    def is_phrase(self):
        # voice = 0, phrase = 1, word = 2, phoneme = 3
        if self.node.depth == 1:
            return True
        else:
            return False

    def after_reposition(self):
        if self.is_phoneme():
            self.setGeometry(self.convert_to_pixels(self.lipsync_object.frame),
                             self.y(), self.convert_to_pixels(self.get_frame_size()), self.height())
        else:
            self.setGeometry(self.convert_to_pixels(self.lipsync_object.start_frame),
                             self.y(), self.convert_to_pixels(self.get_frame_size()), self.height())
        self.update()

    def get_min_size(self):
        # An object should be at least be able to contain all it's phonemes since only 1 phoneme per frame is allowed.
        if self.is_phoneme():
            num_of_phonemes = 1
        else:
            num_of_phonemes = 0
            for descendant in self.node.descendants:
                if descendant.name.is_phoneme():
                    num_of_phonemes += 1
        return num_of_phonemes

    def get_frame_size(self):
        if self.is_phoneme():
            return 1
        else:
            return self.lipsync_object.end_frame - self.lipsync_object.start_frame

    def has_shrink_room(self):
        if self.is_phoneme():
            return False
        else:
            if self.get_min_size() >= self.get_frame_size():
                return False
            else:
                return True

    def has_left_sibling(self):
        left_sibling = False
        try:
            left_sibling = bool(self.get_left_sibling())
        except AttributeError:
            left_sibling = False
        return left_sibling

    def has_right_sibling(self):
        right_sibling = False
        try:
            right_sibling = bool(self.get_right_sibling())
        except AttributeError:
            right_sibling = False
        return right_sibling

    def get_left_max(self):
        left_most_pos = 0
        try:
            temp = self.get_left_sibling().name
            if not temp.lipsync_object.is_phoneme:
                left_most_pos = temp.lipsync_object.end_frame
            else:
                left_most_pos = temp.lipsync_object.frame + 1
        except AttributeError:
            if self.node.depth > 1:
                left_most_pos = self.node.parent.name.lipsync_object.start_frame
            else:
                left_most_pos = 0
        return left_most_pos

    def get_right_max(self):
        right_most_pos = 0
        try:
            temp = self.get_right_sibling().name
            if not temp.lipsync_object.is_phoneme:
                right_most_pos = temp.lipsync_object.start_frame
            else:
                right_most_pos = temp.lipsync_object.frame
        except AttributeError:
            if self.node.depth > 1:
                right_most_pos = self.node.parent.name.lipsync_object.end_frame
            else:
                right_most_pos = self.lipsync_object.end_frame  # Last Phrase
        return right_most_pos

    def convert_to_pixels(self, frame_pos):
        return frame_pos * self.wfv_parent.frame_width
        # if self.lipsync_object.is_phoneme:
        #     current_frame_pos = self.lipsync_object.frame
        # else:
        #     current_frame_pos = self.lipsync_object.start_frame
        # factor = self.x() / current_frame_pos
        # return frame_pos * factor

    def convert_to_frames(self, pixel_pos):
        return pixel_pos / self.wfv_parent.frame_width
        # if self.lipsync_object.is_phoneme:
        #     current_frame_pos = self.lipsync_object.frame
        # else:
        #     current_frame_pos = self.lipsync_object.start_frame
        # factor = current_frame_pos / self.x()
        # return pixel_pos * factor

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            if (self.width() - event.x()) < 10:
                if not self.lipsync_object.is_phoneme:
                    self.is_resizing = True
                    self.resize_origin = 1
            # elif event.x() < 10:
            #     if not self.lipsync_object.is_phoneme:
            #         self.is_resizing = True
            #         self.resize_origin = 0
            else:
                self.is_resizing = False
        if self.is_resizing:
            if self.resize_origin == 1:  # start resize from right side
                if round(self.convert_to_frames(event.x() + self.x())) >= self.lipsync_object.start_frame + self.get_min_size():
                    if round(self.convert_to_frames(event.x() + self.x())) <= self.get_right_max():
                        self.lipsync_object.end_frame = round(self.convert_to_frames(event.x() + self.x()))
                        self.resize(self.convert_to_pixels(self.lipsync_object.end_frame) -
                                    self.convert_to_pixels(self.lipsync_object.start_frame), self.height())
            # elif self.resize_origin == 0:  # start resize from left side
            #     if round(self.convert_to_frames(event.x() + self.x())) < self.lipsync_object.end_frame:
            #         if round(self.convert_to_frames(event.x() + self.x())) >= self.get_left_max():
            #             self.lipsync_object.start_frame = round(self.convert_to_frames(event.x() + self.x()))
            #             new_length = self.convert_to_pixels(self.lipsync_object.end_frame) - self.convert_to_pixels(self.lipsync_object.start_frame)
            #             self.resize(new_length, self.height())
            #             self.move(self.convert_to_pixels(self.lipsync_object.start_frame), self.y())
        else:
            mime_data = QtCore.QMimeData()
            drag = QtGui.QDrag(self)
            drag.setMimeData(mime_data)
            drag.setHotSpot(event.pos() - self.rect().topLeft())
            print("HotSpot:")
            print(drag.hotSpot())
            self.hotspot = drag.hotSpot().x()
            # PyQt5 and PySide use different function names here, likely a Qt4 vs Qt5 problem.
            try:
                exec("dropAction = drag.exec(QtCore.Qt.MoveAction)")  # Otherwise we can't catch it and it will crash...
            except (SyntaxError, AttributeError):
                dropAction = drag.start(QtCore.Qt.MoveAction)

    def mousePressEvent(self, event):
        # Some debugging output
        # try:
        #     print("MyLeftSibling: " + self.get_left_sibling().name.title)
        # except AttributeError:
        #     pass
        # try:
        #     print("MyRightSibling: " + self.get_right_sibling().name.title)
        # except AttributeError:
        #     pass
        # print("LeftMax: " + str(self.get_left_max()))
        # print("RightMax: " + str(self.get_right_max()))
        # print("BeginningPixel: " + str(self.x()))
        # if self.lipsync_object.is_phoneme:
        #     print("BeginningFrame: " + str(self.lipsync_object.frame))
        # else:
        #     print("BeginningFrame: " + str(self.lipsync_object.start_frame))
        # print("EndPixel: " + str(self.x() + self.width()))
        # if self.lipsync_object.is_phoneme:
        #     print("EndFrame: " + str(self.lipsync_object.frame))
        # else:
        #     print("EndFrame: " + str(self.lipsync_object.end_frame))
        # if self.lipsync_object.is_phoneme:
        #     print("Converted_to_Pixel: " + str(self.convert_to_pixels(self.lipsync_object.frame)))
        # else:
        #     print("Converted_to_Pixel: " + str(self.convert_to_pixels(self.lipsync_object.start_frame)))
        # print("Converted_to_frame: " + str(self.convert_to_frames(self.x())))
        # print("ClickedPixel: " + str(self.x() + event.x()))
        # print("ClickedFrame: " + str(self.convert_to_frames(self.x() + event.x())))

        # End of debugging output
        if event.button() == QtCore.Qt.RightButton and self.is_word():
            # manually enter the pronunciation for this word
            dlg = PronunciationDialog(self, self.wfv_parent.doc.parent.phonemeset.set)
            dlg.word_label.setText(dlg.word_label.text() + ' ' + self.text())
            dlg.setWindowTitle(self.title)
            prev_phoneme_list = ""
            for p in self.node.children:
                prev_phoneme_list += " " + p.name.lipsync_object.text
            dlg.phoneme_ctrl.setText(prev_phoneme_list)
            if dlg.exec_():
                list_of_new_phonemes = dlg.phoneme_ctrl.text().split()
                if list_of_new_phonemes:
                    if list_of_new_phonemes != prev_phoneme_list.split():
                        old_childnodes = self.node.children
                        print(self.wfv_parent.items())
                        for old_node in old_childnodes:
                            for proxy in self.wfv_parent.items():
                                try:
                                    if proxy.widget() == old_node.name:
                                        self.wfv_parent.scene().removeItem(proxy)
                                except AttributeError:
                                    pass
                        old_childnodes = []
                        self.node.children = []
                        self.lipsync_object.phonemes = []
                        font_metrics = QtGui.QFontMetrics(font)
                        text_width, text_height = font_metrics.width("Ojyg"), font_metrics.height() + 6
                        phoneme_col_string = "color: #000000; background-color:rgb({0},{1},{2});".format(
                            phoneme_fill_col.red(),
                            phoneme_fill_col.green(),
                            phoneme_fill_col.blue())
                        phoneme_col_string += "border:1px solid rgb({0},{1},{2});".format(phoneme_outline_col.red(),
                                                                                          phoneme_outline_col.green(),
                                                                                          phoneme_outline_col.blue())
                        for phoneme_count, p in enumerate(list_of_new_phonemes):
                            phoneme = LipsyncPhoneme()
                            phoneme.text = p
                            phoneme.frame = self.lipsync_object.start_frame + phoneme_count
                            self.lipsync_object.phonemes.append(phoneme)
                            temp_button = MovableButton(phoneme, phoneme_col_string, self.wfv_parent, phoneme_count % 2)
                            temp_button.node = Node(temp_button, parent=self.node)
                            temp_scene_widget = self.wfv_parent.scene().addWidget(temp_button)
                            temp_scene_widget.setParent(self.wfv_parent)
                            temp_scene_widget.setGeometry(QtCore.QRect(phoneme.frame * self.wfv_parent.frame_width,
                                                                       self.wfv_parent.height() - (
                                                                                   self.wfv_parent.horizontalScrollBar().height() * 1.5) - (
                                                                                   text_height + (text_height * (phoneme_count % 2))),
                                                                       self.wfv_parent.frame_width,
                                                                       text_height))
                            temp_scene_widget.setZValue(99)

    def mouseDoubleClickEvent(self, event):
        if not self.is_phoneme():
            print("Double Click: ")
            print(self.text())
            start = self.lipsync_object.start_frame / self.wfv_parent.doc.fps
            length = (self.lipsync_object.end_frame - self.lipsync_object.start_frame) / self.wfv_parent.doc.fps
            self.wfv_parent.doc.sound.play_segment(start, length)

    def mouseReleaseEvent(self, event):
        if self.is_resizing:
            self.reposition_descendants()
            self.is_resizing = False

    def reposition_descendants(self):
        # These reposition_word and phoneme methods are not really taking account their parent
        # We have to run through the children ourselves and reposition and resize them to fit.
        repositioned = False
        if self.is_phrase():
            repositioned = True
            for word in self.node.children:
                self.lipsync_object.reposition_word(word.name.lipsync_object)
        elif self.is_word():
            repositioned = True
            for phoneme in self.node.children:
                self.lipsync_object.reposition_phoneme(phoneme.name.lipsync_object)
        if repositioned:
            for descendant in self.node.descendants:
                descendant.name.after_reposition()

    def get_left_sibling(self):
        return anytree.util.leftsibling(self.node)

    def get_right_sibling(self):
        return anytree.util.rightsibling(self.node)

    def __del__(self):
        try:
            self.deleteLater()
        except RuntimeError:
            pass


class WaveformView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(WaveformView, self).__init__(parent)
        self.setScene(SceneWithDrag(self))
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.setAcceptDrops(True)
        self.setMouseTracking(True)

        # Other initialization
        self.doc = None
        self.is_dragging = False
        self.basic_scrubbing = False
        self.cur_frame = 0
        self.old_frame = 0
        self.sample_width = default_sample_width
        self.samples_per_frame = default_samples_per_frame
        self.samples_per_sec = 24 * self.samples_per_frame
        self.frame_width = self.sample_width * self.samples_per_frame
        self.phrase_bottom = 16
        self.word_bottom = 32
        self.phoneme_top = 128
        self.waveform_polygon = None
        self.wv_height = 1
        self.temp_phrase = None
        self.temp_word = None
        self.temp_phoneme = None
        self.temp_button = None
        self.draw_play_marker = False
        self.num_samples = 0
        self.list_of_lines = []
        self.amp = []
        self.temp_play_marker = None
        self.scroll_position = 0
        self.first_update = True
        self.node = None
        self.did_resize = None
        self.main_node = None
        # self.scene().setSceneRect(0,0,self.width(),self.height())

        print("LoadedWaveFormView")

    def dragEnterEvent(self, e):
        print("DragEnter!")
        e.accept()

    def dragMoveEvent(self, e):
        position = e.pos()
        new_x = e.pos().x() + self.horizontalScrollBar().value()
        dropped_widget = e.source()
        if new_x > dropped_widget.get_left_max() * self.frame_width:
            if new_x + dropped_widget.width() < dropped_widget.get_right_max() * self.frame_width:
                dropped_widget.move(new_x, dropped_widget.y())
                # after moving save the position and align to the grid based on that. Hacky but works!
                if dropped_widget.lipsync_object.is_phoneme:
                    dropped_widget.lipsync_object.frame = round(new_x / self.frame_width)
                    dropped_widget.move(dropped_widget.lipsync_object.frame * self.frame_width, dropped_widget.y())
                else:
                    dropped_widget.lipsync_object.start_frame = round(dropped_widget.x() / self.frame_width)
                    dropped_widget.lipsync_object.end_frame = round((dropped_widget.x() + dropped_widget.width()) / self.frame_width)
                    dropped_widget.move(dropped_widget.lipsync_object.start_frame * self.frame_width, dropped_widget.y())
                    # Move the children!
                    dropped_widget.reposition_descendants()
        e.accept()

    def set_frame(self, frame):
        self.centerOn(self.temp_play_marker)
        self.temp_play_marker.setPos(frame * self.frame_width, 0)
        self.update()
        self.scene().update()

    def drawBackground(self, painter, rect):
        background_brush = QtGui.QBrush(QtGui.QColor(255, 255, 255), QtCore.Qt.SolidPattern)
        painter.fillRect(rect, background_brush)
        if self.doc is not None:
            pen = QtGui.QPen(frame_col)
            # pen.setWidth(5)
            painter.setPen(pen)
            painter.setFont(font)

            first_sample = 0
            last_sample = len(self.amp)
            bg_height = self.height() + self.horizontalScrollBar().height()
            half_client_height = bg_height / 2
            font_metrics = QtGui.QFontMetrics(font)
            text_width, top_border = font_metrics.width("Ojyg"), font_metrics.height() * 2
            x = first_sample * self.sample_width
            frame = first_sample / self.samples_per_frame
            fps = int(round(self.doc.fps))
            sample = first_sample
            self.list_of_lines = []
            list_of_textmarkers = []
            for i in range(int(first_sample), int(last_sample)):
                if (i + 1) % self.samples_per_frame == 0:
                    frame_x = (frame + 1) * self.frame_width
                    if (self.frame_width > 2) or ((frame + 1) % fps == 0):
                        self.list_of_lines.append(QtCore.QLineF(frame_x, top_border, frame_x, bg_height))
                    # draw frame label
                    if (self.frame_width > 30) or ((int(frame) + 1) % 5 == 0):
                        self.list_of_lines.append(QtCore.QLineF(frame_x, 0, frame_x, top_border))
                        self.list_of_lines.append(QtCore.QLineF(frame_x + 1, 0, frame_x + 1, bg_height))
                        temp_rect = QtCore.QRectF(int(frame_x + 4), font_metrics.height() - 2, text_width, top_border)
                        # Positioning is a bit different in QT here
                        list_of_textmarkers.append((temp_rect, str(int(frame + 1))))
                x += self.sample_width
                sample += 1
                if sample % self.samples_per_frame == 0:
                    frame += 1
            painter.drawLines(self.list_of_lines)
            for text_marker in list_of_textmarkers:
                painter.drawText(text_marker[0], QtCore.Qt.AlignLeft, text_marker[1])
            if self.first_update:
                if self.waveform_polygon:
                    self.setSceneRect(self.waveform_polygon.polygon().boundingRect())
                    self.scene().setSceneRect(self.waveform_polygon.polygon().boundingRect())
                    self.first_update = False

    def update_drawing(self, redraw_all=True):
        self.draw()

    def draw(self):
        print("Begin Drawing")

    def create_waveform(self):
        if self.waveform_polygon in self.scene().items():
            self.scene().removeItem(self.waveform_polygon)
        first_sample = 0
        last_sample = len(self.amp)
        top_and_bottom_space = 4  # This should in theory provide a bit of space at the top and bottom
        self.wv_height = self.height() + self.horizontalScrollBar().height() - top_and_bottom_space
        half_client_height = self.wv_height / 2
        x = first_sample * self.sample_width
        frame = first_sample / self.samples_per_frame
        sample = first_sample
        frame_rectangle_polygon_upper = []
        frame_rectangle_polygon_lower = []
        for i in range(int(first_sample), int(last_sample)):
            height = round(self.wv_height * self.amp[i]) + (top_and_bottom_space / 2)
            half_height = height / 2
            if self.draw_play_marker and (frame == self.cur_frame):
                pass
            else:
                # frame_rectangle_list.append((x, half_client_height - half_height, self.sample_width+1, height))
                # self.scene().addRect(x, half_client_height - half_height, self.sample_width+1, height, line_color, fill_color)
                frame_rectangle_polygon_upper.append((x, half_client_height - half_height))
                frame_rectangle_polygon_upper.append((x + self.sample_width, half_client_height - half_height))
                frame_rectangle_polygon_lower.append((x, half_client_height + half_height))
                frame_rectangle_polygon_lower.append((x + self.sample_width, half_client_height + half_height))
            x += self.sample_width
            sample += 1
            if sample % self.samples_per_frame == 0:
                frame += 1
        frame_rectangle_polygon_lower.reverse()
        temp_polygon = QtGui.QPolygonF()
        for coordinates in (frame_rectangle_polygon_upper + frame_rectangle_polygon_lower):
            temp_polygon.append(QtCore.QPointF(coordinates[0], coordinates[1]))
        self.waveform_polygon = self.scene().addPolygon(temp_polygon, line_color, fill_color)
        self.waveform_polygon.setZValue(1)

    def create_movbuttons(self):
        if self.doc is not None:
            phrase_col_string = "color: #000000; background-color:rgb({0},{1},{2});".format(phrase_fill_col.red(),
                                                                                            phrase_fill_col.green(),
                                                                                            phrase_fill_col.blue())
            phrase_col_string += "background-image: url(:/rsrc/marker.png); background-repeat: repeat-y; background-position: right;"
            phrase_col_string += "border:1px solid rgb({0},{1},{2});".format(phrase_outline_col.red(),
                                                                             phrase_outline_col.green(),
                                                                             phrase_outline_col.blue())

            word_col_string = "color: #000000; background-color:rgb({0},{1},{2});".format(word_fill_col.red(),
                                                                                          word_fill_col.green(),
                                                                                          word_fill_col.blue())
            word_col_string += "background-image: url(:/rsrc/marker.png); background-repeat: repeat-y; background-position: right;"

            word_col_string += "border:1px solid rgb({0},{1},{2});".format(word_outline_col.red(),
                                                                           word_outline_col.green(),
                                                                           word_outline_col.blue())
            phoneme_col_string = "color: #000000; background-color:rgb({0},{1},{2});".format(phoneme_fill_col.red(),
                                                                                             phoneme_fill_col.green(),
                                                                                             phoneme_fill_col.blue())
            phoneme_col_string += "border:1px solid rgb({0},{1},{2});".format(phoneme_outline_col.red(),
                                                                              phoneme_outline_col.green(),
                                                                              phoneme_outline_col.blue())
            font_metrics = QtGui.QFontMetrics(font)
            text_width, top_border = font_metrics.width("Ojyg"), font_metrics.height() * 2
            text_width, text_height = font_metrics.width("Ojyg"), font_metrics.height() + 6
            top_border += 4

            self.main_node = Node(self.doc.current_voice.text)  # Not actually needed, but should make everything a bit easier

            for phrase in self.doc.current_voice.phrases:
                self.temp_button = MovableButton(phrase, phrase_col_string, self)
                self.temp_button.node = Node(self.temp_button, parent=self.main_node)
                temp_scene_widget = self.scene().addWidget(self.temp_button)
                temp_scene_widget.setParent(self)
                temp_scene_widget.setGeometry(QtCore.QRect(phrase.start_frame * self.frame_width, top_border,
                                              (phrase.end_frame - phrase.start_frame) * self.frame_width + 1,
                                              text_height))
                temp_scene_widget.setZValue(99)
                self.temp_phrase = self.temp_button
                word_count = 0
                for word in phrase.words:
                    self.temp_button = MovableButton(word, word_col_string, self)
                    self.temp_button.node = Node(self.temp_button, parent=self.temp_phrase.node)
                    temp_scene_widget = self.scene().addWidget(self.temp_button)
                    temp_scene_widget.setParent(self)
                    temp_scene_widget.setGeometry(QtCore.QRect(word.start_frame * self.frame_width,
                                                  top_border + 4 + text_height + (text_height * (word_count % 2)),
                                                  (word.end_frame - word.start_frame ) * self.frame_width + 1,
                                                  text_height))
                    temp_scene_widget.setZValue(99)
                    self.temp_word = self.temp_button
                    word_count += 1
                    phoneme_count = 0
                    for phoneme in word.phonemes:
                        self.temp_button = MovableButton(phoneme, phoneme_col_string, self, phoneme_count % 2)
                        self.temp_button.node = Node(self.temp_button, parent=self.temp_word.node)
                        temp_scene_widget = self.scene().addWidget(self.temp_button)
                        temp_scene_widget.setParent(self)
                        temp_scene_widget.setGeometry(QtCore.QRect(phoneme.frame * self.frame_width,
                                                      self.height() - (self.horizontalScrollBar().height()*1.5) - (text_height + (text_height * (phoneme_count % 2))),
                                                      self.frame_width,
                                                      text_height))
                        temp_scene_widget.setZValue(99)
                        self.temp_phoneme = self.temp_button
                        phoneme_count += 1

    def set_document(self, document):
        self.doc = document
        if (self.doc is not None) and (self.doc.sound is not None):
            self.frame_width = self.sample_width * self.samples_per_frame
            duration = self.doc.sound.Duration()
            time = 0.0
            sample_dur = 1.0 / self.samples_per_sec
            max_amp = 0.0
            self.amp = []
            while time < duration:
                self.num_samples += 1
                amp = self.doc.sound.GetRMSAmplitude(time, sample_dur)
                self.amp.append(amp)
                if amp > max_amp:
                    max_amp = amp
                time += sample_dur
            # normalize amplitudes
            max_amp = 0.95 / max_amp
            for i in range(len(self.amp)):
                self.amp[i] *= max_amp
            self.scene().clear()
            self.scene().update()
            self.create_movbuttons()
        self.create_waveform()
        self.temp_play_marker = self.scene().addRect(0, 1, self.frame_width + 1, self.height(),
                                                     QtGui.QPen(play_outline_col),
                                                     QtGui.QBrush(play_fore_col, QtCore.Qt.SolidPattern))
        self.temp_play_marker.setZValue(1000)
        self.temp_play_marker.setOpacity(0.5)
        self.temp_play_marker.setVisible(False)

    def on_slider_change(self, value):
        self.scroll_position = value

    def wheelEvent(self, event):
        self.scroll_position = self.horizontalScrollBar().value()+(event.delta()/1.2)
        self.horizontalScrollBar().setValue(self.scroll_position)

    def resizeEvent(self, event):
        update_rect = self.scene().sceneRect()
        width_factor = 1  # Only the height needs to change.
        # try:
        #     width_factor = self.width() / update_rect.width()
        # except ZeroDivisionError:
        #     width_factor = 1

        try:
            height_factor = event.size().height() / event.oldSize().height()
        except ZeroDivisionError:
            height_factor = 1
        update_rect.setHeight(event.size().height())
        if self.doc:
            update_rect.setWidth(self.waveform_polygon.polygon().boundingRect().width())
            self.setSceneRect(update_rect)
            self.scene().setSceneRect(update_rect)
            origin_x, origin_y = 0, 0
            height_factor = height_factor * self.waveform_polygon.transform().m22()  # We need to add the factors
            self.waveform_polygon.setTransform(QtGui.QTransform().translate(
                origin_x, origin_y).scale(width_factor, height_factor).translate(-origin_x, -origin_y))
            # We need to at least update the Y Position of the Phonemes
            font_metrics = QtGui.QFontMetrics(font)
            text_width, top_border = font_metrics.width("Ojyg"), font_metrics.height() * 2
            text_width, text_height = font_metrics.width("Ojyg"), font_metrics.height() + 6
            top_border += 4
            for phoneme_node in self.main_node.leaves:  # this should be all phonemes
                widget = phoneme_node.name
                if widget.lipsync_object.is_phoneme:  # shouldn't be needed, just to be sure
                    widget.setGeometry(widget.x(),
                                       self.height() - (self.horizontalScrollBar().height()*1.5) - (text_height + (text_height * widget.phoneme_offset)),
                                       self.frame_width + 5,
                                       text_height)
        self.horizontalScrollBar().setValue(self.scroll_position)
        if self.temp_play_marker:
            self.temp_play_marker.setRect(self.temp_play_marker.rect().x(), 1, self.frame_width + 1, self.height())

    def on_zoom_in(self, event=None):
        if (self.doc is not None) and (self.samples_per_frame < 16):
            self.samples_per_frame *= 2
            self.samples_per_sec = self.doc.fps * self.samples_per_frame
            self.frame_width = self.sample_width * self.samples_per_frame
            self.set_document(self.doc)
            self.scene().setSceneRect(self.scene().sceneRect().x(), self.scene().sceneRect().y(),
                                      self.sceneRect().width() * 2, self.scene().sceneRect().height())
            self.setSceneRect(self.scene().sceneRect())
            self.scroll_position *= 2
            self.horizontalScrollBar().setValue(self.scroll_position)

    def on_zoom_out(self, event=None):
        if (self.doc is not None) and (self.samples_per_frame > 1):
            self.samples_per_frame /= 2
            self.samples_per_sec = self.doc.fps * self.samples_per_frame
            self.frame_width = self.sample_width * self.samples_per_frame
            self.set_document(self.doc)
            self.scene().setSceneRect(self.scene().sceneRect().x(), self.scene().sceneRect().y(),
                                      self.scene().sceneRect().width() / 2, self.scene().sceneRect().height())
            self.setSceneRect(self.scene().sceneRect())

            self.scroll_position /= 2
            self.horizontalScrollBar().setValue(self.scroll_position)

    def on_zoom_reset(self, event=None):
        if self.doc is not None:
            self.scroll_position /= (self.samples_per_frame / default_samples_per_frame)
            factor = (self.samples_per_frame / default_samples_per_frame)
            self.sample_width = default_sample_width
            self.samples_per_frame = default_samples_per_frame
            self.samples_per_sec = self.doc.fps * self.samples_per_frame
            self.frame_width = self.sample_width * self.samples_per_frame
            self.set_document(self.doc)
            self.scene().setSceneRect(self.scene().sceneRect().x(), self.scene().sceneRect().y(),
                                      self.scene().sceneRect().width() / factor, self.scene().sceneRect().height())
            self.setSceneRect(self.scene().sceneRect())
            self.horizontalScrollBar().setValue(self.scroll_position)

# end of class WaveformView
