from numpy import array
from numpy.polynomial.polynomial import polyval

class PolynomeValueCalc:
    def __init__(self):
        pass


    def calc_polynome(self, data_x, coef):
        return polyval(data_x, coef)


    def calc_polynomes(self, data_x, polynomes):
        calc_y = []
        
        first_polynome = polynomes[0]
        offset = first_polynome.start
        for polynome in polynomes:
            start = polynome.start - offset
            end = polynome.end - offset
            coef = polynome.coef

            interval_y = self.calc_polynome(
                data_x[start:end],
                coef
            )
            
            for y in interval_y:
                calc_y.append(y)

        return array(calc_y)