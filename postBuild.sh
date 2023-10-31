#!/bin/bash

# Install Dash
pip install dash==1.20.0

jupyter labextension install @plotly/dash-jupyterlab
jupyter lab build


# Allow Binder to run the Dash app on port 8050
echo 'c.ServerProxy.servers = {"8050": {"command": ["python", "simulation_script.py"]}}' >> ~/.jupyter/jupyter_notebook_config.py
