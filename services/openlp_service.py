import os
import zipfile
import json


def unzip_file(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)


def extract_service_items(service_dir):
    osj_path = os.path.join(service_dir, "service_data.osj")

    if not os.path.exists(osj_path):
        print(f"\n❌ service_data.osj not found at: {osj_path}")
        return []

    with open(osj_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("\n❌ invalid osj format (not a list)")
        return []


    service_items = []

    # index 0 is useless
    for item in data[1:]:
        if isinstance(item, dict) and "serviceitem" in item:
            if item['serviceitem']['header']['name'] == 'songs':
                service_items.append(item["serviceitem"]['data'])

    print("\n===== service items extracted =====")
    for idx, item in enumerate(service_items, 1):
        print(f"\n----- item {idx} -----")
        print(json.dumps(item, indent=2, ensure_ascii=False))

    print("\n====================================\n")

    return service_items


