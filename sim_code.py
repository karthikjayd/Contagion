import numpy as np

def initialize_agents(population, init_infected=1, box_size=50, immunized_fraction=0.0, seed=None):
    """
    Initialize agent positions, velocities, and health states.
    
    Args:
        population (int): Number of agents.
        init_infected (int): Number of initially infected agents.
        box_size (float): Size of the simulation box.
        immunized_fraction (float): Fraction of agents initially immunized (0.0 to 1.0).
        seed (int or None): Random seed for reproducibility.
        
    Returns:
        agents (np.ndarray): Array of shape (population, 3) with columns [x, y, state].
                             state: 0=healthy, 1=infected, 2=immunized
        velocities (np.ndarray): Array of shape (population, 2) with columns [vx, vy].
    """
    rng = np.random.default_rng(seed)
    agents = np.zeros((population, 4))  # x, y, state, infection_timer
    velocities = rng.uniform(-0.5, 0.5, size=(population, 2))
    agents[:, 0:2] = rng.uniform(0, box_size, size=(population, 2))
    # Assign immunized
    num_immunized = int(immunized_fraction * population)
    if num_immunized > 0:
        immunized_indices = rng.choice(population, num_immunized, replace=False)
        agents[immunized_indices, 2] = 2
    # Assign infected (to non-immunized)
    healthy_indices = np.where(agents[:, 2] == 0)[0]
    infected_indices = rng.choice(healthy_indices, min(init_infected, len(healthy_indices)), replace=False)
    agents[infected_indices, 2] = 1
    return agents, velocities

def update_positions(agents, velocities, box_size=50, timestep=1.0):
    """
    Update agent positions based on their velocities and apply reflective boundaries.
    
    Args:
        agents (np.ndarray): Array of agent positions and states.
        velocities (np.ndarray): Array of agent velocities.
        box_size (float): Size of the simulation box.
        timestep (float): Time step for movement.
    """
    agents[:, 0:2] += velocities * timestep
    # Reflective boundaries
    for dim in [0, 1]:
        over = agents[:, dim] > box_size
        under = agents[:, dim] < 0
        velocities[over | under, dim] *= -1
        agents[over, dim] = box_size
        agents[under, dim] = 0

def update_infections(agents, infection_radius, infection_probability, recovery_time=50, rng=None):
    """
    Update infection states based on proximity and infection probability.
    
    Args:
        agents (np.ndarray): Array of agent positions and states.
        infection_radius (float): Distance threshold for infection.
        infection_probability (float): Probability of infection upon contact.
        rng (np.random.Generator or None): Random number generator.
    """
    if rng is None:
        rng = np.random.default_rng()
    infected = np.where(agents[:, 2] == 1)[0]
    healthy = np.where(agents[:, 2] == 0)[0]
    # Infect new agents
    for i in infected:
        for j in healthy:
            dx = agents[i, 0] - agents[j, 0]
            dy = agents[i, 1] - agents[j, 1]
            dist = np.hypot(dx, dy)
            if dist < infection_radius:
                if rng.random() < infection_probability:
                    agents[j, 2] = 1  # Infect
                    agents[j, 3] = 0  # Reset infection timer
    # Update infection timers and recover agents
    for i in infected:
        agents[i, 3] += 1
        if agents[i, 3] >= recovery_time:
            agents[i, 2] = 2  # Immunized
            agents[i, 3] = 0  # Reset timer

def run_simulation(population, infection_radius, infection_probability, steps, 
                   box_size=50, init_infected=1, immunized_fraction=0.0, seed=None):
    """
    Run the contagion simulation for a given number of steps.
    
    Args:
        population (int): Number of agents.
        infection_radius (float): Distance threshold for infection.
        infection_probability (float): Probability of infection upon contact.
        steps (int): Number of simulation steps.
        box_size (float): Size of the simulation box.
        init_infected (int): Number of initially infected agents.
        immunized_fraction (float): Fraction of agents initially immunized.
        seed (int or None): Random seed for reproducibility.
        
    Returns:
        history (np.ndarray): Array of shape (steps, population, 3) with agent states over time.
    """
    rng = np.random.default_rng(seed)
    agents, velocities = initialize_agents(population, init_infected, box_size, immunized_fraction, seed)
    history = np.zeros((steps, population, agents.shape[1]))
    for t in range(steps):
        history[t] = agents
        update_positions(agents, velocities, box_size)
        update_infections(agents, infection_radius, infection_probability, recovery_time=50, rng=rng)
    return history