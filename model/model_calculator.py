from numpy import convolve, pad, cumsum

class ModelCalculator:
    char_pity = 0
    weapon_pity = 0

    def __init__(self):
        pass

    def set_pity(self, char_pity, weapon_pity):
        self.char_pity = char_pity
        self.weapon_pity = weapon_pity

    def _fiftyfifty_density(self, char_density):
        '''Возвращает плотность вероятности выбить персонажа с учетом 50 на 50'''
        extended_density = pad(char_density, [(0, self.char_pity)])
        convolution = convolve(char_density, char_density)
        convolution = pad(convolution, [(1, 0)])
        fiftyfifty_denstiy = (extended_density + convolution) / 2

        return fiftyfifty_denstiy

    def _weapon_two_points_density(self, density):
        '''Возвращает плотность вероятности выбить оружие с учетом системы очков'''        
        density_first_extended = pad(density, [(0, self.weapon_pity)])
        density_first_point = convolve(density, density)
        density_first_point = pad(density_first_point, [(1, 0)])
        density_first = (density_first_extended + density_first_point) / 2

        density_second_extended = pad(density_first, [(0, self.weapon_pity)])
        density_second_point = convolve(density_first, density)
        density_second_point = pad(density_second_point, [(1, 0)])
        density_second = (density_second_extended + density_second_point) / 2

        return density_second

    def char_consts_density(self, density, const_number, fiftyfifty = True):
        '''
        Возвращает плотность вероятности выбить const_number конст на персонажа.\n
        Параметр fiftyfifty задает начальное условие. Значение True - 50 на 50, значение False - стопроцентный гарант.
        '''
        fiftyfifty_denstiy = self._fiftyfifty_density(density)

        n_const_density = fiftyfifty_denstiy if fiftyfifty else density
        for i in range(const_number):
            n_const_density = convolve(n_const_density, fiftyfifty_denstiy)
            n_const_density = pad(n_const_density, (1, 0))

        return n_const_density

    def weapon_refines_density(self, density, refine_number):
        '''Возвращает плотность вероятности выбить пробуду для оружия refine_number'''
        two_points_density = self._weapon_two_points_density(density)

        n_refine_density = two_points_density
        for i in range(refine_number):
            n_refine_density = convolve(n_refine_density, density)
            n_refine_density = pad(n_refine_density, (1, 0))

        return n_refine_density

    def char_with_weapon_density(self, char_density, weapon_density, char_consts, weapon_refines, char_fiftyfifty=True):
        '''
        Возвращает плотность вероятности выбить char_consts персонажа с weapon_refines пробуд.\n
        Параметр char_fiftyfifty задает начальное условие банера персонажа. Значение True - 50 на 50, значение False - стопроцентный гарант.
        '''
        char_const_density = self.char_consts_density(char_density, char_consts, char_fiftyfifty)
        weapon_refines_density = self.weapon_refines_density(weapon_density, weapon_refines)
        density = convolve(char_const_density, weapon_refines_density)

        return density

    def probability(self, density):
        '''Возвращает функцию вероятности для функции плотности density'''
        probability = cumsum(density)

        return probability

    def percentile(self, probability, percentile):
        '''Возвращает количество круток, которое является перцентилем для процента percentile'''
        percent = percentile / 100

        i = 1
        for prop in probability:
            if prop < percent:
                i += 1

            else:
                break

        return i

    def roll_percent(self, probability, rolls):
        '''Возващает вероятность для указанного числа круток rolls'''
        if rolls < len(probability):
            return probability[rolls - 1] * 100

        else:
            return 100

