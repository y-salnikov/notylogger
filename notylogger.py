#!/usr/bin/python3


window_place=[1420,60]
window_size=[500,1000]

window_css="\
window, list, list-row, menu\
{ \
    background-color: rgba(0,0,0,0.8); \
    color: #fff;\
}\
button\
{\
    color: #000;\
}\
textview text\
{\
    background-color: #003;\
    color: #fff;\
}\
"



from gi.repository import GLib
import gi
gi.require_version("Gtk", "3.0")
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GObject, GLib, GdkPixbuf, Gdk
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import AppIndicator3
import datetime

digits=[
".###. ..#.. .###. .###. ...#. ##### .#### ##### .###. .###. ",
"#...# .##.. #...# #...# ..##. #.... #.... ....# #...# #...# ",
"#..## ..#.. ....# ....# .#.#. #.... #.... ...#. #...# #...# ",
"#.#.# ..#.. ...#. ..##. ##### ####. ####. ..#.. .###. .#### ",
"##..# ..#.. ..#.. ....# ...#. ....# #...# ..#.. #...# ....# ",
"#...# ..#.. .#... #...# ...#. #...# #...# ..#.. #...# #...# ",
".###. .###. ##### .###. ...#. .###. .###. ..#.. .###. .###. "
]

empty_xpm=[
"22 22 3 1",
". c None",
"# c #000000",
"a c #808080",
"......................",
"......................",
"......................",
"......................",
"...#################..",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"...##########aaaa###..",
".............##aaa#...",
"...............##aa#..",
".................####.",
"......................"
]

template_xpm=[
"22 22 3 1",
". c None",
"# c #000000",
"a c #ffffff",
"......................",
"......................",
"......................",
"......................",
"...#################..",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"..#aaaaaaaaaaaaaaaaa#.",
"...##########aaaa###..",
".............##aaa#...",
"...............##aa#..",
".................####.",
"......................"
]

notifications_list=[]

def notifications(bus, message):
	global ind
	global notifications_list
	global window
	args=[arg for arg in message.get_args_list()]
	if len(args)>=8:
		app_name=args[0]
		icon=args[2]
		title=args[3]
		text=args[4]
		notifications_list.append([icon,app_name,title,text,datetime.datetime.now()])
		ind.set_icon(stamp_number(len(notifications_list)))
		if window.opened:
			list_add(notifications_list[-1])
			window.list.show_all()

DBusGMainLoop(set_as_default=True)

bus = dbus.SessionBus()
bus.add_match_string_non_blocking("eavesdrop=true, interface='org.freedesktop.Notifications', member='Notify'")
bus.add_message_filter(notifications)

def stamp_number(n):
	if n>99: n=99
	n_dig=1 if n<10 else 2
	x0=12-((6*n_dig)//2)
	y0=11
	if n_dig==2:
		chars=[n//10,n%10]
	else:
		chars=[n%10]
	out_xpm=template_xpm[:]
	for i in range(len(chars)):
		xd=chars[i]*6
		for y in range(len(digits)):
			for x in range(5):
				if digits[y][xd+x]=='#':
					out_xpm[y0+y]=out_xpm[y0+y][:x0+x+i*6]+'#'+out_xpm[y0+y][x0+1+x+i*6:]
	pixbuf=GdkPixbuf.Pixbuf.new_from_xpm_data(out_xpm)
	return pixbuf

def menu_show_pressed(widget):
	global ind
	global window
	update_list()
	window.show()
	
def menu_clear_pressed(widget):
	global ind
	global notifications_list
	global empty_pixbuf
	global window
	notifications_list=[]
	ind.set_icon(empty_pixbuf)
	if window.opened:
		update_list()
		window.list.show_all()
		window.show()

def list_add(notify):
	global window
	hbox=Gtk.Box(orientation=0,spacing=5)
	window.list.add(hbox)
	image=Gtk.Image.new_from_icon_name(notify[0],3)
	hbox.pack_start(image,False,False,0)
	label=Gtk.Label()
	label.set_markup("<b>%s:</b>" %(notify[1]))
	hbox.pack_start(label,False,False,0)
	vbox=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
	hbox.pack_start(vbox,True,True,0)
	label2=Gtk.Label()
	label2.set_markup("<b>%s</b>" %(notify[2]))
	label2.set_xalign(0)
	vbox.pack_start(label2,False,False,0)
	textview = Gtk.TextView()
	textview.set_editable(False)
	textview.set_wrap_mode(2)
	vbox.pack_start(textview,True,True,0)
	textbuffer = textview.get_buffer()
	textbuffer.set_text(notify[3]+"\n")
	label_time=Gtk.Label(label="%d:%d" %(notify[4].hour,notify[4].minute))
	hbox.pack_start(label_time,False,False,0)
	
def update_list():
	global window
	window.list.foreach(lambda w,d:window.list.remove(w),None)
	for i in notifications_list:
		list_add(i)
		
class ListWindow:
	def __init__(self):
		self.opened=False
		self.win=Gtk.Window()
		self.win.set_decorated(False)
		self.win.set_skip_taskbar_hint(True)
		self.win.move(window_place[0],window_place[1])
		self.win.set_default_size(window_size[0],window_size[1])
		self.win.set_keep_above(True)
		css=bytes(window_css, "utf8")
		css_provider=Gtk.CssProvider()
		css_provider.load_from_data(css)
		context = Gtk.StyleContext()
		screen = Gdk.Screen.get_default()
		context.add_provider_for_screen(screen, css_provider,
                                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
		vbox=Gtk.Box(orientation=1,spacing=0)
		self.win.add(vbox)
		sc_win=Gtk.ScrolledWindow()
		sc_win.set_min_content_width(window_size[0])
		sc_win.set_min_content_height(window_size[1]-40)
		vbox.pack_start(sc_win,True,True,0)
		self.list=Gtk.ListBox()
		self.list.set_selection_mode(Gtk.SelectionMode.NONE)
		sc_win.add(self.list)
		hbox=Gtk.Box(orientation=0,spacing=0)
		vbox.pack_start(hbox,False,False,0)
		button_clear=Gtk.Button.new_with_label("Очистить")
		button_clear.connect("clicked",menu_clear_pressed)
		hbox.pack_start(button_clear,False,False,20)
		button_close=Gtk.Button.new_with_label("Закрыть")
		button_close.connect("clicked",menu_show_pressed)
		hbox.pack_start(button_close,False,False,20)
		
	def show(self):
		if self.opened:
			self.win.hide()
			self.opened=False
		else:
			self.win.move(window_place[0],window_place[1])
			self.win.show_all()
			self.opened=True

class StatusIcon:
	def __init__(self,pixbuf):
		self.statusicon=Gtk.StatusIcon()
		self.statusicon.set_from_pixbuf(pixbuf)
		self.statusicon.connect("popup-menu", self.right_click_event)
		self.statusicon.connect("activate", menu_show_pressed)
	def right_click_event(self, icon, button, time):
		self.menu = Gtk.Menu()

		show = Gtk.MenuItem()
		show.set_label("Показать")
		quit = Gtk.MenuItem()
		quit.set_label("Выход")
		clear = Gtk.MenuItem()
		clear.set_label("Очистить")
		show.connect("activate", menu_show_pressed)
		quit.connect("activate", Gtk.main_quit)
		clear.connect("activate", menu_clear_pressed)
		self.menu.append(show)
		self.menu.append(clear)
		self.menu.append(quit)
		
		self.menu.show_all()
		
		self.menu.popup(None, None, None, self.statusicon, button, time)
	def set_icon(self,pixbuf):
		self.statusicon.set_from_pixbuf(pixbuf)




def main():
	global ind
	global empty_pixbuf
	global window
	ind = Gtk.StatusIcon()
	empty_pixbuf=GdkPixbuf.Pixbuf.new_from_xpm_data(empty_xpm)
	ind=StatusIcon(empty_pixbuf)
	window=ListWindow()
	Gtk.main()



if __name__ == '__main__':
    main()


