from dataclasses import dataclass
import tomllib
import math

@dataclass
class MachineDimensions:
    x_initial_position: int = 0
    x_maximum_position: int = 1000
    y_initial_position: int = 0
    y_maximum_position: int = 1000
    y_feed_rate: int = 6000

@dataclass
class NozzleConfiguration:
    total_nozzles: int = 0
    nozzles_per_manifold: int = 0
    number_of_passes: int = 0

@dataclass
class BedParameters:
    x_size_mm: int = 100
    y_size_mm: int = 100
    resolution_mm: int = 5
    deposition_rate: int = 6000

@dataclass
class Config:
    machine_dimensions: MachineDimensions
    nozzle_configuration: NozzleConfiguration
    bed_parameters: BedParameters

    @classmethod
    def from_dict(cls, data: dict) -> 'Config':
        # Merge default values with provided values
        machine_dims = MachineDimensions(**{
            **{f: getattr(MachineDimensions(), f) for f in MachineDimensions.__annotations__},
            **data.get('machine_dimensions', {})
        })
        
        nozzle_config = NozzleConfiguration(**{
            **{f: getattr(NozzleConfiguration(), f) for f in NozzleConfiguration.__annotations__},
            **data.get('nozzle_configuration', {})
        })
        
        bed_params = BedParameters(**{
            **{f: getattr(BedParameters(), f) for f in BedParameters.__annotations__},
            **data.get('bed_parameters', {})
        })
        
        return cls(
            machine_dimensions=machine_dims,
            nozzle_configuration=nozzle_config,
            bed_parameters=bed_params
        )

    @classmethod
    def from_file(cls, file: str) -> 'Config':
        with open('machine.toml', 'rb') as f:
            config_dict = tomllib.load(f)
            return cls.from_dict(config_dict)
        
    def pattern2machine_coord(self, coord):
        if isinstance(coord, tuple):
            x_dim = math.floor(coord[0] * self.bed_parameters.resolution_mm)
            y_dim = math.floor(coord[1] * self.bed_parameters.resolution_mm)
            return (x_dim, y_dim)
        else:
            return math.floor(coord * self.bed_parameters.resolution_mm)
    
    def machine2pattern_coord(self, coord):
        if isinstance(coord, tuple):
            x_dim = math.floor(coord[0] / self.bed_parameters.resolution_mm)
            y_dim = math.floor(coord[1] / self.bed_parameters.resolution_mm)
            return (x_dim, y_dim)
        else:
            return math.floor(coord / self.bed_parameters.resolution_mm)
        
    def get_bed_array_size(self) -> tuple[int, int]:
        return(self.machine2pattern_coord(self.bed_parameters.x_size_mm), self.bed_parameters.y_size_mm)

default_config_empty = {
    'machine_dimensions': {
        'x_initial_position': None,
        'x_maximum_position': None,
        'y_initial_position': None,
        'y_maximum_position': None,
        'y_feed_rate': None
    },
    'nozzle_configuration': {
        'total_nozzles': None,
        'nozzles_per_manifold': None,
        'number_of_passes': None
    },
    'bed_parameters': {
        'x_size_mm': None,
        'y_size_mm': None,
        'resolution_mm': None,
        'deposition_rate': None
    }
}