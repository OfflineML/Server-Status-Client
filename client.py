import psutil
import time
import os
import json
import sys
import subprocess
import requests
import time
import glob


SAMPLING_INTERVAL = 30

def get_cpu_usage():
    return round(psutil.cpu_percent(interval=1), 2)

def get_ram_usage():
    memory = psutil.virtual_memory()
    
    return round(memory.total/(1024*1024)), round(memory.used/(1024*1024))

def get_hdd_usage(disk_size_threshold=10):
    hdd_health = []
    
    partitions = psutil.disk_partitions()
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue
        
        total_gb = partition_usage.total / (2**30)
        
        # Only consider partitions with size >= 1 GB
        if total_gb >= disk_size_threshold:
            status = {
                "device": partition.device,
                "mount_point": partition.mountpoint,
                "fstype": partition.fstype,
                "total": round(total_gb, 2),
                "used": round(partition_usage.used / (2**30), 2),
                "free": round(partition_usage.free / (2**30), 2),
                "percent": partition_usage.percent
            }
            
            hdd_health.append(status)
    
    return hdd_health

def measure_disk_speed(avg_disk_io):
    """
    Measure the disk speed for the given partition.
    Note: This is not the actual disk speed, but the speed of the disk when the system is idle.
    """
    try:
        # ISOLATION
        # Lock this process to a single CPU core and prevent other processes from using it
        process = psutil.Process(os.getpid())
        core_id = 0  # Use the first CPU core (index 0)
        process.cpu_affinity([core_id])
        
        # Set real-time priority to further isolate the process
        if sys.platform.startswith('linux'):
            try:
                os.sched_setscheduler(0, os.SCHED_FIFO, os.sched_param(99))
            except PermissionError:
                print("Warning: Unable to set real-time priority. Run with higher privileges for better isolation.")
            except AttributeError:
                print("Warning: sched_setscheduler not available on this system. Real-time priority not set.")
        else:
            print("Warning: Real-time priority setting is only supported on Linux systems.")

        # Optionally, you can use taskset on Linux for even stricter isolation
        if sys.platform.startswith('linux'):
            try:
                subprocess.run(['taskset', '-cp', str(core_id), str(os.getpid())], check=True)
            except subprocess.CalledProcessError:
                print("Warning: Unable to use taskset. Continuing without it.")
        
        # Get initial disk I/O counters for the specific partition
        directory = "/tmp"
        write_vol = 100
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        test_file = os.path.join(directory, 'test_file.bin')
        # Measure write speed
        t = time.time()
        with open(test_file, 'wb') as f:
            f.write(os.urandom(write_vol * 1024 * 1024))
        t = time.time() - t
        
        # Reset the CPU affinity and priority to default after execution
        process.cpu_affinity(list(range(psutil.cpu_count(logical=False))))
        if sys.platform.startswith('linux'):
            try:
                os.sched_setscheduler(0, os.SCHED_OTHER, os.sched_param(0))
            except PermissionError:
                print("Warning: Unable to reset real-time priority. Run with higher privileges for better isolation.")
            except AttributeError:
                print("Warning: sched_setscheduler not available on this system. Real-time priority not reset.")

        # Clean up the test file
        os.remove(test_file)
        return round(2*(write_vol/t+avg_disk_io["writes"]), 2) # assumes the read write speed is 2x of the write speed
    except Exception as ex:
        print(ex)
        # If there's any error in getting disk I/O stats, return None for both speeds
        return None


def get_disk_io():
    # Get disk I/O statistics
    disk_io_old = psutil.disk_io_counters()
    time.sleep(SAMPLING_INTERVAL)
    disk_io_new = psutil.disk_io_counters()
    return {"reads": (disk_io_new.read_bytes - disk_io_old.read_bytes) / (SAMPLING_INTERVAL * 1024 * 1024), 
            "writes": (disk_io_new.write_bytes - disk_io_old.write_bytes) / (SAMPLING_INTERVAL * 1024 * 1024)}


def get_status():
    try:
        with open("cache.json", "r") as f:
            cache = json.load(f)
    except Exception:
        cache = {}

    config_template = {
        "min_disk_size_threshold": 10,
        "disk_speed_sample_interval": 84000,
        "partitions": {
        },
        "main_partition": "/",
        "tracked_apps":[]
    }
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except Exception:
        config = config_template
    hdd = get_hdd_usage(config["min_disk_size_threshold"])

    results = {"partitions":[]}
    for entry in hdd:
        mount_point = entry["mount_point"]
        if mount_point in config["partitions"] and config["partitions"][mount_point]["show"]:
            entry_formatted = {"mount_point": mount_point}
            if mount_point not in cache or cache[mount_point].get("display_name") != config["partitions"][mount_point]["display_name"]:
                entry_formatted["display_name"] = config["partitions"][mount_point]["display_name"]
                cache.setdefault(mount_point, {})["display_name"] = config["partitions"][mount_point]["display_name"]
            if mount_point not in cache or cache[mount_point].get("total") != entry["total"]:
                entry_formatted["total"] = entry["total"]
                cache.setdefault(mount_point, {})["total"] = entry["total"]
            if mount_point not in cache or cache[mount_point].get("used") != entry["used"]:
                entry_formatted["used"] = entry["used"]
                cache.setdefault(mount_point, {})["used"] = entry["used"]
            results["partitions"].append(entry_formatted)

        elif mount_point not in config["partitions"]:
            config["partitions"][mount_point] = {
                "display_name": mount_point,
                "show": True
            }
            entry_formatted = {
                "display_name": mount_point,
                "total": entry["total"],
                "used": entry["used"],
                "mount_point": mount_point
            }
            cache[mount_point] = {
                "display_name": mount_point,
                "total": entry["total"],
                "used": entry["used"]
            }
            results["partitions"].append(entry_formatted)
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    results["cpu_usage"] = get_cpu_usage()
    total_ram, used_ram = get_ram_usage()
    results["ram_usage"] = round(used_ram/total_ram, 2)

    avg_disk_io = get_disk_io()
    # Calculate disk performance once a day only
    if cache.get("disk_speed", None) is None or time.time() - cache["disk_speed"]["timestamp"] > config["disk_speed_sample_interval"]:
        cache["disk_speed"] = {"timestamp": time.time(), "speed": measure_disk_speed(avg_disk_io)}
        results["disk_usage"] = round((avg_disk_io["reads"]+avg_disk_io["writes"])/cache["disk_speed"]["speed"], 2)
        results["disk_speed"] = cache["disk_speed"]["speed"]
    else:
        results["disk_usage"] = round((avg_disk_io["reads"]+avg_disk_io["writes"])*100/cache["disk_speed"]["speed"], 2)
    if "ram" not in cache or cache["ram"] != total_ram:
        cache["ram"] = total_ram
        results["ram"] = total_ram

    cores = psutil.cpu_count(logical=False)
    if "cores" not in cache or cache["cores"] != cores:
        cache["cores"] = psutil.cpu_count(logical=False)
        results["cores"] = cache["cores"]

    with open("cache.json", "w") as f:
        json.dump(cache, f, indent=4)

    return results


if __name__ == "__main__":
    if os.path.exists("cache.json"):
        os.remove("cache.json")
    while True:
        api_config_files = glob.glob("*api_configs*")
        if api_config_files:
            with open(api_config_files[0], "r") as f:
                api_configs = json.load(f)
        else:
            raise FileNotFoundError("No api_configs file found in the local directory.")
        
        t = time.time()
        status = get_status()
        status["api_key"] = api_configs["api_key"]
        response = requests.post(api_configs["endpoint"], json=status)
        if response.status_code == 200:
            print("Status sent successfully")
        else:
            print(f"Failed to send status: {response.status_code}")
        time.sleep(max(0, 60-(time.time()-t)))



"""
       {
        "frequency": 1,
        "partitions": {
            "/": {
                "display_name": "/",
                "show": True
            },
            "/home": {
                "display_name": "/home",
                "show": True
            },
            "/tmp": {
                "display_name": "/tmp",
                "show": False
            },
            
        },
        "main_partition": "/",
        "tracked_apps":[]
    }
"""
