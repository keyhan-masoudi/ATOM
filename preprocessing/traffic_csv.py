from utils.paths import DATA_ROOT, CACHE_ROOT
import os
import xml.etree.ElementTree as ET
import pandas as pd

input_file = str(DATA_ROOT / "vehicles" / "chunk_0.xml")

tree = ET.parse(input_file)
root = tree.getroot()

os.makedirs(str(CACHE_ROOT / "traffic_csv"), exist_ok=True)

data = []

for timestep in root.findall("timestep"):
    time_value = timestep.get("time")
    for vehicle in timestep.findall("vehicle"):
        vehicle_id = vehicle.get("id")
        x = float(vehicle.get("x"))
        y = float(vehicle.get("y"))
        angle = float(vehicle.get("angle"))
        speed = float(vehicle.get("speed"))

        data.append([int(time_value), vehicle_id, x, y, speed, angle])

df = pd.DataFrame(data, columns=["time", "vehicle_id", "x", "y", "speed", "angle"])

for time_value, group in df.groupby("time"):
    output_file = os.path.join(str(CACHE_ROOT / "traffic_csv"), f"dataInTime{time_value}.csv")
    if os.path.exists(output_file):
        print(f"{output_file} ignored!")
        continue
    group.to_csv(output_file, index=False)
    print(f"{output_file} saved!\n")
