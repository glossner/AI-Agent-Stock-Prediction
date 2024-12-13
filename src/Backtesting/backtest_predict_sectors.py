import os
import re
import numpy as np
from fredapi import Fred
from dotenv import load_dotenv
from sklearn.metrics import mean_absolute_error
from crewai import Crew, Task
from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents
from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks
import json

# Load environment variables (e.g., FRED API key)
load_dotenv()


class EconomicCrew:
    def __init__(self):
        self.fred_api_key = os.getenv('FRED_API_KEY')
        self.fred = Fred(api_key=self.fred_api_key)

    def run(self):
        # Fetch macroeconomic data
        macroeconomic_data = self.fetch_macroeconomic_data()

        # Fetch financial reports and policy changes
        financial_reports = self.fetch_financial_reports()
        policy_changes = self.fetch_policy_changes()

        # Combine all data
        combined_data = self.get_combined_data(macroeconomic_data, financial_reports, policy_changes)

        # Simulate predictions using CrewAI
        predictions = self.simulate_predictions(combined_data)
        return predictions

    def fetch_macroeconomic_data(self):
        print("Fetching macroeconomic data from FRED...")
        try:
            gdp = self.fred.get_series('GDP')[-1]
            inflation = self.fred.get_series('CPIAUCSL')[-1]
            unemployment = self.fred.get_series('UNRATE')[-1]

            return {
                "GDP": gdp,
                "Inflation": inflation,
                "UnemploymentRate": unemployment
            }
        except Exception as e:
            print(f"Error fetching macroeconomic data: {e}")
            return {}

    def fetch_financial_reports(self):
        print("Fetching financial reports from FRED...")
        try:
            corporate_profits = self.fred.get_series('CP')[-1]
            sp500_index = self.fred.get_series('SP500')[-1]
            return {
                "CorporateProfits": corporate_profits,
                "SP500Index": sp500_index
            }
        except Exception as e:
            print(f"Error fetching financial reports: {e}")
            return {}

    def fetch_policy_changes(self):
        print("Fetching policy changes data from FRED...")
        try:
            fed_funds_rate = self.fred.get_series('FEDFUNDS')[-1]
            government_debt = self.fred.get_series('GFDEBTN')[-1]
            return {
                "FederalFundsRate": fed_funds_rate,
                "GovernmentDebt": government_debt
            }
        except Exception as e:
            print(f"Error fetching policy changes: {e}")
            return {}

    def get_combined_data(self, macroeconomic_data, financial_reports, policy_changes):
        return {
            "MacroeconomicData": macroeconomic_data,
            "FinancialReports": financial_reports,
            "PolicyChanges": policy_changes
        }

    def simulate_predictions(self, combined_data):
        agents = StockAnalysisAgents()
        tasks = StockAnalysisTasks()

        # Create an economic forecasting agent
        economic_forecasting_agent = agents.economic_forecasting_agent()

        # Create the sector prediction task
        sector_prediction_task = tasks.predict_sector_performance(
            agent=economic_forecasting_agent,
            combined_data=combined_data
        )

        # Run CrewAI
        crew = Crew(
            agents=[economic_forecasting_agent],
            tasks=[sector_prediction_task],
            verbose=True
        )
        result = crew.kickoff()

        # Extract predictions from CrewOutput
        predictions = self.extract_predictions(result)
        return predictions

    def extract_predictions(self, crew_output):
        """
        Extracts sector predictions from the CrewOutput object.
        Parses the narrative text to assign numerical values to each sector.
        """
        try:
            # Inspect the structure of CrewOutput for debugging
            print("Inspecting CrewOutput structure...")
            print(crew_output)

            # Check if 'tasks_output' attribute exists and is non-empty
            if hasattr(crew_output, 'tasks_output') and len(crew_output.tasks_output) > 0:
                task_output = crew_output.tasks_output[0]

                # Attempt to access the 'raw' attribute
                if hasattr(task_output, 'raw'):
                    prediction_text = task_output.raw
                else:
                    print("TaskOutput does not have a 'raw' attribute.")
                    print("Available attributes:", dir(task_output))
                    return {}

                # Parse predictions from the text
                predictions = self.parse_narrative_predictions(prediction_text)
                return predictions
            else:
                print("No task output found in CrewOutput.")
                return {}
        except Exception as e:
            print(f"Error extracting predictions: {e}")
            return {}

    def parse_narrative_predictions(self, text):
        """
        Parses the narrative text to extract sector predictions.
        Assigns numerical values based on qualitative descriptions.
        """
        sector_predictions = {}
        sectors = ["Technology", "Finance", "Healthcare", "Energy", "Consumer Discretionary"]

        for sector in sectors:
            # Create a regex pattern to find lines like "- **Technology Sector:** Likely to perform well."
            pattern = rf"-\s*\*\*{sector} Sector\*\*:\s*(.+)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                prediction = match.group(1).strip().lower()
                # Assign numerical values based on keywords
                if "perform well" in prediction or "likely to grow" in prediction or "expected to benefit" in prediction:
                    sector_predictions[sector] = 0.05  # Positive prediction
                elif "stable" in prediction or "neutral" in prediction:
                    sector_predictions[sector] = 0.0   # Neutral prediction
                elif "face challenges" in prediction or "may face challenges" in prediction or "may be negatively impacted" in prediction:
                    sector_predictions[sector] = -0.05  # Negative prediction
                else:
                    sector_predictions[sector] = 0.0   # Default to neutral if unclear
            else:
                # If no specific prediction found, default to 0.0
                sector_predictions[sector] = 0.0

        print(f"Parsed Predictions: {sector_predictions}")
        return sector_predictions


class Backtester:
    def __init__(self):
        self.economic_crew = EconomicCrew()

    def fetch_sector_performance(self, sectors):
        """
        Fetch actual sector performance.
        In a real backtesting scenario, replace this with historical data retrieval.
        """
        print("Fetching actual sector performance...")
        # Simulate actual historical performance data
        # Replace this with actual data fetching logic as needed
        actual_performance = {sector: np.random.uniform(-0.05, 0.10) for sector in sectors}
        print(f"Actual performance: {actual_performance}")
        return actual_performance

    def backtest_crewai(self, sectors):
        """
        Backtests the CrewAI-based system.
        """
        print("\nRunning CrewAI backtest...")
        predictions = self.economic_crew.run()

        if not predictions:
            print("No predictions were generated by CrewAI.")
            return float('inf'), {}, {}  # Return default values without rating

        # Ensure all sectors have predictions, defaulting to 0.0 if missing
        sector_predictions = {sector: predictions.get(sector, 0.0) for sector in sectors}
        print(f"CrewAI Predictions: {sector_predictions}")

        # Fetch actual sector performance
        actual_performance = self.fetch_sector_performance(sectors)

        # Calculate Mean Absolute Error (MAE)
        mae = mean_absolute_error(
            [actual_performance[sector] for sector in sectors],
            [sector_predictions[sector] for sector in sectors],
        )
        print(f"CrewAI MAE: {mae}")

        return mae, sector_predictions, actual_performance

    def backtest_non_crewai(self, sectors):
        """
        Backtests a simple baseline system without CrewAI.
        This randomly predicts sector performance.
        """
        print("\nRunning non-CrewAI backtest...")
        predictions = {sector: np.random.uniform(-0.02, 0.05) for sector in sectors}
        print(f"Non-CrewAI Predictions: {predictions}")

        # Fetch actual sector performance
        actual_performance = self.fetch_sector_performance(sectors)

        # Calculate Mean Absolute Error (MAE)
        mae = mean_absolute_error(
            [actual_performance[sector] for sector in sectors],
            [predictions[sector] for sector in sectors],
        )
        print(f"Non-CrewAI MAE: {mae}")

        return mae, predictions, actual_performance

    def compare_results(self, crewai_results, non_crewai_results):
        """
        Compares the performance of CrewAI and non-CrewAI systems.
        """
        crewai_mae, crewai_predictions, crewai_actuals = crewai_results
        non_crewai_mae, non_crewai_predictions, non_crewai_actuals = non_crewai_results

        print("\nComparison Results:")
        print("-------------------")
        print(f"CrewAI MAE: {crewai_mae}")
        print(f"Non-CrewAI MAE: {non_crewai_mae}")

        if crewai_mae < non_crewai_mae:
            print("CrewAI system outperformed the non-CrewAI system.")
        else:
            print("Non-CrewAI system outperformed the CrewAI system.")

    def run_backtest(self):
        """
        Runs the backtest for both CrewAI and non-CrewAI systems.
        """
        sectors = ["Technology", "Finance", "Healthcare", "Energy", "Consumer Discretionary"]

        # Backtest CrewAI system
        crewai_results = self.backtest_crewai(sectors)

        # Backtest non-CrewAI system
        non_crewai_results = self.backtest_non_crewai(sectors)

        # Compare results
        self.compare_results(crewai_results, non_crewai_results)


if __name__ == "__main__":
    backtester = Backtester()
    backtester.run_backtest()
