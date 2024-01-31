import json
import uuid
import os
import tkinter as tk
from tkinter import filedialog
def convert_format(input_data):
    output_data = {"version": "0.0.1", "captures": []}

    for capture in input_data["captures"]:
        # Generate unique identifiers
        capture_id = str(uuid.uuid4())
        sensor_id = str(uuid.uuid4())
        ego_id = str(uuid.uuid4())
        annotation_id = str(uuid.uuid4())

        # Extract information from the first format
        frame = input_data.get("frame", 0)
        sequence_id = input_data.get("sequence", 0)
        step = capture.get("step", 0)
        timestamp = capture.get("timestamp", 0.0)
        position = capture["position"]
        rotation = capture["rotation"]
        filename = capture.get("filename", "")
        image_format = capture.get("imageFormat", "")
        dimension = capture.get("dimension", [])
        projection = capture.get("projection", "")
        matrix = capture.get("matrix", [])
        annotations = capture.get("annotations", [])

        # Create the corresponding capture in the second format
        new_capture = {
            "id": capture_id,
            "sequence_id": sequence_id,
            "step": step,
            "timestamp": timestamp,
            "sensor": {
                "sensor_id": sensor_id,
                "ego_id": ego_id,
                "modality": "camera",
                "translation": position,
                "rotation": rotation,
                "camera_intrinsic": matrix
            },
            "ego": {
                "ego_id": ego_id,
                "translation": [0.0, 0.0, 0.0],
                "rotation": [0.0, 0.0, 0.0, 1.0]
            },
            "filename": filename,
            "format": image_format,
            "annotations": []
        }

        # Process annotations
        for annotation in annotations:
            new_annotation = {
                "id": annotation_id,
                "annotation_definition": annotation["@type"],
                "values": []
            }

            for value in annotation["values"]:
                instance_id = value["instanceId"]
                label_id = value["labelId"]
                label_name = value["labelName"]
                origin = value["origin"]
                dimension = value["dimension"]

                new_value = {
                    "label_id": label_id,
                    "label_name": label_name,
                    "instance_id": instance_id,
                    "x": origin[0],
                    "y": origin[1],
                    "width": dimension[0],
                    "height": dimension[1]
                }

                new_annotation["values"].append(new_value)

            new_capture["annotations"].append(new_annotation)

        # Add the new capture to the output data
        output_data["captures"].append(new_capture)

    return output_data

def load_all_jsons_from_folder(folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]

    if not json_files:
        raise ValueError("No JSON files found in the specified folder.")

    json_data_list = []

    for json_file in json_files:
        file_path = os.path.join(folder_path, json_file)
        try:
            with open(file_path, "r") as file:
                json_data_list.append((json_file, json.load(file)))
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in {file_path}: {e}")

    return json_data_list

def choose_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    folder_path = filedialog.askdirectory(title="Select Folder")

    return folder_path

def create_output_folder(script_directory):
    output_folder = os.path.join(script_directory, "output_folder")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    return output_folder

if __name__ == "__main__":
    # Get the directory where the script is located
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Choose a folder
    folder_path = choose_folder()

    try:
        # Load all JSON files from the chosen folder
        json_data_list = load_all_jsons_from_folder(folder_path)
    except ValueError as e:
        print(f"Error: {e}")
        exit()

    # Create an output folder in the script's directory
    output_folder = create_output_folder(script_directory)

    for json_file, json_data in json_data_list:
        # Perform conversion for each JSON file
        output_data = convert_format(json_data)

        # Define the output file path in the output folder
        output_file_path = os.path.join(output_folder, f"converted_{json_file}")

        # Write the resulting JSON to a new file in the output folder
        with open(output_file_path, "w") as output_file:
            json.dump(output_data, output_file, indent=2)
