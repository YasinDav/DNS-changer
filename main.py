import subprocess
from tkinter import *
from tkinter import messagebox
import tkinter as tk
from time import sleep

# اطلاعات مورد نیاز برای تنظیم DNS
shekan_dns = ["178.22.122.100", "185.51.200.2"]
b403_dns = ["10.202.10.202", "10.202.10.102"]

def get_saved_wifi_profiles():
    try:
        # اجرای دستور برای نمایش پروفایل‌های Wi-Fi ذخیره شده
        output = subprocess.check_output("netsh wlan show profiles", shell=True, text=True)

        # استخراج نام پروفایل‌ها (SSID های ذخیره شده)
        profiles = []
        for line in output.splitlines():
            if "All User Profile" in line:
                profile_name = line.split(":")[1].strip()
                profiles.append(profile_name)

        return profiles

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error find saved wifis", str(e))
        return []

def set_dns(interface_name, preferred_dns, alternate_dns):
    try:
        # تنظیم DNS اصلی
        subprocess.run(f'netsh interface ip set dns name="{interface_name}" static {preferred_dns}', check=True,
                       shell=True)

        # تنظیم DNS جایگزین
        subprocess.run(f'netsh interface ip add dns name="{interface_name}" {alternate_dns} index=2', check=True,
                       shell=True)

        messagebox.showinfo("Changed DNS", "Successfully changed DNS\nEnjoy your network!")
        return True
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error set DNS", str(e))
        return False

def get_connected_wifi():
    try:
        output = subprocess.check_output("netsh wlan show interfaces", shell=True, text=True)
        for line in output.splitlines():
            if "SSID" in line and "BSSID" not in line:
                connected_ssid = line.split(":")[1].strip()
                return connected_ssid
        return None
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error find connected networks", str(e))
        return None

def reset_dns(interface_name):
    if interface_name:
        try:
            # بازگرداندن تنظیمات DNS به حالت خودکار
            subprocess.run(f'netsh interface ip set dns name="{interface_name}" source=dhcp', check=True, shell=True)
            messagebox.showinfo("Successfully reset DNS", f"Successfully reset {interface_name} network")

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error set DNS defult", str(e))
    else:
        messagebox.showerror("Error emtpy interface", "You must provide an interface\nBefore reset, set an interface")

def get_network_interfaces():
    try:
        # اجرای دستور برای نمایش رابط‌های شبکه
        output = subprocess.check_output("netsh interface show interface", shell=True, text=True)

        # پردازش خروجی برای پیدا کردن نام رابط‌ها
        interfaces = []
        for line in output.splitlines():
            # تنها خطوطی که شامل نام رابط‌ها هستند را فیلتر می‌کنیم
            parts = line.split()
            if len(parts) >= 4 and parts[0] != "Admin":
                interface_name = " ".join(parts[3:])  # نام رابط شبکه در ستون چهارم به بعد است
                interfaces.append(interface_name)

        return interfaces

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error find network interfaces", str(e))
        return []

class Main(Tk):
    def __init__(self):
        super().__init__()
        self.network = None
        self.title("DNS Changer")
        self.geometry("400x450")
        self.resizable(False, False)
        self.bg_image = PhotoImage(file="./img/bg.png")
        self.d403_online = PhotoImage(file="./img/403 (Custom).png")
        self.shekan = PhotoImage(file="./img/shekan (Custom).png")
        self.bg = Label(self, image=self.bg_image).place(x=0, y=0)
        self.wifi_selection = Frame(self)
        self.button = Frame(self)
        self.button.pack(side = BOTTOM)
        Label(self.wifi_selection, text="WiFi Selection").pack(side=TOP)
        Button(self.button, bd = 0, image=self.shekan, command=lambda: self.change(shekan_dns), width=100, height=80).pack(side=LEFT, ipadx=5, ipady=5)
        Button(self.button, bd = 0, image=self.d403_online, command=lambda: self.change(b403_dns), width=100, height=80).pack(side=RIGHT, ipadx=5, ipady=5)
        self.wifi_selection.pack(side=TOP, fill=BOTH)
        self.list_wifi = tk.Listbox(self.wifi_selection, width=40, height=15)
        self.list_wifi.pack(side=TOP, fill=X)
        Button(self, bd=0, text="Refresh WiFis' list", command=self.start).pack()
        Button(self, bd=0, text="Reset DNS", command=lambda: reset_dns(self.network)).pack()
        self.start()
    def start(self):
        self.list_wifi.delete(0, END)
        sleep(2)
        connected_wifi = get_connected_wifi()
        wifis = get_saved_wifi_profiles()
        wifis.remove(connected_wifi)
        wifis.sort()
        interface = get_network_interfaces()
        for profile in interface:
            self.list_wifi.insert(END, profile)
        self.list_wifi.insert(END, connected_wifi)
        for profile in wifis:
            self.list_wifi.insert(END, profile)
    def change(self, DNS:list[str]):
        selected = self.list_wifi.curselection()  # به دست آوردن اندیس انتخاب شده
        if selected:
            selected_value = self.list_wifi.get(selected[0])  # گرفتن مقدار انتخاب شده
            status = set_dns(selected_value, DNS[0], DNS[1])
            if status:
                self.network = selected_value
        else:
            messagebox.showwarning("Error", "Please select a WiFi")



if __name__ == "__main__":
    root = Main()
    root.mainloop()