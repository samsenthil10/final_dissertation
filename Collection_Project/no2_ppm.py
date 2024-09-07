import time
from machine import Pin, ADC

vrefraw = ADC(27)
vgasraw = ADC(26)

conversion_factor = 3.3 / 65535

Sc = -25.08
TIA = 499
M = Sc * TIA

ppb_to_ugm3 = 1.9125

print("MPY: soft reboot")
print("Place the sensor in clean air for zeroing...")
print("Please wait for 1 min...")

z = 0
zsum = 0
while z < 12:
    vrefsum = 0
    vgassum = 0

    for x in range(5000):
        vrefsum += vrefraw.read_u16() * conversion_factor
        vgassum += vgasraw.read_u16() * conversion_factor
        time.sleep(0.001)

    vref = vrefsum / 5000
    vgas = vgassum / 5000

    Cx = (1 / M) * (vgas - vref)
    zsum += Cx
    z += 1
    
    time.sleep(0.1)

zavg = zsum / 12

filename = "no2dataset.csv"
file_exists = False

try:
    with open(filename, "r"):
        file_exists = True
except OSError:
    file_exists = False

has_header = False

if file_exists:
    with open(filename, "r") as f:
        first_line = f.readline().strip()
        if first_line.startswith("Date,Time,NO2 ppb,NO2 µg/m³"):
            has_header = True

file_mode = "a" if file_exists and has_header else "w"

if not file_exists or not has_header:
    with open(filename, file_mode) as file:
        file.write("Date,Time,NO2 ppb,NO2 µg/m³")

try:
    current_time = time.gmtime()
    seconds_to_next_minute = 60 - current_time[5]
    time.sleep(seconds_to_next_minute)
    while True:

        vrefsum = 0
        vgassum = 0

        for x in range(5000):
            vrefsum += vrefraw.read_u16() * conversion_factor
            vgassum += vgasraw.read_u16() * conversion_factor
            time.sleep(0.001)
        vref = vrefsum / 5000
        vgas = vgassum / 5000

        Cx_ppb = ((1 / M) * (vgas - vref)) - zavg
        Cx_ppb = Cx_ppb * 460000

        Cx_ugm3 = Cx_ppb * ppb_to_ugm3

        current_time = time.gmtime()

        date_value = "{:02}-{:02}-{:02}".format(
            current_time[2], current_time[1], current_time[0] % 100
        )
        time_value = "{:02}:{:02}:{:02}".format(
            current_time[3], current_time[4], current_time[5]
        )

        with open(filename, "a") as file:
            file.write("\n{},{},{:.7f},{:.7f}".format(date_value, time_value, Cx_ppb, Cx_ugm3))

        print('***********************')
        print("Date: {}".format(date_value))
        print("Time: {}".format(time_value))
        print("NO2 = {:.7f} ppb".format(Cx_ppb))
        print("NO2 = {:.7f} µg/m³".format(Cx_ugm3))
        print('***********************')

        time.sleep(60-0.001)

except KeyboardInterrupt:
    print("Measurement stopped by user.")
except Exception as e:
    print("An error occurred: {}".format(e))
finally:
    print("Measurement complete.")
