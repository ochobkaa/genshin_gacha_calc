from numpy import seterr
from numpy.polynomial.polynomial import polyfit
from polynome import Polynome

class PolynomeCoefCalc:
    def __init__(self):
        pass


    def get_polynome(self, data_x, data_y, pow, offset=0):
        seterr(under="ignore")

        coef = polyfit(data_x, data_y, pow)
        polynome = Polynome(
            start=offset,
            end=offset + len(data_x),
            coef=coef
        )
        return polynome
