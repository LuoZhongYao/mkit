import gi
import os
import plugin
import random
import hashlib
import shell

gi.require_version('Gtk','3.0')
from gi.repository import Gtk,Gdk,GObject,Pango,GLib

class Plugin(plugin.Plugin, shell.Shell):
    model_name = 'bcm43455'
    otphdr = bytearray([
        0x4b, 0x00, 0xff, 0xff, 0x00,
        0x00, 0x20, 0x04, 0xd0, 0x02,
        0x39, 0x43
        ])
    def on_download_clicked(self, button):
        self.host.clearout()
        self.host.info('HW: ' + ''.join('{:02X}'.format(x) for x in self.otphdr))
        otpbinmap = bytearray()
        otpbinmap[:] = self.otphdr
        #key = self.encrypt(os.urandom(6))
        key = self.encrypt('这个salt非常安全,因为没有人去破解他'.encode())
        self.host.info('KEY: ' + ''.join('{:02X}'.format(x) for x in key))
        self.push_tag(otpbinmap, 0x19, 
                self.host.config.wladdr.to_bytes(6, byteorder='big'))
        self.push_tag(otpbinmap, 0x15, key)
        self.save_otpbinmap(self.model_name + '.bin', otpbinmap)
        try:
            self.exec(['xecho', 'ciswrite', self.model_name + '.bin'])
            self.host.done()
        except Exception as e:
            self.host.fail('烧录失败: %s' %(e))

    def encrypt(self, salt):
        m = hashlib.md5()
        m.update(self.host.config.wladdr.to_bytes(6, byteorder='little'))
        m.update(salt)
        return m.digest()

    def push_tag(self, binmap, tag, dat):
        binmap.extend([0x80, tag, len(dat)])
        binmap.extend(dat)

    def save_otpbinmap(self, fname, otpbinmap):
        otpbinmap.extend([0xff, 0xff])
        with open(fname, 'wb') as f:
            f.write(otpbinmap)

    def __init__(self, host):
        self.host = host
        self.download = Gtk.ToolButton(Gtk.STOCK_MEDIA_PLAY)
        self.download.connect('clicked', self.on_download_clicked)
        self.host.Toolbar.insert(self.download, 1)
        self.host.Toolbar.show_all()

    def load(self):
        self.host.info("BCM43455 load")

    def destroy(self):
        self.host.info("BCM43455 unload")
        self.download.destroy()
