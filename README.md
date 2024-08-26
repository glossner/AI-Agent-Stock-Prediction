# AI-Agent-Stock-Prediction

This code is from Rivier University's Fall 2024 Professional Seminar class (COMP-699)

## Executing the Code

```sh
(stocks) jglossner@jglossner:~/GitRepos/AI-Agent-Stock-Prediction$ streamlit run src/UI/app.py
```

## Installation

Install [Anaconda Python](https://www.anaconda.com/download).

```sh
conda create -n stocks python=3.12 anaconda
conda activate stocks
```

Install yfinance.

```sh
conda install -c conda-forge yfinance
conda update --all
```

Install [CrewAI](https://docs.crewai.com/getting-started/Installing-CrewAI/).


```sh
conda config --set pip_interop_enabled True
pip install openai crewai crewai-tools pandas_ta unstructured sec_api
```
