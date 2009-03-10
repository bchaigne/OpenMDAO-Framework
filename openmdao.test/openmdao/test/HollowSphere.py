from openmdao.main.component import Component, RUN_OK
from openmdao.main.variable import Float, INPUT, OUTPUT
from math import pi

class HollowSphere(Component):
    def __init__(self, name):
        Component.__init__(self, name)
        self.radius = 1.0
        self.thickness = 0.05
        self.volume = None
        self.inner_volume = None
        self.solid_volume = None
        self.surface_area = None
        
        # set up interface to the framework
        Float('radius',INPUT,parent=self,units='cm')
        Float('thickness',INPUT,parent=self,units='cm')
        
        Float('inner_volume',OUTPUT,parent=self,units='cm^3')
        Float('volume',OUTPUT,parent=self,units='cm^3')
        Float('solid_volume',OUTPUT,parent=self,units='cm^3')
        Float('surface_area',OUTPUT,parent=self,units='cm^2')

        
    def execute(self):
        self.surface_area = 4.0*pi*self.radius*self.radius
        self.inner_volume = 4.0/3.0*pi*self.radius^3
        self.volume = 4.0/3.0*pi*(self.radius+self.thickness)^3
        self.solid_volume = self.volume-self.inner_volume
        return RUN_OK

