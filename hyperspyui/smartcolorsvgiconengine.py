# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 18:09:56 2015

@author: vidarton
"""


from python_qt_binding import QtGui, QtCore, QtSvg
from QtCore import *
from QtGui import *
from QtSvg import *


class SmartColorSVGIconEngine(QIconEngineV2):
    """
    This class is basically a port to Python from the code for Qt's
    QSvgIconEnginePlugin. On top of this has been added the ability to exchange
    colors in the icons. It's also possible in the future to do more advanced
    XML pro-processing. Note: Some of the more esoteric uses of QIcon might
    not be fully tested for yet.
    """

    serial_gen = 0L

    def __init__(self, use_qt_disabled=False, other=None):
        if other:
            super(SmartColorSVGIconEngine, self).__init__(other)
            if isinstance(other, SmartColorSVGIconEngine):
                self._svgFiles = other._svgFiles
                if other._svgBuffers:
                    self._svgBuffers = other._svgBuffers.copy()
                if other._addedPixmaps:
                    self._addedPixmaps = other._addedPixmaps.copy()
        else:
            super(SmartColorSVGIconEngine, self).__init__()
        self._addedPixmaps = {}
        self._svgFiles = {}
        self._svgBuffers = {}
        self.default_key = (QIcon.Normal, QIcon.Off)
        self.custom_color_replacements = {}
        self._automatic_color_replacements = {}
        self.use_qt_disabled = use_qt_disabled
        self._palette_key = None
        self._set_replacements_from_palette()

    def _set_replacements_from_palette(self):
        """Sets `_automatic_color_replacements` attribute from application
        palette. Updates `_palette_key` to the cacheKey of the used palette.
        """
        palette = QApplication.palette()
        foreground = palette.color(QPalette.Active, QPalette.WindowText)
        disabled_foreground = palette.color(QPalette.Disabled,
                                            QPalette.WindowText)
        self._automatic_color_replacements = {
            'default': {
                '#000000': foreground.name(),
                'black': foreground.name()
                },
            'disabled': {
                '#000000': disabled_foreground.name(),
                'black': disabled_foreground.name()
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
        svg_file = open(filename, 'r')
        svg_cnt = svg_file.read()

        # Merge automatic and custom LUTs
        color_table = self._automatic_color_replacements.copy()
        color_table.update(self.custom_color_replacements)
        if color_key not in color_table:
            color_key = 'default'

        # Perform replacement according to correct table
        for old, new in color_table[color_key].iteritems():
            svg_cnt = svg_cnt.replace(old, new)
        out = QByteArray(svg_cnt)
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
            buf = QByteArray()

        if buf:
            buf = qUncompress(buf)
            renderer.load(buf)
        else:
            # If no buffer is available, load from file
            if (mode, state) in self._svgFiles:
                svgFile = self._svgFiles[(mode, state)]
                renderer.load(self._replace_in_stream(svgFile))
            else:
                svgFile = self._svgFiles[self.default_key]
                if mode == QIcon.Disabled:
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
            return QSize()
        return pm.size()

    def pixmap(self, size, mode, state):
        # Check if the palette has changed (if so invalidate cache)
        if self._palette_key != QApplication.palette().cacheKey():
            QPixmapCache.clear()
            self._set_replacements_from_palette()
        pmckey = self._make_cache_key(size, mode, state)
        pm = QPixmapCache.find(pmckey)
        if pm:
            return pm

        if (mode, state) in self._addedPixmaps:
            pm = self._addedPixmaps[(mode, state)]
            if pm is not None and pm.size() == size:
                return pm

        renderer = QSvgRenderer()
        self._loadDataForModeAndState(renderer, mode, state)
        if not renderer.isValid():
            return QPixmap()

        actualSize = renderer.defaultSize()
        if actualSize is not None:
            actualSize.scale(size, Qt.KeepAspectRatio)

        img = QImage(actualSize, QImage.Format_ARGB32_Premultiplied)
        img.fill(0x00000000)
        p = QPainter(img)
        renderer.render(p)
        p.end()
        pm = QPixmap.fromImage(img)
        opt = QStyleOption()
        opt.palette = QApplication.palette()
        if self.use_qt_disabled or mode != QIcon.Disabled:
            generated = QApplication.style().generatedIconPixmap(mode, pm, opt)
            if generated is not None:
                pm = generated

        if pm is not None:
            QPixmapCache.insert(pmckey, pm)

        return pm

    def addPixmap(self, pixmap, mode, state):
        self._addedPixmaps[(mode, state)] = pixmap

    def addFile(self, fileName, size, mode, state):
        if fileName:
            abs = fileName
            if fileName[0] != ':':
                abs = QFileInfo(fileName).absoluteFilePath()
            al = abs.lower()
            if (al.endswith(".svg") or al.endswith(".svgz") or
                    al.endswith(".svg.gz")):
                renderer = QSvgRenderer(abs)
                if renderer.isValid():
                    self._svgFiles[(mode, state)] = abs
            else:
                pm = QPixmap(abs)
                if pm is not None:
                    self.addPixmap(pm, mode, state)

    def key(self):
        return "svg"

    def clone(self):
        return SmartColorSVGIconEngine(other=self)

    def read(self, ds_in):

        self._svgBuffers = {}    # QHash<int, QByteArray>

        if ds_in.version() >= QDataStream.Qt_4_4:
            nfiles = ds_in.readInt()
            fileNames = {}
            for i in xrange(nfiles):
                fileNames[i] = ds_in.readString()
            isCompressed = ds_in.readBool()
            key = ds_in.readInt()
            self._svgBuffers[key] = QByteArray()
            ds_in >> self._svgBuffers[key]
            if not isCompressed:
                for key, v in self._svgBuffers.iteritems():
                    self._svgBuffers[key] = qCompress(v)
            hasAddedPixmaps = ds_in.readInt()
            if hasAddedPixmaps:
                npixmaps = ds_in.readInt()
                self._addedPixmaps = {}
                for i in xrange(npixmaps):
                    pm = QPixmap()
                    ds_in >> pm
                    self._addedPixmaps[i] = pm
        else:
            pixmap = QPixmap()
            data = QByteArray()

            ds_in >> data
            if not data.isEmpty():
                data = qUncompress(data)
                if not data.isEmpty():
                    self._svgBuffers[self.default_key] = data
            num_entries = ds_in.readInt()
            for i in xrange(num_entries):
                if ds_in.atEnd():
                    return False
                ds_in >> pixmap
                mode = ds_in.readUInt32()
                state = ds_in.readUInt32()
                # The pm list written by 4.3 is buggy and/or useless, so ignore
                # self._addPixmap(pixmap, QIcon.Mode(mode), QIcon.State(state))

        return True

    def write(self, ds_out):
        if out.version() >= QDataStream.Qt_4_4:
            isCompressed = 1
            if self._svgBuffers:
                svgBuffers = self._svgBuffers
            else:
                svgBuffers = {}     # QHash<int, QByteArray>
            for key, v in self._svgFiles.iteritems():
                buf = QByteArray()
                f = QFile(v)
                if f.open(QIODevice.ReadOnly):
                    buf = f.readAll()
                buf = qCompress(buf)
                svgBuffers[key] = buf
            out << self._svgFiles << isCompressed << svgBuffers
            if self._addedPixmaps:
                out << 1 << self._addedPixmaps
            else:
                out << 0
        else:
            buf = QByteArray()
            if self._svgBuffers:
                buf = self._svgBuffers[self.default_key]
            if buf.isEmpty():
                svgFile = self._svgFiles[self.default_key]
                if not svgFile.isEmpty():
                    f = QFile(svgFile)
                    if f.open(QIODevice.ReadOnly):
                        buf = f.readAll()
            buf = qCompress(buf)
            out << buf
            # 4.3 has buggy handling of added pixmaps, so don't write any
            out << 0
        return True
