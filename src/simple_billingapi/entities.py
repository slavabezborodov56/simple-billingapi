from dataclasses import dataclass


@dataclass
class CreateUserDTO:
    phone: str
    """Телефон"""
