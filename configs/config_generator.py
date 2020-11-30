import os
import random

def random_value(value, dtype = 'usize'):
    value_list = [value]

    if dtype == 'f64':
        value = float(value)
        value_list.extend([value * 1.1, value * 0.9])
    else:
        value = int(value)
        value_list.extend([int(value * 1.1), int(value * 0.9)])
    return random.choice(value_list)
    #return value_list[0]


constants = {}
file = open("generated/config.toml", "w")

with open("config.toml") as original_config_file:
    for line in original_config_file:
        line_details = line.split(" ")
        if line[0] == "#" or line == "\n":
            continue
        if line_details[0][0] == "[":
            file.write(line.strip()+"\n")
            continue
        if line_details[1] == '=':
            value = line_details[2].replace("_","")
            value_type = line_details[4].strip()
            constants[line_details[0]] = [value, value_type, random_value(value, value_type)]
            file.write(line_details[0] + ' = ' + str(constants[line_details[0]][2]) + "\n")

# for k in constants.keys():
#    print(k, constants[k])