#!/usr/bin/env python3
import gi
import os
import pickle

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject, Pango, GLib

from plugin import Plugin, MsgLevel

GObject.threads_init()

session = 'session.dat'

class Config():
    def __init__(self):
        self.plug = None
        self.btcount = 0
        self.wlcount = 0
        self.btaddr = 0x474b42540000
        self.wladdr = 0x474b574c0000


class Plug(GObject.GObject):
    def __init__(self, name):
        super().__init__()
        self.name = name

class GKProductToolKit() :
    def update_status(self, msg):
        self.btstatus.set_text('BT: {:012X}/{:d}'.format(self.config.btaddr,
            self.config.btcount))
        self.wlstatus.set_text('WIFI: {:012X}/{:d}'.format(self.config.wladdr,
            self.config.wlcount))
        self.status.set_text(msg)

    def update_session(self, wl, bt, msg):
        self.config.btcount += bt
        self.config.btaddr += bt
        self.config.wlcount += wl
        self.config.wladdr += wl
        pickle.dump(self.config, open(session, 'wb'), True)
        self.update_status(msg)

    def load_session(self):
        with open(session, 'rb') as f: self.config = pickle.load(f)

    def on_App_delete_event(self, *args):
        self.update_session(0, 0, '退出')
        Gtk.main_quit(*args)
    
    def on_clearout_clicked(self, button): self.clearout()

    def on_PluginList_changed(self, combo):
        self.clearout()
        plugin = combo.get_model().get_value(combo.get_active_iter(), 1)
        self.load_plugin(plugin.name)

    def clearout(self):
        buf = self.outtext.props.buffer
        buf.delete(buf.get_end_iter(), buf.get_start_iter())

    def load_plugin(self, name):
        try:
            plug = __import__(name.replace('/', '.'),
                    fromlist=['*']).Plugin(self)
            if self.plug: self.plug.destroy()
            plug.load()
            self.config.plug = name
            self.plug = plug
            self.update_session(0, 0, '插件加载完成')
        except Exception as e:
            self.err("插件加载失败: " + str(e))
            self.update_status('插件加载失败')

    def detect_plugin(self, piter, path):
        def make_plugin_list(x):
            sub = os.path.join(path, x)
            if x == '__pycache__' or not (os.path.isdir(sub)
                    or os.path.isfile(sub)): return

            dispath = os.path.splitext(sub)
            x = os.path.splitext(x)[0]
            newiter = self.store.append(piter, [x, Plug(dispath[0])])
            if os.path.isdir(sub):
                self.detect_plugin(newiter, sub)
            elif self.config.plug == dispath[0]:
                self.PluginList.set_active_iter(newiter)

        list(map(make_plugin_list, os.listdir(path)))

    def update_plugin(self):
        self.store = Gtk.TreeStore(str, Plug)
        self.PluginList.set_model(self.store)
        self.detect_plugin(None, 'plugins')

        cell = Gtk.CellRendererText()
        Gtk.TreeViewColumn(title='模块型号',
                cell_renderer = cell,
                text = 0, foreground = 4)

        self.PluginList.pack_start(cell, True)
        self.PluginList.add_attribute(cell, 'text', 0)

    def info(self, text): self.output(text)
    def err(self, text) : self.output(text, level=MsgLevel.ERROR)
    def warn(self, text): self.output(text, level=MsgLevel.WARNING)

    def output(self, text, level = MsgLevel.INFO):
        def display(text):
            buf = self.outtext.props.buffer
            buf.insert_with_tags(buf.get_end_iter(), text + '\n', self.tags[level])
            vadj = self.outwin.get_vadjustment()
            vadj.set_value(vadj.get_upper())
        GLib.idle_add(display, text)

    def btdone(self): self.update_session(0, 1, '蓝牙烧录成功')
    def wldone(self): self.update_session(1, 0, 'WIFI烧录成功')
    def done(self):   self.update_session(1, 1, '烧录很成功')
    def fail(self, msg):
        self.err(msg)
        self.update_session(0, 0, '烧录很失败')

    def __init__(self):
        self.plug = None
        self.tags = {}
        self.store = None
        self.config = Config()

        self.load_session()

        self.builder =Gtk.Builder()
        self.builder.add_from_file(os.path.join('ui', 'product.ui'))
        self.builder.connect_signals(self)

        for widget in [
                'App',
                'Toolbar',
                'PluginList',
                'MainWindow',
                'outbuf',
                'outwin',
                'outtext',
                'status',
                'wlstatus',
                'btstatus',
                ] :
            setattr(self, widget, self.builder.get_object(widget))


        self.tags[MsgLevel.INFO] = self.outbuf.create_tag('INFO')
        self.tags[MsgLevel.WARNING] = self.outbuf.create_tag('WARNING', foreground='blue')
        self.tags[MsgLevel.ERROR] = self.outbuf.create_tag('ERROR', foreground='red')
        self.update_plugin()
        self.update_status('初始化完成')
        self.App.show_all()

def main(): 
    product = GKProductToolKit()
    Gdk.threads_enter()
    Gtk.main()
    Gdk.threads_leave()

if __name__ == '__main__':
    main()

