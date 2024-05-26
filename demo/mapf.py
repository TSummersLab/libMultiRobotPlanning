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
    print('Done!')
    with open(cleaned_output_yaml) as output_file:
        return yaml.safe_load(output_file)


if __name__ == '__main__':
    rel_path = os.path.join("scenarios", "0")
    file_path_agents = os.path.join(rel_path, "agents.txt")
    file_path_env = os.path.join(rel_path, "env.txt")
    file_path_scenario_yaml = os.path.join(rel_path, "scenario.yaml")

    N, start_loc, goal_loc = read_agents_file(file_path_agents)
    m, n, obstacles = read_env_file(file_path_env)
    generate_scenario_yaml_file(m, n, start_loc, goal_loc, obstacles, file_path_scenario_yaml)

    r = generate_schedule(file_path_scenario_yaml, rel_path, create_video=True, algo='sipp', start_pos=start_loc)