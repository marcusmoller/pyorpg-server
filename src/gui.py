import pygtk
pygtk.require('2.0')
import gtk

class ServerGUI(gtk.Window):
	def __init__(self):
		# initialize the server gui
		super(ServerGUI, self).__init__()

		self.set_title('PyORPG Server GUI')
		self.set_size_request(800, 600)
		self.set_position(gtk.WIN_POS_CENTER)

		# set icon
		'''
		try:
			self.set_icon_from_file('icon.png')

		except Exception, e:
			print e.message
		'''

		# list
		vbox = gtk.VBox(False, 8)

		sw = gtk.ScrolledWindow()

		vbox.pack_start(sw, True, True, 0)

		store = self.createModel()

		self.show_all()

	def createModel(self):
		store = gtk.ListStore(str, str)

		store.append(['test', 'mon det virker'])

		return store