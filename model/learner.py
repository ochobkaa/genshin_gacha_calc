from numpy import sum, seterr
from collections import namedtuple

class Learner:
    _DoublePolynome = namedtuple(
        "DoublePolynome", 
        ["polynomes", "patition"]
    )

    _polynome_coef_calc = None
    _polynome_value_calc = None


    def __init__(self, polynome_value_calc, polynome_coef_calc):
        self._polynome_value_calc = polynome_value_calc
        self._polynome_coef_calc = polynome_coef_calc


    def _polynome_r_square(self, data_x, data_y, polynome):
        coef = polynome.coef
        calc_y = self._polynome_value_calc.calc_polynome(data_x, coef)

        delta = calc_y - data_y
        dis_res = sum(delta ** 2)
        dis = sum(data_y ** 2)
        r_square = 1 - dis_res / dis
        return r_square


    def _model_r_square(self, data_x, data_y, polynomes):
        calc_y = self._polynome_value_calc.calc_polynomes(data_x, polynomes)

        delta = calc_y - data_y
        dis_res = sum(delta ** 2)
        dis = sum(data_y ** 2)
        r_square = 1 - dis_res / dis
        return r_square
    

    def _get_r_square_delta(self, data_x, data_y, single_polynome, double_polynomes):
        r_square_single = self._polynome_r_square(data_x, data_y, single_polynome)
        r_square_double = self._model_r_square(data_x, data_y, double_polynomes.polynomes)

        r_square_delta = abs(r_square_single - r_square_double)
        return r_square_delta
    

    def _fit_single_polynome(self, data_x, data_y, pow, offset=0):
        polynome = self._polynome_coef_calc.get_polynome(data_x, data_y, pow, offset)
        return polynome
    

    def _fit_double_polynomes(self, data_x, data_y, pow, min_interval, offset=0):
        i = min_interval
        polynome1_with_max = None
        polynome2_with_max = None
        r_square_max = 0
        i_with_max = i
        while i < len(data_x - min_interval):
            polynome1 = self._fit_single_polynome(data_x[:i], data_y[:i], pow, offset)
            polynome2 = self._fit_single_polynome(data_x[i:], data_y[i:], pow, offset + i)
            
            r_square = self._model_r_square(data_x, data_y, (polynome1, polynome2))

            if (r_square > r_square_max):
                polynome1_with_max = polynome1
                polynome2_with_max = polynome2
                r_square_max = r_square
                i_with_max = i

            i += 1

        double_polynomes = self._DoublePolynome((polynome1_with_max, polynome2_with_max), i_with_max)
        return double_polynomes


    def fit_model(self, data_x, data_y, pow, delta, depth, min_interval=4, offset=0):
        polynomes = []

        single_polynome = self._fit_single_polynome(data_x, data_y, pow, offset)

        if len(data_x) <= min_interval:
            polynomes.append(single_polynome)
            return polynomes
        
        double_polynomes = self._fit_double_polynomes(data_x, data_y, pow, min_interval, offset)
        partition = double_polynomes.patition

        r_square_delta = self._get_r_square_delta(data_x, data_y, single_polynome, double_polynomes)

        if r_square_delta > delta:
            if (depth > 0):
                poly_to_add1 = self.fit_model(data_x[:partition], data_y[:partition], 
                                pow, delta, depth - 1, min_interval, offset)
                poly_to_add2 = self.fit_model(data_x[partition:], data_y[partition:], 
                                pow, delta, depth - 1, min_interval, offset + partition)
                
                polynomes = [*polynomes, *poly_to_add1, *poly_to_add2]
                
            else:
                polynomes = [*polynomes, *double_polynomes.polynomes]

        else:
            polynomes.append(single_polynome)

        return polynomes