import subprocess, json, sys, time


def exec_cmd(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    out = out.decode("utf-8", errors='ignore').split('\n')
    return out, err


def get_fan_rpm():
    cmd = 'sensors | grep RPM'
    out, err = exec_cmd(cmd)
    fans = []

    for fan in out:
        fan_dict = {}
        if len(fan) > 0:
            fan = fan.split()
            fan_dict['name'] = fan[0][:-1]
            fan_dict['rpm'] = fan[1]
            fans.append(json.dumps(fan_dict))
    return fans


def get_cpu_temps():
    raspi_cpu = "cat /sys/class/thermal/thermal_zone0/temps"
    cpu_temps = []
    cmd = 'sensors | grep °C'

    out_raspi, err_raspi = exec_cmd(raspi_cpu)

    print("out_raspi", out_raspi)

    try:
        out, err = exec_cmd(cmd)

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
                cpu_temps.append(json.dumps(temp_dict))
    except Exception as e:
        pass
    return cpu_temps


def get_device_temps():
    cmd = "fdisk -l | grep 'Disk /dev/sd'"
    out, err = exec_cmd(cmd)
    device_temp = []

    for device in out:
        if len(device) > 0:
            device = device.split()
            device_data = {}
            device_data['location'] = device[1]

            out_hdtemp, err_hdtemp = exec_cmd(
                "smartctl {} -a | grep Temperature_Celsius".format(device[1].replace(":", "")))

            out_hdtemp = out_hdtemp[0].split()
            device_data["value"] = out_hdtemp[9]

            out_hdmodel, err_hdmodel = exec_cmd(
                "smartctl {} -a | grep 'Device Model'".format(device[1].replace(":", "")))
            out_hdmodel = out_hdmodel[0].split(": ")

            device_name = out_hdmodel[1]
            while (device_name[0] == " "):
                device_name = device_name[1:]

            device_data["name"] = device_name

            try:
                device_data["minmax"] = out_hdtemp[11][:-1]
            except Exception as e:
                pass

            device_temp.append(json.dumps(device_data))
    return device_temp


if __name__ == "__main__":
    tmp_dir = "/tmp/"

    args = sys.argv

    if len(args) < 2:
        args.append("-o")

    if args[1] == "-c" or args[1] == "--cpu":
        cpu_temps = get_cpu_temps()
        print(cpu_temps)

    elif args[1] == "-f" or args[1] == "--fan":
        fan = get_fan_rpm()
        print(fan)

    elif args[1] == "-d" or args[1] == "--device":
        device_temps = get_device_temps()
        print(device_temps)

    elif args[1] == "-t":
        while True:
            temps_json = {}
            temps_json['cpu'] = get_cpu_temps()
            temps_json['device'] = get_device_temps()
            temps_json['fan'] = get_fan_rpm()
            temps_json = json.dumps(temps_json).replace("\\\"", "\"")
            with open(tmp_dir + "systemps.txt", "w+") as f:
                f.write(temps_json)
            time.sleep(5)
    elif args[1] == "-o":
        temps_json = {}
        temps_json['cpu'] = get_cpu_temps()
        temps_json['device'] = get_device_temps()
        temps_json['fan'] = get_fan_rpm()
        temps_json = json.dumps(temps_json).replace("\\\"", "\"")
        with open(tmp_dir + "systemps.txt", "w+") as f:
            f.write(temps_json)
    elif args[1] == "-l" or args[1] == "--list":
        cpu_temps = get_cpu_temps()
        device_temps = get_device_temps()
        fans = get_fan_rpm()
        for cpu_temp in cpu_temps:
            cpu_temp = json.loads(cpu_temp)
            print(cpu_temp['name'], cpu_temp['value'])
        for device in device_temps:
            device = json.loads(device)
            print(device['name'], device['location'], device['value'])
        for fan in fans:
            fan = json.loads(fan)
            print(fan['name'], fan['rpm'])
