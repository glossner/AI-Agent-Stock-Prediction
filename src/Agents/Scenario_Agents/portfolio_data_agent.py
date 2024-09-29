from src.Agents.base_agent import BaseAgent
from pydantic import BaseModel, Field, PrivateAttr
from cryptography.fernet import Fernet
from typing import Dict
from textwrap import dedent
import json
import crewai as crewai
import os

class PortfolioDataAgent(BaseAgent):
    def __init__(self, portfolio_data=None, encrypted_file_path="./portfolio_encrypted", encryption_key_path="./key", **kwargs):
        super().__init__(
            role='Portfolio Data Agent',
            goal='Retrieve and handle portfolio data for scenario analysis',
            backstory='Handles portfolio data securely and maps it for simulation and risk assessment.',
            allow_delegation=False,
            **kwargs)

        if portfolio_data:
            self.portfolio_data = portfolio_data
        else:
            self.portfolio_data = None            
        
        # Load or generate the encryption key       
        self.encrypted_file_path = encrypted_file_path
        self.encryption_key_path = encryption_key_path

        self.encryption_key = self.load_or_generate_encryption_key()
        self._fernet = Fernet(self.encryption_key)

        self.encrypted_portfolio_data: bytes = None
        self.decrypted_portfolio_data: dict = None
        self.mapped_portfolio_data: dict = None


    # Class variables
    #encryption_key: bytes = Field(default_factory=lambda: Fernet.generate_key())
    

    _fernet: Fernet = PrivateAttr()

    def retrieve_portfolio_data(self):
        '''
            See if a portfolio exists on disk.
            If not, create a new default portfolio. Encrypt it and write it to disk.
            If yes, read the file, decrypt it, map it to valid fields.
            Create CrewAI task that send the portfolio to the agents.
        '''
        # if there isn't a portfolio yet, encrypt it and write it to disk (inialize)
        if not os.path.exists(self.encrypted_file_path):
            self.encrypt_and_save_portfolio_data()

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

        # Map by ticker
        for asset in self.decrypted_portfolio_data['assets']:
            ticker = asset['ticker']
            if ticker not in mapped_data:
                mapped_data[ticker] = {
                    'asset_class': asset['asset_class'],
                    'position': 0,
                    'weight': 0
                }
            mapped_data[ticker]['position'] += asset['position']
            mapped_data[ticker]['weight'] += asset['weight']

        self.mapped_portfolio_data = mapped_data
        self.logger.info("Portfolio data has been mapped by tickers.")
        return mapped_data

    def validate_mapped_data(self) -> bool:
        if not self.mapped_portfolio_data:
            self.logger.error("No mapped portfolio data to validate.")
            return False
        total_weight = sum(data['weight'] for data in self.mapped_portfolio_data.values())
        if abs(total_weight - 1.0) > 0.01:
            self.logger.error(f"Validation failed: Total weights sum to {total_weight}, which is not approximately 1.")
            return False
        self.logger.info("Mapped portfolio data has been validated successfully.")
        return True


    def load_or_generate_encryption_key(self):
        if os.path.exists(self.encryption_key_path):
            with open(self.encryption_key_path, 'rb') as f:
                encryption_key = f.read()
            self.logger.info("Encryption key loaded from disk.")
        else:
            encryption_key = Fernet.generate_key()
            with open(self.encryption_key_path, 'wb') as f:
                f.write(encryption_key)
            self.logger.info("Encryption key generated and saved to disk.")
        return encryption_key

    def encrypt_portfolio_data(self):
        data_str = json.dumps(self.portfolio_data).encode('utf-8')
        self.encrypted_portfolio_data = self._fernet.encrypt(data_str)
        self.logger.info("Portfolio data has been securely retrieved and encrypted.")


    def encrypt_and_save_portfolio_data(self):
        """
        Encrypts the initial portfolio data and saves it to disk.
        This method is intended for internal use to set up the encrypted data file.
        """
        try:
            # Provide a default portfolio if none provided
            if not self.portfolio_data:
                self.logger.info("Portfolio data does not exist. Creating new default portfolio")
                self.portfolio_data = {
                    'assets': [
                    {'ticker': 'AAPL', 'asset_class': 'Equity', 'position': 50000, 'weight': 0.25},
                    {'ticker': 'MSFT', 'asset_class': 'Equity', 'position': 50000, 'weight': 0.25},
                    {'ticker': 'IEF', 'asset_class': 'Fixed Income', 'position': 50000, 'weight': 0.25},
                    {'ticker': 'GLD', 'asset_class': 'Commodities', 'position': 50000, 'weight': 0.25},
                    ]
                }
            
            # Encrypt and write the portfolio to disk
            self.encrypt_portfolio_data()
            # Save encrypted data to file
            with open(self.encrypted_file_path, 'wb') as f:
                f.write(self.encrypted_portfolio_data)
            self.logger.info("Portfolio data has been encrypted and saved to disk.")
        except Exception as e:
            self.logger.error(f"Failed to encrypt and save portfolio data: {e}")    