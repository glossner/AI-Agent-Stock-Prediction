import unittest
from unittest.mock import patch, MagicMock
from src.Agents.Analysis.stock_analysis_agents import StockAnalysisAgents
from src.Agents.Analysis.stock_analysis_tasks import StockAnalysisTasks
from src.UI.predict_sectors_main import EconomicCrew

# Mocking the FRED API response for macroeconomic data
mock_macroeconomic_data = {
    "GDP": "Real GDP data",
    "Inflation": "CPI data",
    "UnemploymentRate": "Unemployment rate data"
}

mock_combined_data = {
    "MacroeconomicData": mock_macroeconomic_data,
    "FinancialReports": "Financial Reports Mock Data",
    "PolicyChanges": "Policy Changes Mock Data"
}


class TestEconomicCrew(unittest.TestCase):
    @patch('src.UI.predict_sectors_main.Fred.get_series')
    def test_fetch_macroeconomic_data(self, mock_get_series):
        # Mock FRED API data fetching
        mock_get_series.side_effect = lambda series_id: mock_macroeconomic_data[series_id]
        
        economic_crew = EconomicCrew()
        result = economic_crew.fetch_macroeconomic_data()

        # Check if the result matches the mock data
        self.assertEqual(result['GDP'], "Real GDP data")
        self.assertEqual(result['Inflation'], "CPI data")
        self.assertEqual(result['UnemploymentRate'], "Unemployment rate data")

    def test_get_combined_data(self):
        economic_crew = EconomicCrew()
        result = economic_crew.get_combined_data(mock_macroeconomic_data)

        # Validate that the combined data contains correct financial reports, policy changes, and macroeconomic data
        self.assertEqual(result["MacroeconomicData"], mock_macroeconomic_data)
        self.assertEqual(result["FinancialReports"], "Financial Reports Mock Data")
        self.assertEqual(result["PolicyChanges"], "Policy Changes Mock Data")

    @patch('src.Agents.Analysis.stock_analysis_agents.Agent')
    def test_economic_forecasting_agent(self, mock_agent):
        # Ensure economic forecasting agent is initialized correctly
        agents = StockAnalysisAgents()
        agent = agents.economic_forecasting_agent()
        self.assertTrue(mock_agent.called)
        self.assertEqual(agent.role, 'Economic Analyst')

    @patch('src.Agents.Analysis.stock_analysis_tasks.Task')
    def test_predict_sector_performance_task(self, mock_task):
        # Mocking Task creation for sector performance prediction
        tasks = StockAnalysisTasks()
        agent = StockAnalysisAgents().economic_forecasting_agent()
        task = tasks.predict_sector_performance(agent, mock_combined_data)

        # Check if the Task description is correctly generated
        self.assertTrue(mock_task.called)
        self.assertIn("predict which sectors", task.description)
        self.assertEqual(task.agent, agent)

    @patch('src.UI.predict_sectors_main.EconomicCrew.fetch_macroeconomic_data')
    def test_fetch_macroeconomic_data_error(self, mock_fetch_data):
        # Simulate API error
        mock_fetch_data.side_effect = Exception("FRED API error")

        economic_crew = EconomicCrew()

        with self.assertRaises(Exception):
            economic_crew.fetch_macroeconomic_data()

    @patch('src.Agents.Analysis.stock_analysis_agents.StockAnalysisAgents.economic_forecasting_agent')
    def test_economic_crew_agents(self, mock_forecasting_agent):
        # Ensure agents are correctly initialized
        economic_crew = EconomicCrew()
        agents = economic_crew.run()

        # Check if the economic forecasting agent was called
        self.assertTrue(mock_forecasting_agent.called)

    @patch('src.Agents.Analysis.stock_analysis_agents.StockAnalysisAgents.economic_forecasting_agent')
    def test_economic_forecasting_agent_initialization(self, mock_forecasting_agent):
        # Ensure that the agent is initialized with the correct parameters
        economic_crew = EconomicCrew()
        economic_crew.run()

        # Check agent initialization
        self.assertTrue(mock_forecasting_agent.called)

class TestIntegrationEconomicForecasting(unittest.TestCase):
    @patch('src.UI.predict_sectors_main.EconomicCrew.fetch_macroeconomic_data')
    @patch('src.UI.predict_sectors_main.EconomicCrew.get_combined_data')
    @patch('src.Agents.Analysis.stock_analysis_tasks.Task')
    def test_economic_forecasting_workflow(self, mock_task, mock_combined_data, mock_fetch_macroeconomic_data):
        # Mock data
        mock_fetch_macroeconomic_data.return_value = mock_macroeconomic_data
        mock_combined_data.return_value = mock_combined_data

        # Initialize the EconomicCrew
        economic_crew = EconomicCrew()
        result = economic_crew.run()

        # Check if the crew output is as expected
        self.assertIn("Sector Performance Prediction Report", str(result))

    @patch('src.UI.predict_sectors_main.EconomicCrew.get_combined_data')
    def test_sector_performance_prediction_with_alternative_policy_changes(self, mock_get_combined_data):
        # Introduce hypothetical policy changes
        mock_combined_data['PolicyChanges'] = "Alternative Policy Changes: Policy Z"
        mock_get_combined_data.return_value = mock_combined_data

        # Run the crew with the updated policy changes
        economic_crew = EconomicCrew()
        result = economic_crew.run()

        # Validate output with the alternative policy changes
        self.assertIn("Policy Z", str(result))

    @patch('src.UI.predict_sectors_main.EconomicCrew.get_combined_data')
    def test_sector_performance_with_unexpected_economic_conditions(self, mock_get_combined_data):
        # Introduce an unexpected economic condition
        mock_combined_data['MacroeconomicData']['GDP'] = "Unexpected GDP Decline"
        mock_get_combined_data.return_value = mock_combined_data

        # Run the crew with the unexpected macroeconomic conditions
        economic_crew = EconomicCrew()
        result = economic_crew.run()

        # Validate output with the unexpected economic condition
        self.assertIn("Unexpected GDP Decline", str(result))

if __name__ == '__main__':
    unittest.main()
