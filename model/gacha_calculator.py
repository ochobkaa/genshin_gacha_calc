from numpy import float32, array, convolve, pad, cumsum, sum
from collections import namedtuple
import csv

ROLL_CURRENCY = 160
CONSTS_COUNT = 7
REFINES_COUNT = 6

PITY_CHAR = 90
PITY_WEAPON = 80


def load_rolls_density(file_path):
    def density_from_csv(density_csv_file):
        csv_reader = csv.reader(density_csv_file)

        density_str = []

        for prob in csv_reader:
            density_str.append(prob)

        return density_str[1:]

    def parse_density_to_float(density_str):
        density = []

        for row in density_str:
            new_val = float32(row[1])
            density.append(new_val)

        return density

    def create_density_array(density):
        density_array = array(density)

        return density_array

    def norm_array(density):
        norm_array = density / sum(density)

        return norm_array

    density_csv_file = open(file_path)

    density_str = density_from_csv(density_csv_file)
    density = parse_density_to_float(density_str)
    density_array = create_density_array(density)
    norm_array = norm_array(density_array)

    return norm_array


def get_percentile(probability, percentile):
    percent = percentile / 100

    i = 1
    for prop in probability:
        if prop < percent:
            i += 1

        else:
            break

    return i


def get_percent_from_rolls(probability, rolls):
    if rolls < len(probability):
        return probability[rolls - 1] * 100

    else:
        return 100

def calculate_probability(density):
    probability = cumsum(density)

    return probability

# Вычисления для баннера персонажей

def calculate_fiftyfifty_density(density):
    extended_density = pad(density, [(0, PITY_CHAR - 1)])
    convolution = convolve(density, density)
    fiftyfifty_denstiy = (extended_density + convolution) / 2

    return fiftyfifty_denstiy


def calculate_char_const_density(density, const_number, fiftyfifty = True):
    fiftyfifty_denstiy = calculate_fiftyfifty_density(density)

    n_const_density = fiftyfifty_denstiy if fiftyfifty else density
    for i in range(const_number):
        n_const_density = convolve(n_const_density, fiftyfifty_denstiy)

    return n_const_density


def get_char_const_percentiles(density, fiftyfifty = True):
    for i in range(CONSTS_COUNT):
        n_const_density = calculate_char_const_density(density, i, fiftyfifty)
        n_const_probability = calculate_probability(n_const_density)

        fifty_percentile = get_percentile(n_const_probability, 50)
        ninety_percentile = get_percentile(n_const_probability, 90)
        ninetyfive_percentile = get_percentile(n_const_probability, 95)

        print("50 перцентиль для С{0}: {1}".format(i, fifty_percentile))
        print("90 перцентиль для С{0}: {1}".format(i, ninety_percentile))
        print("95 перцентиль для С{0}: {1}".format(i, ninetyfive_percentile))
        print()


def get_char_consts_percents_from_rolls(density, rolls, fiftyfifty=True):
    for i in range(CONSTS_COUNT):
        n_const_density = calculate_char_const_density(density, i, fiftyfifty)
        n_const_probability = calculate_probability(n_const_density)

        const_percent = get_percent_from_rolls(n_const_probability, rolls)

        print("Вероятность выбить С{0}: {1:.2f}%".format(i, const_percent))

# Вычисления дла баннера оружки

def calculate_weapon_two_points_density(density):
    points = 0
    
    density_first_extended = pad(density, (0, PITY_WEAPON - 1))
    density_first_point = convolve(density, density)
    density_first = (density_first_extended + 2 * density_first_point) / 3

    density_second_extended = pad(density_first, (0, PITY_WEAPON - 1))
    density_second_point = convolve(density_first, density)
    density_second = (density_second_extended + 2 * density_second_point) / 3

    return density_second


def calculate_weapon_refines(density, refine_number):
    two_points_density = calculate_weapon_two_points_density(density)

    n_refine_density = two_points_density
    for i in range(refine_number):
        n_refine_density = convolve(n_refine_density, density)

    return n_refine_density


def get_weapon_refines_percentiles(density):
    for i in range(REFINES_COUNT):
        n_refine_density = calculate_weapon_refines(density, i)
        n_refine_probability = calculate_probability(n_refine_density)

        fifty_percentile = get_percentile(n_refine_probability, 50)
        ninety_percentile = get_percentile(n_refine_probability, 90)
        ninetyfive_percentile = get_percentile(n_refine_probability, 95)

        print("50 перцентиль для R{0}: {1}".format(i, fifty_percentile))
        print("90 перцентиль для R{0}: {1}".format(i, ninety_percentile))
        print("95 перцентиль для R{0}: {1}".format(i, ninetyfive_percentile))
        print()


def get_weapon_refines_percents_from_rolls(density, rolls):
    for i in range(REFINES_COUNT):
        n_refine_density = calculate_weapon_refines(density, i)
        n_refine_probability = calculate_probability(n_refine_density)

        refine_percent = get_percent_from_rolls(n_refine_probability, rolls)

        print("Вероятность выбить R{0}: {1:.2f}%".format(i, refine_percent))

# Комбинированный расчет

def calculate_char_with_weapon_density(char_density, weapon_density, char_consts, weapon_refines, char_fiftyfifty=True):
    char_const_density = calculate_char_const_density(char_density, char_consts, char_fiftyfifty)
    weapon_refines_density = calculate_weapon_refines(weapon_density, weapon_refines)
    density = convolve(char_const_density, weapon_refines_density)

    return density


def get_char_with_weapon_percent_from_rolls(char_density, weapon_density, char_consts, weapon_refines, rolls, char_fiftyfifty=True):
    density = calculate_char_with_weapon_density(char_density, weapon_density, char_consts, weapon_refines, char_fiftyfifty)
    probability = calculate_probability(density)

    percent = get_percent_from_rolls(probability, rolls)

    print("Вероятность выбить C{const} персонажа с R{refine} сигной: {percent:.2f}%".format(
        const=char_consts,
        refine=weapon_refines,
        percent=percent
    ))

# Ввод-вывод

def int_input_with_check(prompt, condition=lambda x: True):
    while True:
        int_input_str = input(prompt)

        try:
            int_input = int(int_input_str)

            if (condition(int_input)):
                return int_input

            else:
                print("Некорректное значение")

        except ValueError:
            print("Введено не целое число")


def get_rolls():
    non_negative = lambda x: x >= 0

    rolled = int_input_with_check("Введи сколько открутил: ", non_negative)
    have_rolls = int_input_with_check("Введи сколько круток: ", non_negative)
    have_primogems = int_input_with_check("Введи сколько примогемов: ", non_negative)

    rolls = rolled + have_rolls + int(have_primogems / ROLL_CURRENCY)

    return rolls


def get_fiftyfifty_status():
    is_binary = lambda x: x == 0 or x == 1

    fiftyfifty_status_num = int_input_with_check("Стопроцентный (1 - есть, 0 - нет): ", is_binary)
    fiftyfifty_status = fiftyfifty_status_num == 0

    return fiftyfifty_status


def get_consts():
    correct_const = lambda x: x >= 0 and x < CONSTS_COUNT

    consts = int_input_with_check("Сколько надо конст: ", correct_const)

    return consts


def get_refines():
    correct_refines = lambda x: x >= 0 and x < REFINES_COUNT

    refines = int_input_with_check("Сколько надо пробуд сигны: ", correct_refines)

    return refines


def get_action_num(actions_list):
    def actions_is_exist(actions_list, action_number):
        return any(action.number == action_number for action in actions_list)

    prompt = "Выберите:\n"
    for action in actions_list:
        prompt += "{number}: {desc}\n".format(
            number=action.number,
            desc=action.desc
        )
    prompt += "> "

    action_num = int_input_with_check(prompt, lambda x: actions_is_exist(actions_list, x))

    return action_num


def run_action(actions_list, action_number, char_density, weapon_density):
    for action in actions_list:
        if action.number == action_number:
            action.action(char_density, weapon_density)
            break

# Алгоритмы действий на выбор

def action_char_const_percentiles(char_density, weapon_density):
    fiftyfifty_status = get_fiftyfifty_status()
    print()

    get_char_const_percentiles(char_density, fiftyfifty_status)


def action_char_percents_from_rolls(char_density, weapon_density):
    rolls = get_rolls()
    fiftyfifty_status = get_fiftyfifty_status()
    print()

    get_char_consts_percents_from_rolls(char_density, rolls, fiftyfifty_status)


def action_weapon_refine_percentiles(char_density, weapon_density):
    get_weapon_refines_percentiles(weapon_density)


def action_weapon_percents_from_rolls(char_density, weapon_density):
    rolls = get_rolls()
    print()

    get_weapon_refines_percents_from_rolls(weapon_density, rolls)


def action_char_and_weapon_percent_from_rolls(char_density, weapon_density):
    consts = get_consts()
    refines = get_refines()
    rolls = get_rolls()
    fiftyfifty_status = get_fiftyfifty_status()
    print()

    get_char_with_weapon_percent_from_rolls(char_density, weapon_density, consts, refines, rolls, fiftyfifty_status)


if __name__ == '__main__':
    Action = namedtuple("Action", ["number", "desc", "action"])
    actions_list = [
        Action(
            number=1, 
            desc="Вывести 50/90/95 перцентили для конст персонажей", 
            action=action_char_const_percentiles
        ),
        Action(
            number=2, 
            desc="Получить вероятность выбить с N круток разное количество конст персонажей",
            action=action_char_percents_from_rolls
        ),
        Action(
            number=3,
            desc="Вывести 50/90/95 перцентили для пробуд оружки", 
            action=action_weapon_refine_percentiles
        ),
        Action(
            number=4,
            desc="Получить вероятность выбить с N круток разное количество пробуд оружки",
            action=action_weapon_percents_from_rolls
        ),
        Action(
            number=5,
            desc="Получить вероятность выбить с N круток указанное количество конст и пробуд сигны одновременно",
            action=action_char_and_weapon_percent_from_rolls
        ),
    ]

    char_density = load_rolls_density("CharRollDensity.csv")
    weapon_density = load_rolls_density("WeaponRollDensity.csv")

    action_num = get_action_num(actions_list)
    run_action(actions_list, action_num, char_density, weapon_density)
