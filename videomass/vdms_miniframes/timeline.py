# -*- coding: UTF-8 -*-
"""
Name: floatingtimeline.py
Porpose: Select and clip a slice of time in the imported media
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: April.07.2023
Code checker: flake8, pylint

This file is part of Videomass.

   Videomass is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   Videomass is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with Videomass.  If not, see <http://www.gnu.org/licenses/>.
"""
import wx
import wx.adv
from pubsub import pub
from videomass.vdms_utils.utils import milliseconds2clock
from videomass.vdms_utils.utils import get_milliseconds


class Time_Selector(wx.Dialog):
    """
    fine-tune the time selection
    """
    def __init__(self, parent, clockstr, mode):
        """
        When this dialog is called, the values already set
        in the timeline panel are reproduced exactly here.
        """
        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        if mode == 'start':
            title = _('Start point adjustment')
        elif mode == 'duration':
            title = _('End point adjustment')
        boxs = wx.StaticBox(self, wx.ID_ANY, 'HH:MM:SS.ms')
        staticbox1 = wx.StaticBoxSizer(boxs, wx.VERTICAL)
        boxsiz1 = wx.BoxSizer(wx.HORIZONTAL)
        staticbox1.Add(boxsiz1, 0, wx.ALL | wx.ALIGN_CENTER, 0)
        sizer_base.Add(staticbox1, 0, wx.ALL | wx.EXPAND, 5)

        self.box_hour = wx.SpinCtrl(self, wx.ID_ANY,
                                    value=f"{clockstr[0:2]}",
                                    min=0, max=23,
                                    style=wx.SP_ARROW_KEYS)

        boxsiz1.Add(self.box_hour, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        lab1 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        boxsiz1.Add(lab1, 0, wx.ALIGN_CENTER, 5)

        self.box_min = wx.SpinCtrl(self, wx.ID_ANY,
                                   value=f"{clockstr[3:5]}",
                                   min=0, max=59,
                                   style=wx.SP_ARROW_KEYS)

        boxsiz1.Add(self.box_min, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        lab2 = wx.StaticText(self, wx.ID_ANY, (":"))
        lab2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        boxsiz1.Add(lab2, 0, wx.ALIGN_CENTER, 5)

        self.box_sec = wx.SpinCtrl(self, wx.ID_ANY,
                                   value=f"{clockstr[6:8]}",
                                   min=0, max=59,
                                   style=wx.SP_ARROW_KEYS)

        boxsiz1.Add(self.box_sec, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        lab3 = wx.StaticText(self, wx.ID_ANY, ("."))
        lab3.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        boxsiz1.Add(lab3, 0, wx.ALIGN_CENTER, 5)

        self.box_mills = wx.SpinCtrl(self, wx.ID_ANY,
                                     value=f"{clockstr[9:12]}",
                                     min=000, max=999,
                                     style=wx.SP_ARROW_KEYS)
        boxsiz1.Add(self.box_mills, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        # confirm buttons:
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        gridexit.Add(btn_close, 0, wx.ALL, 5)
        btn_ok = wx.Button(self, wx.ID_OK, "")
        gridexit.Add(btn_ok, 0, wx.ALL, 5)
        sizer_base.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)

        self.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()

        # ----------------------Properties ----------------------#

        self.SetTitle(title)
        self.box_hour.SetToolTip(_("Hours"))
        self.box_min.SetToolTip(_("Minutes"))
        self.box_sec.SetToolTip(_("Seconds"))
        self.box_mills.SetToolTip(_("Milliseconds"))

        # ----------------------Binding (EVT)----------------------#
        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, btn_ok)

    # ----------------------Event handler (callback)----------------------#

    def on_close(self, event):
        """
        Close this dialog without saving anything
        """
        event.Skip()  # need if destroy from parent
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Confirm OK event
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def getvalue(self):
        """
        This method return values via the GetValue() interface
        """
        val = (f'{str(self.box_hour.GetValue()).zfill(2)}:'
               f'{str(self.box_min.GetValue()).zfill(2)}:'
               f'{str(self.box_sec.GetValue()).zfill(2)}.'
               f'{str(self.box_mills.GetValue()).zfill(3)}'
               )
        return val, get_milliseconds(val)


class Float_TL(wx.MiniFrame):
    """
    A representation of the time selection meter as duration
    and position values viewed as time range selection ruler
    for the FFmpeg syntax, in the following form:

        `-ss 00:00:00.000 -t 00:00:00.000`

    The -ss flag means the start selection (SEEK); the -t flag
    means the time amount (DURATION) starting from -ss.
    See FFmpeg documentation for details:

        <https://ffmpeg.org/documentation.html>
        <https://trac.ffmpeg.org/wiki/Seeking#Timeunitsyntax>

    """
    YELLOW = '#bd9f00'  # for warnings
    BLACK = '#060505'  # black for background status bar
    ORANGE = '#f28924'  # for errors and warnings
    LGREEN = '#52EE7D'
    RULER_BKGRD = '#84D2C9'  # light blue for panelruler background
    SELECTION = '#31BAA7'  # CYAN
    DELIMITER_COLOR = '#00FE00'  # green for margin selection
    TEXT_PEN_COLOR = '#020D0F'  # black for text and draw lines
    DURATION_START = '#E95420'  # Light orange for duration/start indicators

    # ruler and panel specifications constants
    RW = 900  # ruler width
    RM = 0  # ruler margin
    PW = 902  # panel width
    PH = 60  # panel height

    def __init__(self, parent):
        """
        self.pix: scale pixels to milliseconds
        self.milliseconds: int(milliseconds)
        self.duration: see parent attr.
        self.bar_w: pixel point val for END selection
        self.bar_x: pixel point val for START selection
        """
        get = wx.GetApp()
        self.appdata = get.appset
        self.parent = parent
        self.duration = self.parent.duration
        self.overalltime = '23:59:59:999'
        self.milliseconds = 86399999  # 23:59:59:999
        self.clock_start = '00:00:00.000'  # seek position
        self.clock_end = '00:00:00.000'
        self.mills_end = 0
        self.mills_start = 0
        self.pix = Float_TL.RW / self.milliseconds  # set pixel constant
        self.bar_w = 0.0
        self.bar_x = 0.0
        self.dc = None
        self.movepixel = [0, 0]  # see `on_move()` `on_leftdown()`
        self.sourcedur = _('No source duration:')

        wx.MiniFrame.__init__(self, parent, style=wx.RESIZE_BORDER
                              | wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU
                              | wx.FRAME_FLOAT_ON_PARENT
                              )
        panel = wx.Panel(self, wx.ID_ANY, style=wx.TAB_TRAVERSAL
                         | wx.BORDER_THEME)
        self.font_med = wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        sizer_base = wx.BoxSizer(wx.VERTICAL)
        self.paneltime = wx.Panel(panel, wx.ID_ANY,
                                  size=(Float_TL.PW, Float_TL.PH),
                                  style=wx.BORDER_SUNKEN,
                                  )
        sizer_base.Add(self.paneltime, 0, wx.LEFT | wx.RIGHT | wx.CENTRE, 5)

        # ----------------------Properties ----------------------#
        self.paneltime.SetBackgroundColour(wx.Colour(Float_TL.RULER_BKGRD))
        panel.SetBackgroundColour(wx.Colour(Float_TL.BLACK))
        self.SetTitle("Timeline Editor")
        self.sb = self.CreateStatusBar(1)
        msg = _('{0} {1}  |  Segment Duration: {2}'
                ).format(self.sourcedur, self.overalltime, '00:00:00.000')
        self.statusbar_msg(msg, None)

        # ----------------------Layout----------------------#
        self.SetMinSize((925, 113))
        self.CentreOnScreen()
        panel.SetSizer(sizer_base)
        sizer_base.Fit(self)
        self.Layout()
        # print(self.GetSize())
        # ----------------------Binding (EVT)----------------------#
        self.paneltime.Bind(wx.EVT_PAINT, self.OnPaint)
        self.paneltime.Bind(wx.EVT_LEFT_DOWN, self.on_leftdown)
        self.paneltime.Bind(wx.EVT_LEFT_UP, self.on_leftup)
        self.paneltime.Bind(wx.EVT_LEFT_DCLICK, self.on_set_pos)
        self.paneltime.Bind(wx.EVT_MOTION, self.on_move)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_CONTEXT_MENU, self.onContext)

        pub.subscribe(self.set_values, "RESET_ON_CHANGED_LIST")

    # ----------------------Event handler (callback)----------------------#

    def onContext(self, event):
        """
        Create and show a Context Menu
        """
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID1"):
            popupID1 = wx.ID_ANY
            popupID2 = wx.ID_ANY
            popupID3 = wx.ID_ANY
            popupID4 = wx.ID_ANY
            self.Bind(wx.EVT_MENU, self.onPopup, id=popupID1)
            self.Bind(wx.EVT_MENU, self.onPopup, id=popupID2)
            self.Bind(wx.EVT_MENU, self.onPopup, id=popupID3)
            self.Bind(wx.EVT_MENU, self.onPopup, id=popupID4)
        # build the menu
        menu = wx.Menu()
        menu.Append(popupID1, _("End adjustment"))
        menu.Append(popupID2, _("Start adjustment"))
        menu.Append(popupID3, _("Reset"))
        menu.Append(popupID4, _("Help"))
        # show the popup menu
        self.PopupMenu(menu)
        menu.Destroy()
    # ----------------------------------------------------------------------

    def onPopup(self, event):
        """
        Evaluate the label string of the menu item selected and starts
        the related process
        """
        itemId = event.GetId()
        menu = event.GetEventObject()
        menuItem = menu.FindItemById(itemId)
        if menuItem.GetItemLabel() == _("End adjustment"):
            self.on_set_pos(None, mode='duration')
        elif menuItem.GetItemLabel() == _("Start adjustment"):
            self.on_set_pos(None, mode='start')
        elif menuItem.GetItemLabel() == _("Reset"):
            self.on_trim_time_reset()
        elif menuItem.GetItemLabel() == _("Help"):
            self.messagehelp()
    # ----------------------------------------------------------------------

    def on_trim_time_reset(self):
        """
        Reset all timeline values to default.
        """
        self.pix = Float_TL.RW / self.milliseconds
        self.bar_w = 0
        self.bar_x = 0
        self.mills_end = 0
        self.clock_end = '00:00:00.000'
        self.mills_start = 0
        self.clock_start = '00:00:00.000'
        msg = _('{0} {1}  |  Segment Duration: {2}'
                ).format(self.sourcedur, self.overalltime, '00:00:00.000')
        self.statusbar_msg(msg, None)
        self.parent.time_seq = ""
        self.onRedraw(self)
    # ------------------------------------------------------------------#

    def set_values(self, msg):
        """
        Any change to the file list in the drag panel reset
        timeline data. This method is called using pub/sub protocol
        subscribing "RESET_ON_CHANGED_LIST" by adding, selecting or
        removing imported files (see`filedrop.py`).
        """
        self.sourcedur = _('No source duration:')
        if msg == 'Changes':
            if not self.duration or not max(self.duration):
                self.milliseconds = 86399999
            elif max(self.duration) < 100:  # if .jpeg
                self.milliseconds = 86399999
            else:
                fdropsel = self.parent.filedropselected
                if fdropsel:
                    idx = self.parent.file_src.index(fdropsel)
                    self.milliseconds = self.duration[idx]
                    self.sourcedur = _('Source duration:')
                else:
                    self.milliseconds = 86399999

            self.overalltime = milliseconds2clock(self.milliseconds)
            self.on_trim_time_reset()
    # ------------------------------------------------------------------#

    def set_time_seq(self, isset=True):
        """
        Set parent time_seq attr.
        """
        if isset:
            dur = milliseconds2clock(self.mills_end - self.mills_start)
            self.parent.time_seq = f"-ss {self.clock_start} -t {dur}"
            msg = _('{0} {1}  |  Segment Duration: {2}'
                    ).format(self.sourcedur, self.overalltime, dur)
            self.statusbar_msg(f'{msg}', None)
        else:
            self.parent.time_seq = ""
            msg = _('{0} {1}  |  Segment Duration: {2}'
                    ).format(self.sourcedur, self.overalltime, '00:00:00.000')
            self.statusbar_msg(f'{msg}', None)
    # ------------------------------------------------------------------#

    def set_coordinates(self):
        """
        Set data for x axis rectangle selection and
        call onRedraw.
        """
        if self.movepixel[1] > 30:
            self.bar_w = self.movepixel[0]
            self.mills_end = int(round(self.bar_w / self.pix))
            self.clock_end = milliseconds2clock(self.mills_end)
            self.onRedraw(self)

        elif self.movepixel[1] < 30:
            self.bar_x = self.movepixel[0]
            self.mills_start = int(round(self.bar_x / self.pix))
            self.clock_start = milliseconds2clock(self.mills_start)
            self.onRedraw(self)
    # ------------------------------------------------------------------#

    def on_leftdown(self, event):
        """
        Event on clicking the left mouse button
        """
        self.paneltime.SetCursor(wx.Cursor(wx.CURSOR_HAND))
        self.movepixel = event.GetLogicalPosition(self.dc)
        if self.movepixel[0] >= Float_TL.RW:
            return
        if self.movepixel[0] <= 0:
            return
        self.set_coordinates()
    # ------------------------------------------------------------------#

    def on_leftup(self, event):
        """
        Event on releasing the left mouse button

        """
        self.paneltime.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

        if self.bar_w == 0 and self.bar_x == 0:
            self.set_time_seq(isset=False)
            return

        if self.bar_w <= self.bar_x:
            msg = _('WARNING: Invalid selection, out of range.')
            self.statusbar_msg(f'{msg}', Float_TL.ORANGE, Float_TL.BLACK)
            return

        self.set_time_seq(isset=True)
    # ------------------------------------------------------------------#

    def on_set_pos(self, event, mode=None):
        """
        Event on mouse double click right button
        """
        if mode == 'duration':
            clock, mode = self.clock_end, 'duration'
        elif mode == 'start':
            clock, mode = self.clock_start, 'start'
        elif self.movepixel[1] > 30:
            clock, mode = self.clock_end, 'duration'
        elif self.movepixel[1] < 30:
            clock, mode = self.clock_start, 'start'

        with Time_Selector(self, clock, mode) as selector:
            if selector.ShowModal() == wx.ID_OK:
                data = selector.getvalue()
                # pixpos, get new pixel value from ms var
                pixpos = self.pix / (Float_TL.RW / data[1]) * Float_TL.RW
                if mode == 'start':
                    self.bar_x = pixpos
                    self.mills_start = data[1]
                    self.clock_start = data[0]
                elif mode == 'duration':
                    self.bar_w = pixpos
                    self.mills_end = data[1]
                    self.clock_end = data[0]

                self.onRedraw(self)
                self.on_leftup(None)
    # ------------------------------------------------------------------#

    def on_move(self, event):
        """
        Mouse event when moving it on the panel bar
        """
        if event.Dragging():
            self.movepixel = event.GetLogicalPosition(self.dc)
            if self.movepixel[1] > 30:
                if self.mills_end == self.milliseconds:
                    return
            elif self.movepixel[1] < 30:
                if self.mills_start == 0:
                    return
            self.set_coordinates()
    # ------------------------------------------------------------------#

    def OnPaint(self, event):
        """
        wx.PaintDC event
        """
        self.dc = wx.PaintDC(self.paneltime)  # draw window boundary
        self.dc.Clear()
        self.onRedraw(self)
    # ------------------------------------------------------------------#

    def onRedraw(self, event):
        """
        Draw ruler and update the selection rectangle
        (a semi-transparent background rectangle upon a ruler)
        """
        msg = _('Start by dragging the bottom left handle,\n'
                'or right-click for options.')
        self.dc = wx.ClientDC(self.paneltime)
        self.dc.Clear()
        self.dc.SetPen(wx.Pen(Float_TL.DELIMITER_COLOR, 3, wx.PENSTYLE_SOLID))
        # self.dc.SetBrush(wx.Brush(wx.Colour(30, 30, 30, 200)))
        if self.bar_w == 0 and self.bar_x == 0:
            selcolor, textcolor = Float_TL.SELECTION, Float_TL.SELECTION
            self.dc.SetTextForeground(Float_TL.DURATION_START)
            w = self.dc.GetTextExtent(msg)[0]
            self.dc.DrawText(msg, 300, 10)
        elif self.bar_x >= self.bar_w:
            selcolor, textcolor = wx.RED, wx.YELLOW
        else:
            selcolor, textcolor = Float_TL.SELECTION, Float_TL.DURATION_START
        self.dc.SetBrush(wx.Brush(selcolor, wx.BRUSHSTYLE_SOLID))
        self.dc.DrawRectangle(self.bar_x, -8, self.bar_w - self.bar_x, 80)
        self.dc.SetPen(wx.Pen(Float_TL.TEXT_PEN_COLOR))
        self.dc.SetTextForeground(Float_TL.TEXT_PEN_COLOR)

        self.dc.SetFont(self.font_med)
        txt_s = _('Start')
        txt_d = _('End')

        self.dc.SetPen(wx.Pen(Float_TL.DELIMITER_COLOR, 2, wx.PENSTYLE_SOLID))
        self.dc.SetBrush(wx.Brush(Float_TL.DELIMITER_COLOR))

        # Make start txt
        txt1 = f'{txt_s}  {self.clock_start}'
        self.dc.SetTextForeground(textcolor)
        w = self.dc.GetTextExtent(txt1)[0]
        if w > self.bar_x:
            self.dc.DrawText(txt1, self.bar_x + 3, 14)
            self.dc.DrawRectangle(self.bar_x, 1, 7, 7)
        else:
            self.dc.DrawText(txt1, self.bar_x - w - 2, 14)
            self.dc.DrawRectangle(self.bar_x - 5, 1, 7, 7)

        # Make duration txt
        txt2 = f'{txt_d}  {self.clock_end}'
        w = self.dc.GetTextExtent(txt2)[0]
        if w < Float_TL.RW - self.bar_w:
            self.dc.DrawText(txt2, self.bar_w + 1, 31)
            self.dc.DrawRectangle(self.bar_w - 1, 51, 7, 7)
        else:
            self.dc.DrawText(txt2, self.bar_w - w - 5, 31)
            self.dc.DrawRectangle(self.bar_w - 6, 51, 7, 7)
    # ------------------------------------------------------------------#

    def statusbar_msg(self, msg, bcolor, fcolor=None):
        """
        Set the status-bar message and color.
        See main_frame docstrings for details.
        """
        if self.appdata['ostype'] == 'Linux':
            if not bcolor:
                self.sb.SetBackgroundColour(wx.NullColour)
                self.sb.SetForegroundColour(wx.NullColour)
            else:
                self.sb.SetBackgroundColour(bcolor)
                self.sb.SetForegroundColour(fcolor)

        self.sb.SetStatusText(msg)
        self.sb.Refresh()
    # ------------------------------------------------------------------#

    def messagehelp(self):
        """
        Show a message help dialog
        """
        msg = _("The timeline editor is a tool that allows you to trim slices "
                "of time on imported media. It is individually associated "
                "with each file selected in the Queued Files panel. Importing "
                "new files, making new selections, deleting items, and "
                "sorting items (ie by LEFT clicking on the column headers), "
                "will reset the settings to their default values. In other "
                "hands, deselecting all source files will also have the same "
                "effect, but the overall duration values will be set to "
                "23:59:59.000 (HH:MM:SS.ms).\n\n"
                "Both duration values given by the moving actions of the "
                "\"Start\"/\"End\" handles always refer to the zero point "
                "(00:00:00.000). Both the duration values of the selected "
                "file and of any segment can be viewed in the status bar, as "
                "well as any warning messages.")
        wx.MessageBox(msg, _('Contextual help to the Timeline Editor'),
                      wx.ICON_INFORMATION, self)
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        Hide this frame
        """
        self.parent.menuBar.Check(self.parent.viewtimeline.GetId(), False)
        self.Hide()
