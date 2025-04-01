import dataclasses


@dataclasses.dataclass
class Address:
  street: str = ""
  number: str = "0"
  floor: int = 0
  city: str = ""

  def __str__(self) -> str:
    return (
      f"Street: {self.street} | Number: {self.number} | Floor: {self.floor} | City: {self.city}"
    )


@dataclasses.dataclass
class PropertyProfile:
  property_type: str = "apartment"
  size: float = 0.0

  def __str__(self) -> str:
    return f"Type: {self.property_type} | Size: {self.size} sqm"


@dataclasses.dataclass
class HousingOffer:
  monthly_price: float = 0.0
  total_price: float = 0.0
  address: Address = dataclasses.field(default_factory=Address)
  property_profile: PropertyProfile = dataclasses.field(default_factory=PropertyProfile)
  responded: bool = False

  def __str__(self) -> str:
    return f"Monthly: {self.monthly_price} | Total: {self.total_price} | Address: [{self.address}] | Property: [{self.property_profile}] | Responded: {self.responded}"
