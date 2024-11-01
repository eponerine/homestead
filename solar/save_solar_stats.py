from renogymodbus import RenogyChargeController
from datetime import datetime, timezone
import json, influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

# Load the config
with open('./config.json') as config_file:
    config = json.load(config_file)
    config_file.close()

# InfluxDB connection variables
influxDB_bucket   = config['influxDB_bucket']
influxDB_location = config['influxDB_location']
influxDB_org      = config['influxDB_org']
influxDB_token    = config['influxDB_token']
influxDB_url      = config['influxDB_url']

# Renogy serial connection
controller = RenogyChargeController("/dev/ttyUSB0", 1)

current_time = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
solar_voltage = float(controller.get_solar_voltage())
solar_current = float(controller.get_solar_current())
solar_power = float(controller.get_solar_power())
load_voltage = float(controller.get_load_voltage())
load_current = float(controller.get_load_current())
load_power = float(controller.get_load_power())
battery_voltage = float(controller.get_battery_voltage())
battery_soc = float(controller.get_battery_state_of_charge())
battery_temp = float(controller.get_battery_temperature())
controller_temp = float(controller.get_controller_temperature())

# CPU Temperature
# Open the file and divide by 1000 for value in Centigrade
file = open("/sys/class/thermal/thermal_zone0/temp")
cpu_temp = (float(file.read()) / 1000)
file.close()

# Output to stdout
print(current_time, end=',')
print(solar_voltage, end=',')
print(solar_current, end=',')
print(solar_power, end=',')
print(load_voltage, end=',')
print(load_current, end=',')
print(load_power, end=',')
print(battery_voltage, end=',')
print(battery_soc, end=',')
print(battery_temp, end=',')
print(controller_temp, end=',')
print(cpu_temp)

# Connect to InfluxDB
influxDB_client = influxdb_client.InfluxDBClient(url=influxDB_url,token=influxDB_token,org=influxDB_org)
influxDB_writer = influxDB_client.write_api(write_options=SYNCHRONOUS)

# Write to InfluxDB
influxDB_writer.write(bucket=influxDB_bucket, record=[influxdb_client.Point("myMeasurement").tag("location", influxDB_location).field("solar_voltage", solar_voltage).field("solar_current", solar_current).field("solar_power", solar_power).field("load_voltage", load_voltage).field("load_current", load_current).field("load_power", load_power).field("battery_voltage",battery_voltage).field("battery_soc",battery_soc).field("battery_temp",battery_temp).field("controller_temp",controller_temp).field("cpu_temp",cpu_temp)])
