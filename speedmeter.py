#!/usr/bin/env python3
import atexit
import json
import os
import signal
import time
import webbrowser
from threading import Thread
import gi
import netifaces
import speedtest
import xlsxwriter
import time

class AesirExcelWriter:
    def __init__(self, file_name, reserve_row):
        self.current_row_index = 0
        self.current_column_index = 0
        self.file_name = file_name
        if reserve_row is not None:
            self.reserverow(reserve_row)
        self.workbook = xlsxwriter.Workbook(self.file_name)
        self.worksheet = self.workbook.add_worksheet()
        self.worksheet.fit_width

    def createTitle(self, list):
        row = 0
        col = 0
        for item in list:
            self.worksheet.write(row,
                                 col, item)
            col += 1

    def reserverow(self, how_many):
        self.current_row_index += how_many

    def writefromdict(self, dict):
        pass

    def closeFile(self):
        self.workbook.close()

    def writefromlist(self, list):

        for item in list:
            self.worksheet.write(self.current_row_index,
                                 self.current_column_index, item)
            self.current_column_index += 1

        self.current_row_index += 1
        self.current_column_index = 0

class HandlerOptionsWindow:

    def switch_updates_event_activate(self, widget):
        pass

    def switch_boot_event_activate(self, widget):
        pass

    def switch_save_event_activate(self, widget):
        pass

    def switch_updates_event_set(self, widget):
        pass

    def switch_boot_event_set(self, widget):
        pass

    def switch_save_event_set(self, widget):
        pass

class Handler:

    def openURL(self, instance, url):
        webbrowser.open('http://embedded-tips.com')  # Go to example.com

    def onButtonPressed(self, button):
        print("Hello World!")


gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GObject, Gdk

try:
    json_data = open(os.path.dirname(os.path.abspath(__file__)) + '/conf.json').read()
    CONF_FILE_INSTANCE = json.loads(json_data)
except Exception as e:
    print(e)


class Indicator():

    @staticmethod
    def checkinternetconnection(self):
        try:
            import httplib
        except:
            import http.client as httplib

        conn = httplib.HTTPConnection("www.google.com", timeout=5)
        try:
            conn.request("HEAD", "/")
            conn.close()
            return True
        except:
            conn.close()
            return False

    def getstaticsofnetworkinterface(self, network_interface):
        path = "/sys/class/net/" + network_interface + "/statistics/"
        tx_count_path = path + "tx_bytes"
        rx_count_path = path + "rx_bytes"

        if not os.path.isdir("/sys/class/net/" + network_interface):
            return None, None

        file = open(tx_count_path, "r")
        tx_count = file.readline()
        file.close()
        file = open(rx_count_path, "r")
        rx_count = file.readline()
        file.close()
        return int(tx_count), int(rx_count)

    def haveinternetconnection(self):
        if self.checkinternetconnection(self):
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            return True
        else:
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ATTENTION)
            self.indicator.set_label(" Internet Fail!", self.applicationtitle)
            self.notifysystem("Aesir Speed Meter", "Internet connection is down!")

            return False

    @staticmethod
    def geticonpath(icon_name):
        try:
            return os.path.dirname(os.path.abspath(__file__)) + "/icons/" + icon_name + ".png"
        except Exception as e:
            print(e)
            return None

    def __init__(self):
        self.applicationtitle = 'Aesir-Speedmeter'
        self.indicator = AppIndicator3.Indicator.new(
            self.applicationtitle, self.geticonpath("active"),
            AppIndicator3.IndicatorCategory.OTHER)
        self.indicator.set_attention_icon(self.geticonpath("attention"))
        self.indicator.set_title(self.applicationtitle)
        self.indicator.set_menu(self.create_menu())
        if self.haveinternetconnection():
            self.indicator.set_label(" Internet Ok!", self.applicationtitle)
        self.measurement_result = []
        self.animation_counter_old = 0

        list2 = []
        list2.append("download")
        list2.append("upload")
        list2.append("ping")
        list2.append("sponsor")
        list2.append("timestamp")
        list2.append("ip")
        file_name = time.strftime("result_%d_%m_%Y_%H:%M.xlsx")
        self.excelhandler = AesirExcelWriter(file_name, 1)
        self.excelhandler.createTitle(list2)


        self.time_counter = 59
        self.total_animation_index = 0
        self.animation_index = 0
        self.update = Thread(target=self.main_thread_func)
        self.update.setDaemon(True)
        self.update.start()




        atexit.register(self.exithandler)

        self.current_ip_address = None
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    def exithandler(self):
        print('My application is ending!')
        self.excelhandler.closeFile()

    def open_options(self, widget):
        builder = Gtk.Builder()
        builder.add_from_file("options.glade")
        builder.connect_signals(HandlerOptionsWindow())
        window = builder.get_object("optionWindow")
        window.show_all()

    def check_updates(self, widget):
        pass

    def do_measure(self, widget):
        try:
            self.time_counter = 60
            self.notifysystem("Aesir Speedmeter", "Measurement started!")
        except Exception as e:
            print(e)

    def open_about(self, widget):

        builder = Gtk.Builder()
        builder.add_from_file("about.glade")
        builder.connect_signals(Handler())
        window = builder.get_object("aboutWindow")
        window.show_all()


    def quit(self, widget):
        self.exithandler()
        os._exit(0)

    def onmiddleclickevent(self, widget):
        if len(self.measurement_result) > 1:
            self.clipboard.set_text(self.current_ip_address, -1)
            self.notifysystem("Aesir Speedmeter", "Your IP: " +
                              str(self.current_ip_address) + " was copied to clipboard!")

    def create_menu(self):
        menu = Gtk.Menu()
        activator_item = Gtk.MenuItem()
        activator_item.set_visible(False)
        activator_item.connect("activate", self.onmiddleclickevent)
        menu.append(activator_item)
        self.indicator.set_secondary_activate_target(activator_item)
        for item in CONF_FILE_INSTANCE["menu_items"]:
            keys = item.split(" = ")
            menu_item = Gtk.MenuItem(keys[0])
            menu_item.connect('activate', getattr(self, keys[1]))
            menu.append(menu_item)
        for item in CONF_FILE_INSTANCE["check_items"]:
            keys = item.split(" = ")
            menu_item = Gtk.CheckMenuItem(keys[0])
            menu_item.connect('activate', getattr(self, keys[1]))
            menu.append(menu_item)
        for item in CONF_FILE_INSTANCE["misc_items"]:
            keys = item.split(" = ")
            menu_item = Gtk.MenuItem(keys[0])
            menu_item.connect('activate', getattr(self, keys[1]))
            menu.append(menu_item)
        menu.show_all()
        return menu

    @staticmethod
    def getactivenetworkinterface():
        try:
            return netifaces.gateways()['default'][netifaces.AF_INET][1]
        except:
            return None


    def getcurrentspeed(self):
        try:
            servers = []
            st_service = speedtest.Speedtest()
            st_service.get_servers(servers)
            st_service.get_best_server()
            self.setindicatorlabeltext("Download Test!")
            st_service.download()
            self.setindicatorlabeltext("Upload Test!")
            st_service.upload()
            self.setindicatorlabeltext("Finished Test!")
            results = st_service.results.dict()
            st_service = None
            servers = None
            return results
        except Exception as Ex:
            print(Ex)
            return None

    def notifysystem(self, title, message):
        try:
            os.system('notify-send "{}" "{}"'.format(title, message))
        except Exception as e:
            print(e)

    def animation(self, current_time):

        if len(self.measurement_result) <= 0:
            return

        if self.animation_counter_old > current_time:
            self.animation_counter_old = current_time

        if current_time - self.animation_counter_old >= 3:
            self.animation_counter_old = current_time
            self.animation_index = self.animation_index + 1

        else:
            if self.animation_index > self.total_animation_index:
                self.animation_index = 0

            GObject.idle_add(
                self.indicator.set_label,
                self.measurement_result[self.animation_index], self.applicationtitle,
                priority=GObject.PRIORITY_DEFAULT
            )
        pass

    def setindicatorlabeltext(self, label_text):
        GObject.idle_add(
            self.indicator.set_label,
            label_text, self.applicationtitle,
            priority=GObject.PRIORITY_DEFAULT
        )

    def parseresultdata(self, resultdata):
        self.measurement_result.clear()
        speed_data = " ⬇:" + str(round(resultdata['download'] / 1048576, 1)) + " MiB/s" + " ⬆:" \
                     + str(round(resultdata['upload'] / 1048576, 1)) + " MiB/s"
        self.measurement_result.append(speed_data)
        ping_data = " Ping: " + str(round(resultdata['ping'], 2)) + " ms ↔ " + \
                    resultdata['server']['sponsor'] + " (" + resultdata['server']['cc'] + ")"
        self.measurement_result.append(ping_data)
        self.total_animation_index = self.total_animation_index + 1
        self.current_ip_address = resultdata['client']['ip']
        ip_data = " IP: " + str(resultdata['client']['ip']) + " (" + str(resultdata['client']['country']) + ")"
        self.measurement_result.append(ip_data)
        self.total_animation_index = self.total_animation_index + 1
        tx_count, rx_count = self.getstaticsofnetworkinterface(self.getactivenetworkinterface())
        isp_vendor = " " + str(resultdata['client']['isp'])
        self.measurement_result.append(isp_vendor)
        self.total_animation_index = self.total_animation_index + 1

        if tx_count and rx_count is not None:
            self.total_animation_index = self.total_animation_index + 1
            bandwith_usage = " Total: ⬇: " + str(round(rx_count / 1048576000, 2)) + " GB " + "⬆: " \
                             + str(round(tx_count / 1048576000, 2)) + " GB "
            self.measurement_result.append(bandwith_usage)

    def main_thread_func(self):

        while True:
            self.time_counter = self.time_counter + 1
            time.sleep(1)
            if not self.haveinternetconnection():
                continue
            if self.time_counter < 60:
                self.animation(self.time_counter)
            else:
                self.time_counter = 0
                self.total_animation_index = 0
                self.setindicatorlabeltext(" Calculating!")
                results_dict = self.getcurrentspeed()
                if results_dict is not None:

                    x = json.dumps(results_dict, ensure_ascii=False)
                    x = json.loads(x)
                    list = []


                    list.append(x["download"])
                    list.append(x["upload"])
                    list.append(x["ping"])
                    list.append(x["server"]["sponsor"])
                    list.append(x["timestamp"])
                    list.append(x["client"]["ip"])
                    self.excelhandler.writefromlist(list)
                    self.parseresultdata(results_dict)


Indicator()
GObject.threads_init()
signal.signal(signal.SIGINT, signal.SIG_DFL)
Gtk.main()
