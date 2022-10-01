# -*- coding: utf-8 -*-
# Copyright 2014-2016 The HyperSpyUI developers
#
# This file is part of HyperSpyUI.
#
# HyperSpyUI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HyperSpyUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HyperSpyUI.  If not, see <http://www.gnu.org/licenses/>.
"""
Created on Wed Jul 29 18:09:56 2015

@author: vidarton
"""


from qtpy import QtGui, QtCore, QtSvg, QtWidgets
from qtpy.QtGui import QPalette

import re


class SmartColorSVGIconEngine(QtGui.QIconEngine):
    """
    This class is basically a port to Python from the code for Qt's
    QSvgIconEnginePlugin. On top of this has been added the ability to exchange
    colors in the icons. It's also possible in the future to do more advanced
    XML pro-processing. Note: Some of the more esoteric uses of QIcon might
    not be fully tested for yet.
    """

    serial_gen = 0

    def __init__(self, use_qt_disabled=False, other=None):
        if other:
            super().__init__(other)
            if isinstance(other, SmartColorSVGIconEngine):
                self._svgFiles = other._svgFiles
                if other._svgBuffers:
                    self._svgBuffers = other._svgBuffers.copy()
                if other._addedPixmaps:
                    self._addedPixmaps = other._addedPixmaps.copy()
        else:
            super().__init__()
        self._addedPixmaps = {}
        self._svgFiles = {}
        self._svgBuffers = {}
        self.default_key = (QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.custom_color_replacements = {}
        self._automatic_color_replacements = {}
        self.use_qt_disabled = use_qt_disabled
        self._palette_key = None
        self._set_replacements_from_palette()

    def _set_replacements_from_palette(self):
        """Sets `_automatic_color_replacements` attribute from application
        palette. Updates `_palette_key` to the cacheKey of the used palette.
        """
        palette = QtWidgets.QApplication.palette()
        foreground = palette.color(QPalette.Active, QPalette.WindowText)
        background = palette.color(QPalette.Active, QPalette.Window)
        disabled_foreground = palette.color(QPalette.Disabled,
                                            QPalette.WindowText)
        disabled_background = palette.color(QPalette.Disabled,
                                            QPalette.Window)
        self._automatic_color_replacements = {
            'default': {
                b'#000000': foreground.name().encode('ascii'),
                b'black': foreground.name().encode('ascii'),
                b'#ffffff': background.name().encode('ascii'),
                b'white': background.name().encode('ascii'),
                },
            'disabled': {
                b'#000000': disabled_foreground.name().encode('ascii'),
                b'black': disabled_foreground.name().encode('ascii'),
                b'#ffffff': disabled_background.name().encode('ascii'),
                b'white': disabled_background.name().encode('ascii'),
                }
            }
        self._palette_key = palette.cacheKey()

    def _make_cache_key(self, size, mode, state):
        """Make a unique, reproducable key to store/lookup icons in the pixmap
        cache.
        """
        return str(self) + str((size, mode, state))

    def _replace_in_stream(self, filename, color_key='default'):
        """Opens supplied SVG file, parses the file replacing colors according
        to the dictionary `color_replacements`. Returns a QByteArray of the
        processed content.
        """
        f_low = filename.lower()
        if f_low.endswith('.svgz') or f_low.endswith('.svg.gz'):
            import gzip
            with gzip.open(filename, 'rb') as svg_file:
                svg_cnt = svg_file.read()
        else:
            with open(filename, 'rb') as svg_file:
                svg_cnt = svg_file.read()

        # Merge automatic and custom LUTs
        color_table = self._automatic_color_replacements.copy()
        color_table.update(self.custom_color_replacements)
        if color_key not in color_table:
            color_key = 'default'

        # Perform replacement according to correct table
        for old, new in color_table[color_key].items():
            re_exp = re.compile(re.escape(old), re.IGNORECASE)
            svg_cnt = re_exp.sub(new, svg_cnt)
        out = QtCore.QByteArray(svg_cnt)
        return out

    def _loadDataForModeAndState(self, renderer, mode, state):
        """Load SVG data to renderer.
        """
        # First, try to load from a buffer if available.
        if (mode, state) in self._svgBuffers:
            buf = self._svgBuffers[(mode, state)]
        elif self.default_key in self._svgBuffers:
            buf = self._svgBuffers[self.default_key]
        else:
            buf = QtCore.QByteArray()

        if buf:
            buf = QtCore.qUncompress(buf)
            renderer.load(buf)
        else:
            # If no buffer is available, load from file
            if (mode, state) in self._svgFiles:
                svgFile = self._svgFiles[(mode, state)]
                renderer.load(self._replace_in_stream(svgFile))
            elif self.default_key in self._svgFiles:
                svgFile = self._svgFiles[self.default_key]
                if mode == QtGui.QIcon.Disabled:
                    renderer.load(self._replace_in_stream(svgFile, 'disabled'))
                else:
                    renderer.load(self._replace_in_stream(svgFile))

    def paint(self, painter, rect, mode, state):
        painter.drawPixmap(rect, self.pixmap(rect.size(), mode, state))

    def actualSize(self, size, mode, state):
        if (mode, state) in self._addedPixmaps:
            pm = self._addedPixmaps[(mode, state)]
            if pm and pm.size() == size:
                return size

        pm = self.pixmap(size, mode, state)
        if pm is None:
            return QtCore.QSize()
        return pm.size()

    def pixmap(self, size, mode, state):
        # Check if the palette has changed (if so invalidate cache)
        if self._palette_key != QtWidgets.QApplication.palette().cacheKey():
            QtGui.QPixmapCache.clear()
            self._set_replacements_from_palette()
        pmckey = self._make_cache_key(size, mode, state)
        pm = QtGui.QPixmapCache.find(pmckey)
        if pm:
            return pm

        if (mode, state) in self._addedPixmaps:
            pm = self._addedPixmaps[(mode, state)]
            if pm is not None and pm.size() == size:
                return pm

        renderer = QtSvg.QSvgRenderer()
        self._loadDataForModeAndState(renderer, mode, state)
        if not renderer.isValid():
            return QtGui.QPixmap()

        actualSize = renderer.defaultSize()
        if actualSize is not None:
            actualSize.scale(size, QtCore.Qt.KeepAspectRatio)

        img = QtGui.QImage(actualSize, QtGui.QImage.Format_ARGB32_Premultiplied)
        img.fill(0x00000000)
        p = QtGui.QPainter(img)
        renderer.render(p)
        p.end()
        pm = QtGui.QPixmap.fromImage(img)
        opt = QtWidgets.QStyleOption()
        opt.palette = QtWidgets.QApplication.palette()
        if self.use_qt_disabled or mode != QtGui.QIcon.Disabled:
            generated = QtWidgets.QApplication.style().generatedIconPixmap(mode, pm, opt)
            if generated is not None:
                pm = generated

        if pm is not None:
            QtGui.QPixmapCache.insert(pmckey, pm)

        return pm

    def addPixmap(self, pixmap, mode, state):
        self._addedPixmaps[(mode, state)] = pixmap

    def addFile(self, fileName, size, mode, state):
        if fileName:
            abs = fileName
            if fileName[0] != ':':
                abs = QtCore.QFileInfo(fileName).absoluteFilePath()
            al = abs.lower()
            if (al.endswith(".svg") or al.endswith(".svgz") or
                    al.endswith(".svg.gz")):
                renderer = QtSvg.QSvgRenderer(abs)
                if renderer.isValid():
                    self._svgFiles[(mode, state)] = abs
            else:
                pm = QtGui.QPixmap(abs)
                if pm is not None:
                    self.addPixmap(pm, mode, state)

    def key(self):
        return "svg"

    def clone(self):
        return SmartColorSVGIconEngine(other=self)

    def read(self, ds_in):

        self._svgBuffers = {}    # QHash<int, QByteArray>

        if ds_in.version() >= QtCore.QDataStream.Qt_4_4:
            nfiles = ds_in.readInt()
            fileNames = {}
            for i in range(nfiles):
                fileNames[i] = ds_in.readString()
            isCompressed = ds_in.readBool()
            key = ds_in.readInt()
            self._svgBuffers[key] = QtCore.QByteArray()
            ds_in >> self._svgBuffers[key]
            if not isCompressed:
                for key, v in self._svgBuffers.items():
                    self._svgBuffers[key] = QtCore.qCompress(v)
            hasAddedPixmaps = ds_in.readInt()
            if hasAddedPixmaps:
                npixmaps = ds_in.readInt()
                self._addedPixmaps = {}
                for i in range(npixmaps):
                    pm = QtGui.QPixmap()
                    ds_in >> pm
                    self._addedPixmaps[i] = pm
        else:
            pixmap = QtGui.QPixmap()
            data = QtCore.QByteArray()

            ds_in >> data
            if not data.isEmpty():
                data = QtCore.qUncompress(data)
                if not data.isEmpty():
                    self._svgBuffers[self.default_key] = data
            num_entries = ds_in.readInt()
            for i in range(num_entries):
                if ds_in.atEnd():
                    return False
                ds_in >> pixmap
                mode = ds_in.readUInt32()
                state = ds_in.readUInt32()
                # The pm list written by 4.3 is buggy and/or useless, so ignore
                # self._addPixmap(pixmap, QIcon.Mode(mode), QIcon.State(state))

        return True

    def write(self, ds_out):
        if out.version() >= QtCore.QDataStream.Qt_4_4:
            isCompressed = 1
            if self._svgBuffers:
                svgBuffers = self._svgBuffers
            else:
                svgBuffers = {}     # QHash<int, QByteArray>
            for key, v in self._svgFiles.items():
                buf = QtCore.QByteArray()
                f = QtCore.QFile(v)
                if f.open(QtCore.QIODevice.ReadOnly):
                    buf = f.readAll()
                buf = QtCore.qCompress(buf)
                svgBuffers[key] = buf
            out << self._svgFiles << isCompressed << svgBuffers
            if self._addedPixmaps:
                out << 1 << self._addedPixmaps
            else:
                out << 0
        else:
            buf = QtCore.QByteArray()
            if self._svgBuffers:
                buf = self._svgBuffers[self.default_key]
            if buf.isEmpty():
                svgFile = self._svgFiles[self.default_key]
                if not svgFile.isEmpty():
                    f = QtCore.QFile(svgFile)
                    if f.open(QtCore.QIODevice.ReadOnly):
                        buf = f.readAll()
            buf = QtCore.qCompress(buf)
            out << buf
            # 4.3 has buggy handling of added pixmaps, so don't write any
            out << 0
        return True
