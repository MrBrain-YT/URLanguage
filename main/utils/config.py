config_data = {"trajectory_send": True, "verify": True}

class Config:
    _config_data = config_data
    
    @property
    def trajectory_send(self) -> bool:
        return self._config_data["trajectory_send"]
    
    @trajectory_send.setter
    def trajectory_send(self, value:bool) -> None:
        if isinstance(value, bool):
            self._config_data["trajectory_send"] = value
        else:
            raise TypeError("Invalid type for trajectory_send. Expected bool.")
        
    @property
    def verify(self) -> bool:
        return self._config_data["verify"]
    
    @verify.setter
    def verify(self, value:bool) -> None:
        if isinstance(value, bool):
            self._config_data["verify"] = value
        else:
            raise TypeError("Invalid type for verify. Expected bool.")