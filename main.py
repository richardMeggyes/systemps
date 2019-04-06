import subprocess, json

def exec_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    out = out.decode("utf-8", errors='ignore').split('\n')
    return out, err

def get_cpu_temps():
    cpu_temps = []
    cmd = 'sensors | grep °C'

    out, err  = exec_cmd(cmd)

    for temp in out:
        temp_dict = {}
        if len(temp) > 0:
            temp_name = temp.split(":")[0]
            temp_data = temp.split(":")[1].split()
            temp_dict["name"] = temp_name
            temp_dict["value"] = temp_data[0].replace("+", "").split(".")[0]

            try:
                high_index = temp_data.index("(high")
                temp_high = temp_data[high_index + 2].replace("+", "").split(".")[0]
                temp_dict["high"] = temp_high
            except ValueError:
                pass

            try:
                crit_index = temp_data.index("crit")
                temp_crit = temp_data[crit_index + 2].replace("+", "").split(".")[0]
                temp_dict["crit"] = temp_crit
            except ValueError:
                pass

            try:
                crit_index = temp_data.index("(crit")
                temp_crit = temp_data[crit_index + 2].replace("+", "").split(".")[0]
                temp_dict["crit"] = temp_crit
            except ValueError:
                pass
        cpu_temps.append(temp_dict)
    return cpu_temps

def get_device_temps():
    cmd = "fdisk -l | grep 'Disk /dev/sd'"
    out, err = exec_cmd(cmd)
    device_temp = []

    for device in out:
        if len(device) > 0:
            device = device.split()
            device_data = {}
            device_data['type'] = device[0]
            device_data['location'] = device[1]
            out_hdtemp, err_hdtemp = exec_cmd("hddtemp " + device[1].replace(":", ""))
            device_data["value"] = out_hdtemp[0].split(": ")[2]

            device_temp.append(device_data)
    return device_temp

if __name__ == "__main__":
    cpu_temps = get_cpu_temps()

    device_temps = get_device_temps()

    for cpu_temp in cpu_temps:
        print(cpu_temp)


    for device in device_temps:
        print(device)