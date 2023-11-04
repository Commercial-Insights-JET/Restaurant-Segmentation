# Restaurant Segmentation - Exploratory Code

## Overview

Repo for model code used in Just Eat Restaurant Segmentation client project (Jul-Oct 2023)


## Environment and dependencies

This project was originally created in conda, but we provide both pip and conda install options.


### For conda installation

Declare any dependencies in `src/environment.yml`.
- Create project env and install packages:
    `conda env create --name <env_name> -f src/environment.yml`

- Export project env:
    `conda env export --no-builds | grep -v "prefix" > src/environment.yml`

**tip**: ensure conda base env is deactivated to avoid env conflict.

### For pip installation
Declare any dependencies in `src/requirements.txt`
- Create a virtual environment using tool of your choice
- install packages:
    `pip install -r src/requirements.txt`
- export pip requirements:
    `pip list --format=freeze > src/requirements.txt`

### Manual environment
If the above environment installations do not work, the environment can be recreated manually using these commands in terminal:
```
conda install python=3.9
conda install pandas=1.5
conda install matplotlib=3.7
conda install seaborn=0.12
conda install -c conda-forge kedro=0.18
conda install -c conda-forge kedro-mlflow=0.11
conda install -c conda-forge kedro-viz=6.6
conda install -c conda-forge tpot=0.12
conda install -c conda-forge ruff=0.1.0
```

## Data
Data is not stored in this repo.
- .gitignore ignores the data/ folder
- see section on data below for the necessary data folder structure

# Quick Start Guide

## Packages overview

This project uses
|Package|Purpose|Notes|
|:----|:--|:--|
|python|All code is written in python|python=3.9|
|pandas, numpy|Data manipulation and processing|Pandas is mostly used with some execption for NaN handling|
|seaborn, matplotlib| Visualising data and results|
|scikit-learn|Used to create all ML models||
|tpot|auto-ML tool used to automate best model hyperparameter selection through automatic iteration | |
|kedro|Used to create modular code structure in ML project using Pipelines, Nodes and Tags|project generated using `kedro 0.18.12` see [Kedro documentation](https://docs.kedro.org)|
|MLFlow|Used to track ML experiments every time a Kedro element is executed| see [MLFlow documentation]()|
|black|Used to format code according to PEP8 standards|Run `python black .` before commit or include in git pre-commit hook|


## Layout

The project is made of 7 pipelines. Each pipeline is responsible for a section of the ML model.

There are 3 data preprocessing pipelines and 4 ML pipelines
|Pipeline|Purpose|Notes|
|:----|:--|:--|
|preprocessing|pipeline for general consolidation, processing and treatment of data and anomalies before model specific treatments||
|scorecard|pipeline for creating the Aspirational Index used as targets in ML model training||
|model_features|pipeline for manipulating and selecting the ML model input features||

|Pipeline|Purpose|Notes|
|:----|:--|:--|
|model_aspidx|pipeline for training ML models to predict Aspirational Index|
|model_kmeans|pipeline for kmeans clustering training and prediction||
|predict|pipeline to make Aspirational Index predictions and clustering on new data||
|model_tpot|pipeline responsible for triggering auto-ml action|auto-ml iteration takes a long time (>12 hours), it is sensible to use this only when there has been significant change to underlying data|

Each pipeline contains nodes, where each node is a function and the pipeline orchestrates the execution of the nodes. 

You can view the layout of all pipelines and nodes using
```
kedro viz
```

## Running pipelines

Pipelines and nodes can be executed independently or in a chain. Additionally in this project we make extensive use of `tags` to organise our pipelines.

There are two main tags to execute in this project, to re-train new models and to make predictions on new data respectively.
```
kedro run --tags train_models
kedro run --tags predict
```

The two tags `train_models` and `predict` alone cover all of the project's operational functions. Other tags have been used to group subsets of functions and give context.
- 'pipeline_<sequence_number>_<pipeline_name>' helps identify pipelines when using the kedro viz ui (e.g. 'pipeline_2_scorecard')
- 'model_<model_name>' helps identify nodes contributing to the model, regardless of pipeline, when using the kedro viz ui (e.g. 'model_xgb_17')
- 'retired' tags nodes which are no longer part of the main operation but are retained for legacy or future use purposes.

It is unlikely you will need other tags, but it is possible to combine kedro cli commands, node, pipeline, and other tags to customise a run. See kedro docs for more [kedro run commands](https://docs.kedro.org/en/stable/development/commands_reference.html#modifying-a-kedro-run).

Example run commands:

- `kedro run --tags train_models --from-nodes create_train_features` will run the train_models process without re-loading data or re-scoring the aspirational index.
- `kedro run --tags train_models --to-nodes create_train_features` will run the train_models process up till the aspirational index is created.
- `kedro run --tags train_models --from-nodes qualify_data --to-nodes create_train_features` will run only the section where the aspirational index is re-scored without re-loading data.

To see what will execute when a tag or pipeline is run, see the diagram using ```kedro viz```

 
**tip**: as per kedro docs you can run the entire kedro project with ```kedro run``` but we DO NOT recommend this as this will include running the ```model_tpot``` pipeline which is computationally expensive and often unnecessary. We recommend sticking to the use of tags `kedro run --tags train_models` and `kedro run --tags predict`


## Inputs and Outputs

### Data Catalog
All inputs and outputs (regardless of pipeline), are all declared in one central file `conf/base/catalog.yml` refered to as the "catalogue".
The alias and stored location of a pipeline input and/or output is determined by the parameters in the catalogue. If an input/output is not defined in the catalogue, the object is accessed in-memory.

We recommend using the `kedro viz` ui again to explore how artifacts in the data catalog are related to nodes and each other.

### Data Folder
Data is stored in the `./data/` folder. There are 9 folders
|Folder|Contains|
|:----|:--|
|01_train_input|Input data for training the models. This is usually 1 csv for restaurants on the JET platform|
|02_train_intermediate|Various data files created in the process of training models are stored here by the pipeline|
|03_train_output|End-pipeline outputs used for consumption. These are cross-validated predictions used in evaluating trained models|
|04_predict_input|Input data used for prediction. This is usually 1 csv for prospecting restaurants not yet on the JET platform|
|05_predict_intermediate|Various data files created in the process of making predictions are stored here by the pipeline|
|06_predict_output|End-pipeline outputs used for consumption. These are predictions of data input in 04_predict_input|
|07_scorecard|Output: The created Aspirational Index used as the target in predictive models|
|08_models|Output: Trained model files in pickle format|
|09_reporting|Output: All visualisations or metrics used to evaluate or explain performance of trained models|

### Run History

Previous kedro runs and versions of the model can be accessed from the kedro mlflow ui, which launches an interactive UI in browser.
```
kedro mlflow ui
```
The history displayed in the mlflow ui can also be accessed from the `./mlruns/` folder, organised by run id. This includes previously saved artifacts, previous model pickle files, and run metrics.


## To modify the pipeline
Each pipeline has a corresponding node.py, pipeline.py and parameters .yml file.
- **nodes** are in `src/jet/pipelines/<pipeline_name>/nodes.py`
- **pipelines** are in `src/jet/pipelines/<pipeline_name>/pipeline.py`
- pipeline **parameters** are in `conf/base/parameters/<pipeline_name>.yml`

All pipelines share the same central catalog
- the **catalogue** is in `conf/base/catalog.yml`

If new pipelines are to be created, or old ones deleted use kedro commands to set up the structure instead of manually creating them
- create a new pipeline with `kedro pipeline create <pipeline_name>` and modify from there
- delete a pipeline with `kedro pipeline delete <pipeline_name>`

See [official kedro docs](https://docs.kedro.org/en/stable/tutorial/create_a_pipeline.html#introduction) for more information.


**tip**: when executing a `kedro run` command after modification and a "pipeline not found" error returns, this is usually a misinformed error from legacy. Instead, the issue usually is in the syntax of the pipeline.py file itself (missing commas etc.), rather that the pipeline doesn't exist, especially if it has run successfully before.