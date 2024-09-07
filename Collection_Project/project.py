import time
import csv
import os
from pms5003 import PMS5003, ReadTimeoutError
from scd30_i2c import SCD30

def remaining_seconds():
    now = time.localtime()
    return 60 - now.tm_sec

interval = 60

pms5003 = PMS5003()
scd30 = SCD30()
time.sleep(1.0)

csv_file = 'dataset.csv'

def csv_has_header(filename):
    if os.path.isfile(filename):
        with open(filename, 'r') as file:
            first_line = file.readline().strip()
            return first_line.startswith('Date,')

try:
    file_exists = os.path.isfile(csv_file)
    if not file_exists or not csv_has_header(csv_file):
        header_written = False
    else:
        header_written = True

    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        for i in range(0, 15):
                    readings = pms5003.read()
        time.sleep(remaining_seconds())
        while True:
            try:
                readings = pms5003.read()
                if scd30.get_data_ready():
                    m = scd30.read_measurement()
                    if m is not None:
                        co2_reading = f"{m[0]:.2f}"
                        temp_reading = f"{m[1]:.2f}"
                        rh_reading = f"{m[2]:.2f}"
                
                readings_str = str(readings)
                lines = readings_str.split('\n')
                
                data_dict = {}
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        data_dict[key.strip()] = value.strip()

                if not header_written:
                    csv_header = []
                    csv_header.append("Date")
                    csv_header.append("Time")
                    for item in data_dict.keys():
                        csv_header.append(str(item))
                    csv_header.append("CO2 in ppm")
                    csv_header.append("Temperature in C")
                    csv_header.append("Relative Humidity")
                    writer.writerow(csv_header)
                    print(csv_header)
                    header_written = True

                # Get the current time formatted to the beginning of the minute
                current_date = time.strftime("%Y-%m-%d")
                current_time = time.strftime("%H:%M:%S")

                row = [current_date] + [current_time] + list(data_dict.values()) + [co2_reading, temp_reading, rh_reading]
                writer.writerow(row)
                print(row)

                time.sleep(interval)

            except ReadTimeoutError:
                pms5003 = PMS5003()
                scd30 = SCD30()

except KeyboardInterrupt:
    pass



