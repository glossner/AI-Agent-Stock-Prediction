# AI-Agent-Stock-Prediction

This code is from Rivier University's Fall 2024 Professional Seminar class (COMP-699)

## Executing the Code

There are two programs that are not yet integrated. From the root directory run:

```sh
(stocks) jglossner@jglossner:~/GitRepos/AI-Agent-Stock-Prediction$ streamlit run src/UI/app.py
```
or
```sh
(stocks) jglossner@jglossner:~/GitRepos/AI-Agent-Stock-Prediction$ python -m src.UI.main
```

## Installation

Install [Anaconda Python](https://www.anaconda.com/download).

```sh
conda create -n stocks python=3.12 anaconda
conda activate stocks
```

Install yfinance.

```sh
conda install langchain
conda install -c conda-forge yfinance langchain
conda update --all
```

If you are running on Windows, [download Visual Studio](https://visualstudio.microsoft.com/downloads/). You need a c++ compiler to generate the wheels for crewai. Minimally, [you must have buildtools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) installed. If you've already installed Visual Studio, you do not need to separately install build tools.

Install [CrewAI](https://docs.crewai.com/getting-started/Installing-CrewAI/).


```sh
conda config --set pip_interop_enabled True
pip install openai crewai crewai-tools pandas_ta unstructured sec_api
```

## Install faiss
If you have an nVidia GPU
```sh
pip install faiss-gpu
```
Else
```sh
pip install faiss-cpu
```


## Set Environment Variables
```sh
export OPENAI_API_KEY=sk-     # This is supplied to you in the Canvas shell.
export SEC_API_API_KEY= your long list of numbers   # Sign up for a free key
export SERPER_API_KEY= your key # Free for 2500 queries
```
Note: for Windows use set instead of export

Sign up to get a [free SEC API Key](https://sec-api.io/)
Sign up to get a [free SERPER API Key](https://serper.dev/)
