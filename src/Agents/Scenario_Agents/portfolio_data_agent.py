from src.Agents.base_agent import BaseAgent
from pydantic import BaseModel, Field, PrivateAttr
from cryptography.fernet import Fernet, InvalidToken
from typing import Dict, List, Optional
from textwrap import dedent
import json
import crewai as crewai
import os
import base64
import logging


# Optional: Define Pydantic models for better data validation
class Holding(BaseModel):
    ticker: str
    position: float
    weight: float


class Asset(BaseModel):
    asset_class: str
    holdings: List[Holding] = Field(default_factory=list)


class PortfolioDataAgent(BaseAgent):
    # Class variables
    encrypted_portfolio_data: bytes = None
    decrypted_portfolio_data: Dict = None
    mapped_portfolio_data: Dict = None

    _fernet: Fernet = PrivateAttr()

    def __init__(
        self,
        portfolio_data: Optional[List[Dict]] = None,
        encrypted_file_path: str = "./portfolio_encrypted",
        key_file_path: str = "./portfolio_key",
        **kwargs
    ):
        super().__init__(
            role='Portfolio Data Agent',
            goal='Retrieve and handle portfolio data for scenario analysis',
            backstory='Handles portfolio data securely and maps it for simulation and risk assessment.',
            allow_delegation=False,
            **kwargs
        )

        self.encrypted_file_path = encrypted_file_path
        self.key_file_path = key_file_path  # Assign the key_file_path to self

        # Initialize logger if not already present
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(__name__)
            if not self.logger.hasHandlers():
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
                self.logger.setLevel(logging.WARNING)

        # Retrieve encryption key from environment variable or file
        env_key = os.getenv("PORTFOLIO_ENCRYPTION_KEY")
        if env_key:
            try:
                # Ensure the key is bytes
                self.encryption_key = env_key.encode('utf-8')
                # Validate the key by attempting to create a Fernet instance
                Fernet(self.encryption_key)
                self.logger.info("Encryption key loaded from environment variable.")
            except (ValueError, InvalidToken, base64.binascii.Error) as e:
                self.logger.error(f"Invalid encryption key in environment variable: {e}")
                raise ValueError("Invalid encryption key format in environment variable.")
        elif os.path.exists(self.key_file_path):
            self.encryption_key = self._load_encryption_key()
            self.logger.info("Encryption key loaded from file.")
        else:
            self.encryption_key = Fernet.generate_key()
            self.logger.warning("Encryption key not found in environment or file. Generated a new key.")
            self._save_encryption_key(self.encryption_key)

        self._fernet = Fernet(self.encryption_key)

        # Initialize portfolio data
        if portfolio_data:
            # Validate using Pydantic models if provided
            try:
                assets = [Asset(**asset) for asset in portfolio_data]
                self.portfolio_data = [asset.dict() for asset in assets]
            except Exception as e:
                self.logger.error(f"Invalid portfolio data provided: {e}")
                raise ValueError("Invalid portfolio data structure.")
        else:  # default portfolio with specific tickers
            self.portfolio_data = [
                {
                    'asset_class': 'Equity',
                    'holdings': [
                        {'ticker': 'SPY', 'position': 60000, 'weight': 0.3},
                        {'ticker': 'DIA', 'position': 40000, 'weight': 0.2},
                    ]
                },
                {
                    'asset_class': 'Fixed Income',
                    'holdings': [
                        {'ticker': 'AGG', 'position': 50000, 'weight': 0.25}
                    ]
                },
                {
                    'asset_class': 'Commodities',
                    'holdings': [
                        {'ticker': 'GLD', 'position': 50000, 'weight': 0.25}
                    ]
                },
            ]

    def _save_encryption_key(self, key: bytes):
        try:
            with open(self.key_file_path, 'wb') as key_file:
                key_file.write(key)  # Write the key directly without additional encoding
            self.logger.info("Encryption key has been saved successfully.")
        except Exception as e:
            self.logger.error(f"Failed to save encryption key: {e}")
            raise e

    def _load_encryption_key(self) -> bytes:
        try:
            with open(self.key_file_path, 'rb') as key_file:
                key = key_file.read()
            # Validate the key by decoding and checking length
            decoded_key = base64.urlsafe_b64decode(key)
            if len(decoded_key) != 32:
                raise ValueError("Invalid key length after decoding.")
            self.logger.info("Encryption key has been loaded and validated successfully.")
            return key  # Return the base64-encoded key bytes
        except Exception as e:
            self.logger.error(f"Failed to load encryption key: {e}")
            raise e

    #### CrewAI.Task()
    def retrieve_portfolio_data(self):
        '''
            See if a portfolio exists on disk.
            If not, create a new default portfolio. Encrypt it and write it to disk.
            If yes, read the file, decrypt it, map it to valid fields.
            Create CrewAI task that send the portfolio to the agents.
        '''
        # if there isn't a portfolio yet, encrypt it and write it to disk (initialize)
        if not os.path.exists(self.encrypted_file_path):
            self._encrypt_and_save_portfolio_data()

        # Read and decrypt portfolio data
        self.read_and_decrypt_portfolio_data()
        self.map_portfolio_data()
        is_valid = self.validate_mapped_data()
        if is_valid:
            # Log the mapped portfolio data in a pretty format
            pretty_data = json.dumps(self.mapped_portfolio_data, indent=4)
            self.logger.info("Mapped Portfolio Data:\n%s", pretty_data)

        return crewai.Task(
            description=dedent("""
                Provide portfolio data to the Crew
            """),
            agent=self,
            expected_output=json.dumps(self.portfolio_data)
        )

    def encrypt_portfolio_data(self):
        data_str = json.dumps(self.portfolio_data).encode('utf-8')  # Use JSON for consistent encoding
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
        except InvalidToken:
            self.logger.error("Decryption failed: Invalid encryption key or corrupted data.")
            raise ValueError("Decryption failed: Invalid encryption key or corrupted data.")
        except Exception as e:
            self.logger.error(f"Failed to load and decrypt portfolio data: {e}")    
            raise e
        return self.decrypted_portfolio_data

    def map_portfolio_data(self) -> Dict:
        if self.decrypted_portfolio_data is None:
            self.logger.error("No decrypted portfolio data to map.")
            return None
        mapped_data = {}
        for asset in self.decrypted_portfolio_data:
            asset_class = asset['asset_class']
            for holding in asset['holdings']:
                ticker = holding['ticker']
                position = holding['position']
                weight = holding['weight']
                if asset_class not in mapped_data:
                    mapped_data[asset_class] = {
                        'total_position': 0,
                        'total_weight': 0,
                        'tickers': {}
                    }
                mapped_data[asset_class]['total_position'] += position
                mapped_data[asset_class]['total_weight'] += weight
                mapped_data[asset_class]['tickers'][ticker] = {
                    'position': position,
                    'weight': weight
                }
        self.mapped_portfolio_data = mapped_data
        self.logger.info("Portfolio data has been mapped to asset categories with specific tickers.")
        return mapped_data

    def validate_mapped_data(self) -> bool:
        if not self.mapped_portfolio_data:
            self.logger.error("No mapped portfolio data to validate.")
            return False
        # Corrected: Use 'total_weight' instead of 'weight'
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
            self.logger.info("Portfolio data does not exist. Creating new default portfolio.")
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
            raise e
