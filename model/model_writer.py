import json

class ModelWriter:
    _model_output_path = ""
    _model_output_filename = ""

    def __init__(self):
        pass

    
    def set_destination(self, model_output_path, model_output_filename):
        '''Устанавливает путь и имя для записи файла модели'''
        self._model_output_path = model_output_path
        self._model_output_filename = model_output_filename


    def write(self, model):
        '''Записывает модель с указанными параметрами в yaml файл'''
        polynomes_serialize_dict = list(map(
            lambda polynome: {
                "start": polynome.start,
                "end": polynome.end,
                "coef": [*polynome.coef]
            },
            model.polynomes
        ))

        serialize_dict = {
            "fifty_fifty": model.fifty_fifty,
            "consts": model.consts,
            "refines": model.refines,
            "polynomes": polynomes_serialize_dict
        }

        fifty_fifty_prompt = "50" if model.fifty_fifty else "100"

        filename = "{name}_{fifty_fifty}_c{consts}_r{refines}.json".format(
            name=self._model_output_filename,
            fifty_fifty=fifty_fifty_prompt,
            consts=model.consts,
            refines=model.refines
        )
        file_path = self._model_output_path + "/" + filename

        file_path.replace("/", "\\")

        with open(file_path, "w") as model_file:
            json.dump(serialize_dict, model_file, indent=4, separators=(", ", ": "))