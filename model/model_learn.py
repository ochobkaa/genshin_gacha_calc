from model import Model
from config_loader import ConfigLoader
from density_loader import DensityLoader
from model_calculator import ModelCalculator
from polynome_coef_calc import PolynomeCoefCalc
from polynome_value_calc import PolynomeValueCalc
from learner import Learner
from model_writer import ModelWriter
from logger_creator import LoggerCreator

import sys
from collections import namedtuple
import logging
from logging.handlers import QueueHandler, QueueListener
from threading import Thread
from multiprocessing import Queue, Manager, Process
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import matplotlib.pyplot as plot
from numpy import array, seterr, float32

class ModelLearn:
    _ModelConf = namedtuple(
        "ModelConf",
        ["consts", "refines", "pow", "delta", "depth", "min_interval"]
    )

    _config_loader = None
    _density_loader = None
    _model_calculator = None
    _learner = None
    _model_writer = None
    _logger_creator = None

    _models_conf = None
    _learned_models = None
    
    _char_density = None
    _weapon_density = None

    def __init__(self, config_loader, density_loader, model_calculator, learner, model_writer, logger_creator):
        self._config_loader = config_loader
        self._density_loader = density_loader
        self._model_calculator = model_calculator
        self._learner = learner
        self._model_writer = model_writer
        self._logger_creator = logger_creator


    def load_config(self):
        '''Загрузка данных из файла конфигурации модели'''
        logger = self._logger_creator.create("GIGM Cofig loader")

        logger.info("Loading config...")
        try:
            self._config_loader.load()
            logger.info("Config loaded")

        except EnvironmentError:
            logger.error("Cannot open models_config.yml file!")

        char_density_path = self._config_loader.char_density_path
        weapon_density_path = self._config_loader.weapon_density_path
        char_pity = self._config_loader.char_pity
        weapon_pity = self._config_loader.weapon_pity
        model_output_path = self._config_loader.model_output_path
        model_output_filename = self._config_loader.model_output_filename
        self._models_conf = self._config_loader.models_conf

        self._density_loader.select_files(char_density_path, weapon_density_path)
        self._model_calculator.set_pity(char_pity, weapon_pity)
        self._model_writer.set_destination(model_output_path, model_output_filename)


    def load_density(self):
        '''Загрузка данных о баннере персонажа и оружейном баннере'''
        logger = self._logger_creator.create("GIGM Density loader")

        logger.info("Loading density...")
        try:
            self._density_loader.load()
            logger.info("Character and weapon banner density data loaded")
        
        except EnvironmentError:
            logger.error(
                "Error with loading density data. Ensure that correct file paths have " +
                "specified in models_config.yml file and all files exist and accessible by these paths."
            )

        self._char_density = self._density_loader.char_density
        self._weapon_density = self._density_loader.weapon_density


    @staticmethod
    def _get_const_refine_str(consts, refines, fifty_fifty):
        fifty_fifty_s = "(with fifty-fifty)" if fifty_fifty else "(without fifty-fifty)"

        if consts == -1 and refines > 0:
            s = "R{0}".format(refines)

        elif consts > -1 and refines == 0:
            s = "C{0} {1}".format(consts, fifty_fifty_s)

        else:
            s = "C{0} R{1} {2}".format(consts, refines, fifty_fifty_s)
        
        return s

    
    def _calc_density(self, consts, refines, fifty_fifty=True):
        calc = self._model_calculator
        char_density = self._char_density
        weapon_density = self._weapon_density

        if consts == -1 and refines > 0:
            density = calc.weapon_refines_density(weapon_density, refines)

        elif consts > -1 and refines == 0:
            density = calc.char_consts_density(char_density, consts, fifty_fifty)

        else:
            density = calc.char_with_weapon_density(
                char_density, weapon_density,
                consts, refines, fifty_fifty
            )

        return density


    def _get_model_conf(self, model_conf_dict):
        parsed_delta = float32(model_conf_dict["delta"])

        model_conf = self._ModelConf(
            consts=model_conf_dict["consts"],
            refines=model_conf_dict["refines"],
            pow=model_conf_dict["pow"],
            delta=parsed_delta,
            depth=model_conf_dict["depth"],
            min_interval=model_conf_dict["min_interval"]
        )
        return model_conf


    def _learn_model(self, model_conf, logger, fifty_fifty=True):
        calc = self._model_calculator
        learner = self._learner
        consts = model_conf.consts
        refines = model_conf.refines
        pow = model_conf.pow
        delta = model_conf.delta
        depth = model_conf.depth
        min_interval = model_conf.min_interval

        consts_refine_str = self._get_const_refine_str(consts, refines, fifty_fifty)

        logger.debug("Learning {0} model...".format(consts_refine_str))

        density = self._calc_density(consts, refines, fifty_fifty)

        data_x = array(range(1, len(density) + 1))

        probability = calc.probability(density)

        polynomes = learner.fit_model(
            data_x, probability, pow, delta, depth, min_interval
        )

        logger.debug("{0} model learned".format(consts_refine_str))

        learned_model = Model(
            fifty_fifty=fifty_fifty, 
            consts=model_conf.consts,
            refines=model_conf.refines,
            polynomes=polynomes
        )
        return learned_model
    

    def _learn_list(self, model_conf_list, logger, fifty_fifty=True):
        learned_models = []
        for model_conf_dict in model_conf_list:
            model_conf = self._get_model_conf(model_conf_dict)
            learned_model = self._learn_model(model_conf, logger, fifty_fifty)
            learned_models.append(learned_model)
        
        return learned_models
        

    def _learn_fifty_fifty(self):
        logger = self._logger_creator.create("GIGM Fifty fifty learn")

        logger.info("Learning fifty fifty models...")
        fifty_fifty_models = self._learn_list(self._models_conf["fifty_fifty"], logger, fifty_fifty=True)
        logger.info("Fifty fifty models learned")
        
        return fifty_fifty_models


    def _learn_no_fifty_fifty(self):
        logger = self._logger_creator.create("GIGM No fifty fifty learn")

        logger.info("Learning no fifty fifty models...")
        no_fifty_fifty_models = self._learn_list(self._models_conf["no_fifty_fifty"], logger, fifty_fifty=False)
        logger.info("No fifty fifty models learned")

        return no_fifty_fifty_models
    

    def _learn_weapon_only(self):
        logger = self._logger_creator.create("GIGM Weapon only learn")

        logger.info("Learning weapon only models...")
        weapon_only_models = self._learn_list(self._models_conf["weapon_only"], logger)
        logger.info("Weapon only models learned")

        return weapon_only_models


    def learn(self, workers=2):
        tasks = [
            self._learn_fifty_fifty,
            self._learn_no_fifty_fifty,
            self._learn_weapon_only
        ]

        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(t) for t in tasks]
            results = [future.result() for future in futures]

        fifty_fifty, no_fifty_fifty, weapon_only = results
        
        learned_models = [*fifty_fifty, *no_fifty_fifty, *weapon_only]
        self._learned_models = learned_models


    def write_models(self):
        logger = self._logger_creator.create("GIGM Save")

        model_writer = self._model_writer
        models = self._learned_models

        logger.info("Saving models...")

        try:
            for model in models:
                model_writer.write(model)

            logger.info("All models sucessfuly saved!")

        except EnvironmentError:
            logger.error(
                "Error was occured during models saving! " +
                "Ensure that path specified in models_config.yml are accessible"
            )


def get_messages(queue):
    logger = logging.getLogger("GIGM")
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(name)s: [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    while True:
        try:
            message = queue.get_nowait()
            logger.handle(message)

        except Exception:
            pass


def learn(queue, lock):
    config_loader = ConfigLoader("models_config.yml")
    
    density_loader = DensityLoader()
    model_calculator = ModelCalculator()
    model_writer = ModelWriter()

    polynome_value_calc = PolynomeValueCalc()
    polynome_coef_calc = PolynomeCoefCalc()
    learner = Learner(polynome_value_calc, polynome_coef_calc)
    logger_creator = LoggerCreator(queue, lock)

    model_learn = ModelLearn(
        config_loader, density_loader,
        model_calculator, learner, model_writer, logger_creator
    )

    listener = QueueListener(queue)

    listener.start()
    model_learn.load_config()
    model_learn.load_density()
    model_learn.learn(workers=3)
    model_learn.write_models()
    listener.stop()

    
if __name__ == "__main__":
    with Manager() as manager:
        queue = manager.Queue(-1)
        lock = manager.Lock()

        messages_thread = Thread(target=get_messages, args=(queue,))

        messages_thread.start()
        learn(queue, lock)
        messages_thread.join()