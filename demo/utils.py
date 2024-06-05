"""
Utility functions that support the solution.
"""
import os
import yaml


def read_agents_file(file_path):
    """
    Reads the agents file containing the start and end locations.
    Returns the number of agents and two lists containing the start and goal locations
    """
    from_data, to_data = [], []
    with open(file_path, 'r') as file:
        for line in file:
            x_from, y_from, x_to, y_to = map(int, line.strip().split(','))  # remove leading/trailing spaces, split at ",", then cast into ints
            # save into lists
            from_data.append([x_from, y_from])
            to_data.append([x_to, y_to])
    N = len(from_data)  # number of agents = number of rows = length of from-to pairs
    return N, from_data, to_data


def read_env_file(file_path):
    """
    Read the environment file containing the size of the grid and the location of obstacles.
    Returns the dimensions of the environment and a list of obstacle locations
    """
    data = []
    with open(file_path, 'r') as file:
        m, n = map(int, next(file).strip().split(','))  # read the first line
        for line in file:
            x, y = map(int, line.strip().split(','))  # read the remaining lines: remove leading/trailing spaces, split at ",", then cast into ints
            data.append([x, y])  # save into a list
    return m, n, data


def generate_scenario_yaml_file(m, n, start_positions, goal_positions, obstacles, output_file_path):
    """
    Generates a YAML file representing the scenario based on input data (obtained by reading the agents and env files).

    Args:
        m (int): Environment horizontal dimension (m x n).
        n (int): Environment vertical dimension (m x n).
        start_positions (list of tuples): List of (x, y) pairs indicating start positions of agents.
        goal_positions (list of tuples): List of (x, y) pairs indicating goal positions of agents.
        obstacles (list of tuples): List of (x, y) pairs indicating obstacle positions.
        output_file_path (str): Path to save the generated YAML file.

    Returns:
        None
    """
    # Create a dictionary with the specified structure
    yaml_data = {
        "map": {
            "dimensions": [m, n],
            "obstacles": obstacles
        },
        "agents": []
    }

    # Add agent information
    for i, (start, goal) in enumerate(zip(start_positions, goal_positions)):
        agent = {
            "name": f"agent{i}",
            "start": list(start),
            "goal": list(goal)
        }
        yaml_data["agents"].append(agent)

    # Write the dictionary to a YAML file
    with open(output_file_path, "w") as yaml_file:
        yaml.safe_dump(yaml_data, yaml_file, default_flow_style=False)

    print(f"YAML data has been written to {output_file_path}")


def cleanup_result_yaml_file(output_yaml, cleaned_output_yaml, start_positions=None):
    """
    After planning, the MAPF algo will save the planning schedule to a yaml file.
    However, for some agents, planning might be infeasible. This makes the video plotting function crash.
    This function cleans up the planning schedule yaml file and saves a new cleaned file that works with the video plotter.
    """
    # Load the YAML file
    with open(output_yaml, 'r') as file:
        data = yaml.safe_load(file)

    # Remove empty "agent" entries
    total = len(data['schedule'])
    failed = []
    for i, (k, v) in enumerate(data['schedule'].items()):
        if v != []:  # plan for agent exists --> keep it.
            data['schedule'][k] = v
        else:  # planning for agent failed --> set schedule to stay in place
            failed.append(i)
            pos_when_fail = [-1, -1-i] if start_positions is None else start_positions[i]
            data['schedule'][k] = [{'x': pos_when_fail[0], 'y': pos_when_fail[1], 't': 0}]

    # Write the cleaned data to a yaml file
    with open(cleaned_output_yaml, 'w') as file:
        yaml.safe_dump(data, file)

    # Print info about the robots for which planning failed
    print("{} kings have failed out of {}".format(len(failed), total))
    if failed:
        print("The failed ones are: ", failed)


def read_clean_yaml_into_list(file_path):
    # Read the YAML file
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)

    # Extract the schedule
    schedule = data.get('schedule', {})

    # Initialize the schedule_list
    schedule_list = []

    agent_index = -1
    # Iterate over the agents in the schedule
    for agent, points in schedule.items():
        agent_index += 1
        schedule_list.append([])  # add a list to save the data of the current agent

        # Iterate over the points for the current agent
        for point in points:
            t = point['t']
            x = point['x']
            y = point['y']

            # Add a point to the list
            schedule_list[agent_index].append([x, y])

    # Pad out the sublists with the last (x, y) values
    max_length = max(len(sublist) for sublist in schedule_list)
    for sublist in schedule_list:
        while len(sublist) < max_length:
            sublist.append(sublist[-1])

    return schedule_list


def save_schedule_list_to_file(schedule_list, file_path):
    # Open the file in write mode
    with open(file_path, 'w') as file:
        # Iterate over each agent's list
        for agent_list in schedule_list:
            # Convert each (x, y) tuple to a string and join them with commas
            line = ','.join(f"{x} {y}" for x, y in agent_list)
            # Write the line to the file
            file.write(line + '\n')


def read_schedule_list_from_file(file_path):
    # Initialize the schedule_list
    schedule_list = []
    # Open the file in read mode
    with open(file_path, 'r') as file:
        # Read each line from the file
        for line in file:
            # Split the line by commas and convert each part to a tuple of integers
            agent_list = [list(map(float, point.split())) for point in line.strip().split(',')]
            # Append the agent list to schedule_list
            schedule_list.append(agent_list)
    # Return the schedule_list
    return schedule_list


def transform_coordinates_to_world(s_list, x0, y0, grid_len):
    """
    Converts the schedule list from a grid coordinate to world coordinates.
    args:
        s_list: schedule list using grid indices
        x0: index of grid cell that corresponds to the world x=0
        y0: index of grid cell that corresponds to the world y=0
        grid_len: length of the side of a grid cell (meters)
    """
    # Initialize the new list for world coordinates
    new_s_list = []

    # Iterate over each agent's list in s_list
    for agent_list in s_list:
        # Initialize the new agent list for world coordinates
        new_agent_list = []
        # Iterate over each (x, y) tuple in the agent's list
        for x, y in agent_list:
            # Apply the transformation to match the world coordinates
            new_x = (x - x0) * grid_len
            new_y = (y - y0) * grid_len
            # Append the new (x, y) tuple to the new agent list
            new_agent_list.append([new_x, new_y])
        # Append the new agent list to the new_s_list
        new_s_list.append(new_agent_list)

    # Return the new list with world coordinates
    return new_s_list


if __name__ == "__main__":
    rel_path = os.path.join("scenarios", "0")
    file_path_agents = os.path.join(rel_path, "agents.txt")
    file_path_env = os.path.join(rel_path, "env.txt")
    file_path_scenario_yaml = os.path.join(rel_path, "scenario.yaml")

    N, start_loc, goal_loc = read_agents_file(file_path_agents)
    print("Number of agents: ", N)
    print("From: ", start_loc)
    print("To: ", goal_loc)

    m, n, obstacles = read_env_file(file_path_env)
    print("Map size: ", m, " x ", n)
    print("Obstacle locations: ", obstacles)

    generate_scenario_yaml_file(m, n, start_loc, goal_loc, obstacles, file_path_scenario_yaml)

