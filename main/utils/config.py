config_data = {"trajectory_send": True, "verify": True, "login_simulation": False, "simulation_role": "SuperAdmin", "simulation_token": ""}

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
        
    @property
    def login_simulation(self) -> bool:
        return self._config_data["login_simulation"]
    
    @login_simulation.setter
    def login_simulation(self, value:bool) -> None:
        if isinstance(value, bool):
            self._config_data["login_simulation"] = value
        else:
            raise TypeError("Invalid type for login_simulation. Expected bool.")
        
    @property
    def simulation_role(self) -> str:
        return self._config_data["simulation_role"]
    
    @simulation_role.setter
    def simulation_role(self, value:str) -> None:
        if isinstance(value, str):
            self._config_data["simulation_role"] = value
        else:
            raise TypeError("Invalid type for simulation_role. Expected string.")
        
    @property
    def simulation_token(self) -> str:
        return self._config_data["simulation_token"]
    
    @simulation_token.setter
    def simulation_token(self, value:str) -> None:
        if isinstance(value, str):
            self._config_data["simulation_token"] = value
        else:
            raise TypeError("Invalid type for simulation_token. Expected string.")