from numpy import float32, array
import csv


class DensityLoader:
    _char_density_path = None
    _weapon_density_path = None
    _char_density = None
    _weapon_density = None

    def __init__(self):
        pass


    def select_files(self, char_density_path, weapon_density_path):
        '''Для отложенного выбора файлов данных о количестве круток в баннере персонажа и оружейном баннере'''
        self._char_density_path = char_density_path
        self._weapon_density_path = weapon_density_path


    def _load_csv(self, csv_file_path):
        '''Загружает из csv файла количество 5* на разных крутках для баннера, и возвращает плотность вероятности'''

        def counts_from_csv(density_csv_file):
            csv_reader = csv.reader(density_csv_file)

            counts_str = []

            for prob in csv_reader:
                counts_str.append(prob)

            return counts_str[1:]

        def parse_counts_to_float(counts_str):
            counts = []

            for row in counts_str:
                new_val = float32(row[1])
                counts.append(new_val)

            return counts

        def create_counts_array(counts):
            counts_array = array(counts)

            return counts_array

        def density(counts):
            density = counts / sum(counts)

            return density

        with open(csv_file_path) as csv_file:
            counts_csv_file = csv_file
            counts_str = counts_from_csv(counts_csv_file)

        counts = parse_counts_to_float(counts_str)
        counts_array = create_counts_array(counts)
        density = density(counts_array)

        return density
    

    def load(self):
        '''Загружает плотности для баннера персонажа и оружейного баннера из выбранных файлов'''
        self._char_density = self._load_csv(self._char_density_path)
        self._weapon_density = self._load_csv(self._weapon_density_path)
    

    @property
    def char_density(self):
        return self._char_density
    

    @property
    def weapon_density(self):
        return self._weapon_density