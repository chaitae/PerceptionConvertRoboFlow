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

def load_first_json_from_folder(folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]

    if not json_files:
        raise ValueError("No JSON files found in the specified folder.")

    first_json_file = os.path.join(folder_path, json_files[0])

    with open(first_json_file, "r") as file:
        return json.load(file)

def choose_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    folder_path = filedialog.askdirectory(title="Select Folder")

    return folder_path

if __name__ == "__main__":
    # Choose a folder
    folder_path = choose_folder()

    try:
        # Load the first JSON file from the chosen folder
        input_data = load_first_json_from_folder(folder_path)
    except ValueError as e:
        print(f"Error: {e}")
        exit()

    # Perform conversion
    output_data = convert_format(input_data)

    # Print the resulting JSON
    print(json.dumps(output_data, indent=2))
