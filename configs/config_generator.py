import os
import random
import argparse


def random_value_old(value, dtype='usize'):
    value_list = [value]

    if dtype == 'f64':
        value = float(value)
        value_list.extend([value * 1.1, value * 0.9])
    else:
        value = int(value)
        value_list.extend([int(value * 1.1), int(value * 0.9)])
    if args.random:
        return random.choices(value_list, weights=(0.6, 0.2, 0.2))[0]
    else:
        return value


def random_value(value, dtype='usize', diff=1.3, share_unchanged=0.6):
    # 1276+ datapoint
    value_list = [value]
    if dtype == 'f64':
        value = float(value)
        value_list.extend([value * random.uniform(1, diff), value / random.uniform(1, diff)])
    else:
        value = int(value)
        value_list.extend([int(value * random.uniform(1, diff)), int(value / random.uniform(1, diff))])
    if args.random:
        return random.choices(value_list, weights=(share_unchanged, (1-share_unchanged)/2, (1-share_unchanged)/2))[0]
    else:
        return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='creating config file')
    parser.add_argument('--random', action='store_true', help='is random configs')
    parser.add_argument('--output', default="./generated/config.toml", type=str, help='output file path')
    parser.add_argument('--dev', action='store_true', help='dev config')
    args = parser.parse_args()

    if args.dev:
        os.popen('cp ./generated/config.toml ' + args.output)
    else:
        constants = {}
        file = open(args.output, "w")
        with open("config.toml") as original_config_file:
            for line in original_config_file:
                line_details = line.split(" ")
                if line[0] == "#" or line == "\n":
                    continue
                if line_details[0][0] == "[":
                    file.write(line.strip()+"\n")
                    continue
                if line_details[1] == '=':
                    value = line_details[2].replace("_", "")
                    value_type = line_details[4].strip()
                    constants[line_details[0]] = [value, value_type, random_value(value, value_type)]
                    file.write(line_details[0] + ' = ' + str(constants[line_details[0]][2]) + "\n")
