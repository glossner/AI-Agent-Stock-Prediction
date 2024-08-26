######################################
# This code comes from: https://github.com/crewAIInc/crewAI-examples/blob/main/stock_analysis/tools/calculator_tools.py 
# And is licensed under MIT
######################################

from langchain.tools import tool


class CalculatorTools():

  @tool("Make a calculation")
  def calculate(operation):
    """Useful to perform any mathematical calculations, 
    like sum, minus, multiplication, division, etc.
    The input to this tool should be a mathematical 
    expression, a couple examples are `200*7` or `5000/2*10`
    """
    return eval(operation)