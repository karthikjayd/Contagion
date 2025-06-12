# filepath: c:\Users\Jayadevan\Documents\Me\Quarto_Contagion\Contagion\app.py
from shiny import App, ui, render
import matplotlib.pyplot as plt
import numpy as np
from sim_code import run_simulation

plt.rcParams['text.usetex'] = True
plt.rcParams['font.family'] = 'serif'

plt.style.use('ggplot')

state_colors = {0: '#7678ed', 1: '#bc4749', 2: '#76c893'}

app_ui = ui.page_fluid(
    ui.h2("Contagion Spread Simulation"),
    ui.layout_columns(
        # First column: sliders
        ui.panel_well(
            ui.input_slider("population", "Population", 10, 500, 50, step=10),
            ui.input_slider("infection_radius", "Infect Radius", 0.1, 5.0, 1.0, step=0.1),
            ui.input_slider("infection_probability", "Infect Prob", 0.0, 1.0, 0.2, step=0.01),
            ui.input_slider("steps", "Steps", 50, 2000, 200, step=10),
            ui.input_slider("immunized_fraction", "Immunized %", 0.0, 0.9, 0.0, step=0.05),
            ui.input_slider("seed", "Seed", 0, 10000, 0, step=1),
            width=4
        ),
        # Second column: plots
        ui.panel_well(
            ui.output_plot("sim_plot", width="600px", height="600px"),
            ui.output_plot("infected_plot", width="600px", height="300px"),
            width=8
        ),
    )
)

def server(input, output, session):
    @output
    @render.plot
    def sim_plot():
        history = run_simulation(
            population=input.population(),
            infection_radius=input.infection_radius(),
            infection_probability=input.infection_probability(),
            steps=input.steps(),
            immunized_fraction=input.immunized_fraction(),
            seed=input.seed()
        )
        agents = history[-1]
        fig, ax = plt.subplots(figsize=(6, 6))
        for state, color in state_colors.items():
            idx = agents[:, 2] == state
            ax.scatter(agents[idx, 0], agents[idx, 1], c=color, label={0:'Healthy',1:'Infected',2:'Immunized'}[state], s=30)
        ax.set_title(f"Agent States at Final Step")
        ax.set_xlim(0, 50)
        ax.set_ylim(0, 50)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.legend(facecolor='white')
        # ax.grid(True)
        return fig

    @output
    @render.plot
    def infected_plot():
        history = run_simulation(
            population=input.population(),
            infection_radius=input.infection_radius(),
            infection_probability=input.infection_probability(),
            steps=input.steps(),
            immunized_fraction=input.immunized_fraction(),
            seed=input.seed()
        )
        infected_counts = np.sum(history[:, :, 2] == 1, axis=1)
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(np.arange(len(infected_counts)), infected_counts, color='red')
        ax.set_xlabel("Time step")
        ax.set_ylabel("Number infected")
        ax.set_title("Infected Over Time")
        ax.grid(True)
        fig.tight_layout()
        return fig

app = App(app_ui, server)