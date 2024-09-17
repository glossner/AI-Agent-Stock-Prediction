from src.Agents.base_agent import BaseAgent
from pydantic import BaseModel, Field, PrivateAttr
from cryptography.fernet import Fernet
from typing import Dict
from textwrap import dedent
import json
import crewai as crewai
import os

class PortfolioDataAgent(BaseAgent):
    def __init__(self, portfolio_data=None, encrypted_file_path="./portfolio_encrypted", **kwargs):
        super().__init__(
            role='Portfolio Data Agent',
            goal='Retrieve and handle portfolio data for scenario analysis',
            backstory='Handles portfolio data securely and maps it for simulation and risk assessment.',
            allow_delegation=False,
            **kwargs)
        self._fernet = Fernet(self.encryption_key)

        if portfolio_data:
            self.portfolio_data = portfolio_data
        else:   #default portfolio
            self.portfolio_data = {
                'assets': [
                    {'asset_class': 'Equity', 'position': 100000, 'weight': 0.5},
                    {'asset_class': 'Fixed Income', 'position': 50000, 'weight': 0.25},
                    {'asset_class': 'Commodities', 'position': 50000, 'weight': 0.25},
                ]
            }
        
        self.encrypted_file_path = encrypted_file_path


    # Class variables
    encryption_key: bytes = Field(default_factory=lambda: Fernet.generate_key())
    encrypted_portfolio_data: bytes = None
    decrypted_portfolio_data: dict = None
    mapped_portfolio_data: dict = None

    _fernet: Fernet = PrivateAttr()

    # TODO: Replace with portfolio manager library   
    def retrieve_portfolio_data(self):
        '''
            See if a portfolio exists on disk.
            If not, create a new default portfolio. Encrypt it and write it to disk.
            If yes, read the file, decrypt it, map it to valid fields.
            Create CrewAI task that send the portfolio to the agents.
        '''
        # if there isn't a portfolio yet, encrypt it and write it to disk (inialize)
        if not os.path.exists(self.encrypted_file_path):
            self._encrypt_and_save_portfolio_data()

        # Read and decrypt portfolio data
        self.read_and_decrypt_portfolio_data()
        self.map_portfolio_data()
        self.validate_mapped_data()

        return crewai.Task(
            description=dedent(f"""
                Provide portfolio data to the Crew
            """),
            agent=self,
            expected_output=json.dumps(self.portfolio_data)
        )

    
    def encrypt_portfolio_data(self):
        data_str = str(self.portfolio_data).encode('utf-8')
        self.encrypted_portfolio_data = self._fernet.encrypt(data_str)
        self.logger.info("Portfolio data has been securely retrieved and encrypted.")

    def read_and_decrypt_portfolio_data(self) -> Dict:
        try:
            with open(self.encrypted_file_path, 'rb') as f:
                encrypted_portfolio_data = f.read()
            # Decrypt the data
            decrypted_data_bytes = self._fernet.decrypt(encrypted_portfolio_data)
            # Decode bytes to string and parse JSON
            self.decrypted_portfolio_data = json.loads(decrypted_data_bytes.decode('utf-8'))
            self.logger.info("Portfolio data has been loaded and decrypted.")
        except Exception as e:
            self.logger.error(f"Failed to load and decrypt portfolio data: {e}")    
        return self.decrypted_portfolio_data

    def map_portfolio_data(self) -> Dict:
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

    def validate_mapped_data(self) -> bool:
        if not self.mapped_portfolio_data:
            self.logger.error("No mapped portfolio data to validate.")
            return False
        total_weight = sum(data['total_weight'] for data in self.mapped_portfolio_data.values())
        if abs(total_weight - 1.0) > 0.01:
            self.logger.error(f"Validation failed: Total weights sum to {total_weight}, which is not approximately 1.")
            return False
        self.logger.info("Mapped portfolio data has been validated successfully.")
        return True
    
    def _encrypt_and_save_portfolio_data(self):
        """
        Encrypts the initial portfolio data and saves it to disk.
        This method is intended for internal use to set up the encrypted data file.
        """
        try:
            self.logger.info("Portfolio data does not exist. Creating new default portfolio")
            # Convert data to JSON string and encode to bytes
            data_str = json.dumps(self.portfolio_data).encode('utf-8')
            # Encrypt the data
            encrypted_data = self._fernet.encrypt(data_str)
            # Save encrypted data to file
            with open(self.encrypted_file_path, 'wb') as f:
                f.write(encrypted_data)
            self.logger.info("Portfolio data has been encrypted and saved to disk.")
        except Exception as e:
            self.logger.error(f"Failed to encrypt and save portfolio data: {e}")    