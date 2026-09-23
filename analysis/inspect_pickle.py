from utils.paths import CACHE_ROOT
import pickle

# change your pkl file name to see the overview of it
file_path = str(CACHE_ROOT / "hex_traffic_predictions.pkl")

try:
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    print(data)

except Exception as e:
    print(f"error: {e}")