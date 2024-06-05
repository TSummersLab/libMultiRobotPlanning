import subprocess
import yaml
import os
from utils import *


def generate_schedule(scenario_yaml, relative_path=".", create_video=False, algo='sipp', start_pos=None):
    output_yaml = os.path.join(relative_path, "output.yaml")
    cleaned_output_yaml = os.path.join(relative_path, "output_cleaned.yaml")
    if algo == 'sipp':
        subprocess.run(
            ["../build/mapf_prioritized_sipp",
             "-i", scenario_yaml,
             "-o", output_yaml,
             ],
            check=True)
    else:
        raise NotImplemented("Chosen algorithm not supported")

    print("Planning done.")
    cleanup_result_yaml_file(output_yaml, cleaned_output_yaml, start_pos)
    if create_video:
        print("Generating video...")
        subprocess.run(
            ["python3", "../example/visualize.py",
             scenario_yaml,
             cleaned_output_yaml,
             "--video", os.path.splitext(scenario_yaml)[0] + "_" + algo + "_video.mp4"],
            check=True)
        print('Generating video done)')

    print('Saving cleaned yaml')
    with open(cleaned_output_yaml) as output_file:
        yaml.safe_load(output_file)

    print('Saving text version of yaml that can be read into a balanced list')
    schedule_output_txt = os.path.join(relative_path, "schedule.txt")
    schedule_list = read_clean_yaml_into_list(cleaned_output_yaml)
    save_schedule_list_to_file(schedule_list, schedule_output_txt)
    schedule_list_read = read_schedule_list_from_file(schedule_output_txt)
    print('Saved txt file, when read into list, matches the original schedule list: ', schedule_list == schedule_list_read)

    print('Saving schedule list using global coordinates')
    schedule_output_global_txt = os.path.join(relative_path, "schedule_global.txt")
    schedule_list_global = transform_coordinates_to_world(schedule_list, x0=5, y0=7, grid_len=0.582)
    save_schedule_list_to_file(schedule_list_global, schedule_output_global_txt)
    schedule_list_global_read = read_schedule_list_from_file(schedule_output_global_txt)
    print('Saved global txt file, when read into list, matches the original schedule list: ',
          schedule_list_global == schedule_list_global_read)
    print("Done!")


if __name__ == '__main__':
    rel_path = os.path.join("scenarios", "0")
    file_path_agents = os.path.join(rel_path, "agents.txt")
    file_path_env = os.path.join(rel_path, "env.txt")
    file_path_scenario_yaml = os.path.join(rel_path, "scenario.yaml")

    N, start_loc, goal_loc = read_agents_file(file_path_agents)
    m, n, obstacles = read_env_file(file_path_env)
    generate_scenario_yaml_file(m, n, start_loc, goal_loc, obstacles, file_path_scenario_yaml)

    r = generate_schedule(file_path_scenario_yaml, rel_path, create_video=True, algo='sipp', start_pos=start_loc)