# -*- coding: UTF-8 -*-
"""
Name: urldrop.py
Porpose: Allows you to add text URLs
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: March.17.2023
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
from urllib.parse import urlparse
import wx


class UrlDropTarget(wx.TextDropTarget):
    """
    This is a Drop target object for handle dragging text URL data
    on a ListCtrl object.
    """
    RED = '#ea312d'
    YELLOW = '#bd9f00'
    WHITE = '#fbf4f4'  # white for background status bar
    BLACK = '#060505'

    def __init__(self, parent, listctrl):
        """
        Defining the ListCtrl object attribute
        """
        wx.TextDropTarget.__init__(self)
        self.parent = parent
        self.listctrl = listctrl
        self.index = None

    def OnDropText(self, x, y, data):
        """
        Populate ListCtrl object by dragging text inside it.
        """
        self.index = self.listctrl.GetItemCount()
        listurl = data.split()
        for url in listurl:
            res = urlparse(url)
            if not res[1]:  # if empty netloc given from ParseResult
                self.parent.statusbar_msg('Invalid URL: "{}"'.format(url),
                                          UrlDropTarget.RED,
                                          UrlDropTarget.WHITE
                                          )
                return False

            for idx in range(self.index):
                if self.listctrl.GetItemText(idx, 1) == url:
                    self.parent.statusbar_msg('Some equal URLs found',
                                              UrlDropTarget.YELLOW,
                                              UrlDropTarget.BLACK
                                              )
                    return False
            self.listctrl.InsertItem(self.index, str(self.index + 1))
            self.listctrl.SetItem(self.index, 1, url)
            self.index += 1

        self.parent.changes_in_progress()
        return True


class Url_DnD_Panel(wx.Panel):
    """
    Panel responsible to embed URLs controls
    """
    ORANGE = '#f28924'
    WHITE = '#fbf4f4'

    def __init__(self, parent):
        """
        parent is the MainFrame
        """
        self.parent = parent
        get = wx.GetApp()
        # colors = get.appset['icontheme'][1]

        wx.Panel.__init__(self, parent, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add((0, 10))
        self.btn_remove = wx.Button(self, wx.ID_REMOVE, "")
        self.btn_remove.Disable()
        sizer.Add(self.btn_remove, 0, wx.ALL | wx.CENTRE, 2)
        infomsg = _("Drag URLS here")
        lbl_info = wx.StaticText(self, wx.ID_ANY, label=infomsg)
        sizer.Add(lbl_info, 0, wx.ALL | wx.EXPAND, 5)
        self.urlctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.urlctrl.InsertColumn(0, ('#'), width=30)
        self.urlctrl.InsertColumn(1, (_('Url')), width=400)
        dragt = UrlDropTarget(self, self.urlctrl)
        sizer.Add(self.urlctrl, 1, wx.EXPAND | wx.ALL, 5)
        self.urlctrl.SetDropTarget(dragt)
        sizer_ctrl = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer_ctrl, 0, wx.ALL | wx.EXPAND, 0)
        self.text_path_save = wx.TextCtrl(self, wx.ID_ANY, "",
                                          style=wx.TE_PROCESS_ENTER
                                          | wx.TE_READONLY,
                                          )
        sizer_ctrl.Add(self.text_path_save, 1, wx.LEFT | wx.EXPAND, 5)

        self.btn_save = wx.Button(self, wx.ID_OPEN, "...", size=(35, -1))
        sizer_ctrl.Add(self.btn_save, 0, wx.RIGHT | wx.LEFT
                       | wx.ALIGN_CENTER_HORIZONTAL
                       | wx.ALIGN_CENTER_VERTICAL, 5,
                       )
        self.SetSizer(sizer)

        if get.appset['ostype'] == 'Darwin':
            lbl_info.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        else:
            lbl_info.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))

        self.text_path_save.SetValue(self.parent.filedldir)
        # Tooltip
        tip = _("Set up a temporary folder for downloads")
        self.btn_save.SetToolTip(tip)
        self.text_path_save.SetToolTip(_("Destination folder"))

        self.Bind(wx.EVT_BUTTON, self.on_del_url_selected, self.btn_remove)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.urlctrl)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect, self.urlctrl)
    # ---------------------------------------------------------

    def changes_in_progress(self, setfocus=True):
        """
        Update new URLs list by drag&drop operations.
        """
        if setfocus:
            sel = self.urlctrl.GetFocusedItem()  # Get the current row
            selitem = sel if sel != -1 else 0
            self.urlctrl.Focus(selitem)  # make the line the current line
            self.urlctrl.Select(selitem, on=1)  # default event selection

        data = []
        for x in range(self.urlctrl.GetItemCount()):
            data.append(self.urlctrl.GetItemText(x, 1))

        if not data == self.parent.data_url:
            self.parent.changed = True

        self.statusbar_msg(_('Ready'), None)
        self.parent.data_url = data.copy()
        self.parent.destroy_orphaned_window()
    # -----------------------------------------------------------------------

    def statusbar_msg(self, mess, bcolor, fcolor=None):
        """
        Set a status bar message of the parent method.
        bcolor: background, fcolor: foreground
        """
        self.parent.statusbar_msg(f'{mess}', bcolor, fcolor)
    # -----------------------------------------------------------------------

    def on_select(self, event):
        """
        Selecting line with mouse or up/down keyboard buttons
        """
        self.btn_remove.Enable()

    # ----------------------------------------------------------------------

    def on_deselect(self, event):
        """
        Event to deselect a line when clicking
        in an empty space of the control list
        """
        self.btn_remove.Disable()
    # ----------------------------------------------------------------------

    def delete_all(self, event):
        """
        clear all text lines of the TxtCtrl
        """
        self.urlctrl.DeleteAllItems()
        self.parent.destroy_orphaned_window()
        del self.parent.data_url[:]
    # -----------------------------------------------------------

    def on_del_url_selected(self, event):
        """
        Delete a selected url
        """
        item, indexes = -1, []
        while 1:
            item = self.urlctrl.GetNextItem(item,
                                            wx.LIST_NEXT_ALL,
                                            wx.LIST_STATE_SELECTED)
            indexes.append(item)
            if item == -1:
                indexes.remove(-1)
                break

        if self.urlctrl.GetItemCount() == len(indexes):
            self.delete_all(self)
            return

        for num in sorted(indexes, reverse=True):
            self.urlctrl.DeleteItem(num)  # remove selected items
            self.urlctrl.Select(num - 1)  # select the previous one
        self.changes_in_progress(setfocus=False)

        for x in range(self.urlctrl.GetItemCount()):
            self.urlctrl.SetItem(x, 0, str(x + 1))  # re-load counter
        return
    # ----------------------------------------------------------------------

    def on_file_save(self, path):
        """
        Set a specific directory for files saving
        """
        self.text_path_save.SetValue("")
        self.text_path_save.AppendText(path)
        self.parent.filedldir = path
