class Charger:
    def __init__(self, id, max_charging_time):
        """Initialize a Charger object
        
        Args:
            id: Unique identifier for the charger
            max_charging_time: Maximum time this charger can charge a vehicle
        """
        self.id = id
        self.max_charging_time = max_charging_time
