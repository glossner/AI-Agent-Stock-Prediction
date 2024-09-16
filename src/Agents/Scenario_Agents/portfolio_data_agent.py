from src.Agents.base_agent import BaseAgent
from pydantic import BaseModel, Field, PrivateAttr
from cryptography.fernet import Fernet

class PortfolioDataAgent(BaseAgent):
    encryption_key: bytes = Field(default_factory=lambda: Fernet.generate_key())
    encrypted_portfolio_data: bytes = None
    decrypted_portfolio_data: dict = None
    mapped_portfolio_data: dict = None

    _fernet: Fernet = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(
            role='Portfolio Data Agent',
            goal='Securely retrieve and handle portfolio data for scenario analysis',
            backstory='Handles portfolio data securely and maps it for simulation and risk assessment.',
            **kwargs)
        self._fernet = Fernet(self.encryption_key)

    def setup(self):
        # Retrieve and process portfolio data during setup
        self.retrieve_portfolio_data()
        self.decrypt_portfolio_data()
        self.map_portfolio_data()
        self.validate_mapped_data()
        # Provide mapped data to other agents via CrewAI messaging
        self.send('ScenarioSimulationAgent', self.mapped_portfolio_data)

    def retrieve_portfolio_data(self):
        portfolio_data = {
            'assets': [
                {'asset_class': 'Equity', 'position': 100000, 'weight': 0.5},
                {'asset_class': 'Fixed Income', 'position': 50000, 'weight': 0.25},
                {'asset_class': 'Commodities', 'position': 50000, 'weight': 0.25},
            ]
        }
        data_str = str(portfolio_data).encode('utf-8')
        self.encrypted_portfolio_data = self._fernet.encrypt(data_str)
        self.logger.info("Portfolio data has been securely retrieved and encrypted.")

    def decrypt_portfolio_data(self):
        if self.encrypted_portfolio_data is None:
            self.logger.error("No encrypted portfolio data found.")
            return
        data_str = self._fernet.decrypt(self.encrypted_portfolio_data)
        # Using eval is unsafe; use ast.literal_eval or json.loads in production
        self.decrypted_portfolio_data = eval(data_str.decode('utf-8'))
        self.logger.info("Portfolio data has been decrypted securely.")

    def map_portfolio_data(self):
        if self.decrypted_portfolio_data is None:
            self.logger.error("No decrypted portfolio data to map.")
            return None
        mapped_data = {}
        for asset in self.decrypted_portfolio_data['assets']:
            asset_class = asset['asset_class']
            if asset_class not in mapped_data:
                mapped_data[asset_class] = {'total_position': 0, 'total_weight': 0}
            mapped_data[asset_class]['total_position'] += asset['position']
            mapped_data[asset_class]['total_weight'] += asset['weight']
        self.mapped_portfolio_data = mapped_data
        self.logger.info("Portfolio data has been mapped to asset categories.")
        return mapped_data

    def validate_mapped_data(self):
        if not self.mapped_portfolio_data:
            self.logger.error("No mapped portfolio data to validate.")
            return False
        total_weight = sum(data['total_weight'] for data in self.mapped_portfolio_data.values())
        if abs(total_weight - 1.0) > 0.01:
            self.logger.error(f"Validation failed: Total weights sum to {total_weight}, which is not approximately 1.")
            return False
        self.logger.info("Mapped portfolio data has been validated successfully.")
        return True