#!/usr/bin/env python
#
#	Author of this software - phanindra srungavarapu <pahninsd@gmail.com> - phanindras.com
#
#	Cyberoam login client GUI for linux
#	This is a free software distributed under GPL without any warrenty and support
#	you can redistribute it and/or modify it
#	under the terms of the GNU  General Public License as published
#	by the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This software is distributed in the hope that it will be useful, but
#	WITHOUT ANY WARRANTY; without esavingven the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#	See the GNU General Public License for more details.
#
#	You should have received a copy of the GNU Lesser General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/#GPL>. 
#

import urllib, urllib2, os, sys, gobject
from xml.dom.minidom import parseString
import pygtk
pygtk.require('2.0')
import gtk
import re

class Cyberoam():
	def __init__(self):
		self.url 	= 	'http://192.168.1.250:8090/corporate/servlet/CyberoamHTTPClient'
		self.params	=	{
						'mode' : '192'
					}
		self.status="new"
		print "Cyberoam client for linux started.."
		self.build_gui()
	
	def build_gui(self):
		print "Starting GUI for cyberoam-linux client.."
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect("delete_event", self.gotoTray)
		self.window.connect("destroy", self.destroy)
		#self.window.set_border_width(24)
		self.window.set_size_request(400, 200)
		self.window.set_title("Cyberoam client")
		self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
		self.window.set_resizable(False)
		
		topwid=gtk.VBox(gtk.FALSE, 0)
		
				
		mb = gtk.MenuBar()

		appmenu = gtk.Menu()
		app = gtk.MenuItem("App")
		app.set_submenu(appmenu)

		exit = gtk.MenuItem("Exit")
		exit.connect("activate", self.destroy)
		appmenu.append(exit)

		mb.append(app)
		vbox = gtk.VBox(False, 2)
		vbox.pack_start(mb, False, False, 0)
		topwid.pack_start(vbox)
		
		
		
		
		table = gtk.Table(3, 3, True)
		topwid.pack_start(table)
		
		label = gtk.Label("Username")
		table.attach(label,0,1,0,1)
		label.show()
		
		self.username=gtk.Entry(max=10)
		table.attach(self.username,1,3,0,1)
		self.username.show()
		
		label1 = gtk.Label("Password")
		table.attach(label1,0,1,1,2)
		label1.show()
		
		self.password=gtk.Entry(max=10)
		table.attach(self.password,1,3,1,2)
		self.password.set_visibility(False)
		self.password.show()
		
		self.button=gtk.Button("Login")
		self.button.connect("clicked",self.click_button)
		table.attach(self.button,1,3,2,3)
		self.button.show()
		
		#
		
		table.show()

		
		self.window.add(topwid)

		topwid.show()
		
		self.statusicon = gtk.status_icon_new_from_stock(gtk.STOCK_NETWORK)
		self.statusicon.connect('activate', self.status_clicked )
		self.statusicon.set_name("Cyberoam")
		
		self.window.show_all()
		self.winstatus='showing'
		
		gtk.main()
	
	
	def gotoTray(self, widget, event, data=None):
		self.window.hide_on_delete()
		self.winstatus='hiding'
		print "minimizing app to tray"
		return True
	
	def destroy(self, widget, data=None):
		if self.status=='login':
			self.doLogout()
		
		gtk.main_quit()
		sys.exit(0)
		
	def status_clicked(self,status):
		if self.winstatus == 'showing':
			self.window.hide()
			print "Hiding app"
			self.winstatus='hiding'
		else:
			print "Showing app"
			self.window.show_all()
			self.winstatus='showing'
		
	
	def conServer(self):
		print "connecting to server"
		encodedata = urllib.urlencode(self.params)
		req = urllib2.Request(self.url, encodedata)
		self.response = urllib2.urlopen(req)
		self.responsedata = self.response.read()
		print self.responsedata
	
	def chkLogin(self):
		try:
			self.conServer()
			hasip = re.search('((25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)\.){3}(25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)',self.responsedata)
			if self.responsedata == "<?xml version='1.0' ?><liverequestresponse><loginstatus>false</loginstatus><livemessage>Critical error has occured</livemessage></liverequestresponse>":
				self.doLogin()
			
			elif self.responsedata == "<?xml version='1.0' ?><liverequestresponse><liverequesttime>180</liverequesttime><livemessage></livemessage></liverequestresponse>":
				print "you are already logged in"
				self.doLogin()
			
			elif hasip:
				print "some one already logged in on this computer"
				self.doLogin()
			
			elif self.responsedata == "<?xml version='1.0' ?><liverequestresponse><loginstatus>false</loginstatus><livemessage>You have been logged on from somewhere else, please relogon</livemessage></liverequestresponse>":
				print "you are loggedd in some where else"
				self.doLogout()
				self.doLogin()
			
		except Exception, detail:
			print "Error Occured ", detail 
		
	def keepalive(self):
		if self.status=="login":
			print "updating status"
			self.conServer()
			return True
		else:
			return False
		
	
	def doLogin(self):
		self.params['mode']=191
		self.conServer()
		self.status="login"
		self.button.set_label('Logout')
		self.gotoTray(self,self.window,"minimize_event")
		self.params['mode']=192
		
	def doLogout(self):
		self.params['mode']=193
		self.conServer()
		print self.responsedata
		self.status="logout"
		self.button.set_label('Login')
		self.params['mode']=192
		
	
	def click_button(self, widget, data=None):
		if self.username.get_text_length() != 0 and self.password.get_text_length() != 0:
			self.params['username']=self.username.get_text()
			self.params['password']=self.password.get_text()
			
			if self.status=="login":
				self.doLogout()
				
			elif self.status=="logout":
				self.doLogin()
				gobject.timeout_add(150000,self.keepalive)
				
			elif self.status=="new":
				self.chkLogin()
				self.button.set_label('Logout')
				gobject.timeout_add(150000,self.keepalive)
						
		#	if self.chkLogin():
		#		print self.responsedata
		#	else:
		#		msgpop=gtk.MessageDialog(parent=None, flags=gtk.DIALOG_DESTROY_WITH_PARENT, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format="Some error occured")
		#		msgpop.run()
		#		msgpop.destroy()
			
		else:
			msgpop=gtk.MessageDialog(parent=None, flags=gtk.DIALOG_DESTROY_WITH_PARENT, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format="Need password and username fields")
			msgpop.run()
			msgpop.destroy()
	

cyb=Cyberoam()
