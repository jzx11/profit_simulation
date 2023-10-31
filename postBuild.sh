# Ensure nodejs is installed for JupyterLab extension builds
conda install -c conda-forge nodejs

# Install the JupyterLab extension
jupyter labextension install @plotly/dash-jupyterlab

# Build JupyterLab with the new extension
jupyter lab build
