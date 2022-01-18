import numpy as np
import pandas as pd

class River:
    def __init__(self, x1, y1, x2, y2):
        self.m = (y2-y1)/(x2-x1)
        self.theta = np.where(np.arctan(self.m)> 0, np.pi - np.arctan(self.m), -np.pi - np.arctan(self.m))
    
    def rot_matrix(self):
        t = self.theta
        return(np.array([np.cos(t), -np.sin(t)], [np.sin(t), np.cost(t)]))

    def operator(self,x,y):
        return None

class Model:
    def __init__(self, k, H, h0, Qo_x, river = None, x_ref = 500, y_ref = 500):
        self.k = k
        self.H = H
        self.h0 = h0
        self.aem_elements = []
        self.well_df = pd.DataFrame({'wellid' : [], 'Discharge' : [], 'X' : [], 'Y' : []})
        self.Qo_x = Qo_x

        if river is None:
            self.river_a = 1
            self.river_b = 0
            self.river_c = 0
        
        else:
            self.river_a = river.river_a
            self.river_b = river.river_b
            self.river_c = river.river_c
        if self.h0 < self.H:
            self.phi0 = 0.5 * self.k * self.h0**2
        else:
            self.phi0 = self.k * self.H * self.h0 - 0.5 * self.k * self.H**2

    def calc_phi(self, x, y):
        phi_well = 0
        for element in self.aem_elements:
            d = np.abs(self.river_a * element.x + self.river_b * element.y + self.river_c) / np.sqrt(self.river_a**2 + self.river_b**2)
            if (x == element.x):
                phi_q = phi_q = (element.Q/(4*np.pi)) * np.log(((x+element.rw - element.x)**2 + (y-element.y)**2)/((x+element.rw-(element.x-2*d))**2+(y-element.y)**2))
            elif (y == element.y):
                phi_q = phi_q = (element.Q/(4*np.pi)) * np.log(((x-element.x)**2 + (y+element.rw-element.y)**2)/((x-(element.x - 2*d))**2+(y+element.rw-element.y)**2))
            else:
                phi_q = (element.Q/(4*np.pi))*np.log(((x-element.x)**2 + (y-element.y)**2)/((x-(element.x - 2*d))**2+(y-element.y)**2))
             
            phi_well += phi_q
        phi_base = self.Qo_x*x
        return self.phi0 + phi_well + phi_base

    def calc_head(self, x, y):
        phi = self.calc_phi(x,y)
        phicrit = 0.5 * self.k * self.H ** 2
        if phi >= phicrit:
            h = (phi + 0.5*self.k*self.H**2)/(self.k*self.H)
        else:
            h = np.sqrt((2 / self.k) * (phi))
        return h

    def calc_psi(self, x, y):
        psi_well = 0
        for element in self.aem_elements:
            d = np.abs(self.river_a*element.x + self.river_b*element.y + self.river_c)/np.sqrt(self.river_a**2 + self.river_b**2)
            if (x == element.x) & (y == element.y):
                psi_q = (element.Q/(2*np.pi))*(np.arctan2((y-element.y), (x-element.x+element.rw))) - np.arctan2((y-element.y), (x-(element.x-2*d)))
            else:
                psi_q = (element.Q/(2*np.pi)) * (np.arctan2((y-element.y), (x-element.x)) - np.arctan2((y-element.y), (x-(element.x-2*d))))
            psi_well += psi_q
            psi_base = self.Qo_x*y
            psi = psi_well+psi_base

        return psi

class Well:
    def __init__(self, model, Q, rw, x, y):
        self.x = x
        self.y = y
        self.Q = Q
        self.rw = rw
        model.aem_elements.append(self)

#aem_model = Model(k = 10, H=20, h0 = 18)

#well = Well(aem_model, Q = 10, rw = 0.2, x = 50, y = 50)

#print(aem_model.calc_psi(120, 0))


