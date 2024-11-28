from passlib.hash import bcrypt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a password hash
password = "password"
hashed = bcrypt.hash(password)
logger.info(f"Password: {password}")
logger.info(f"Generated hash: {hashed}")

# Verify it works
verification = bcrypt.verify(password, hashed)
logger.info(f"Verification test: {verification}") 