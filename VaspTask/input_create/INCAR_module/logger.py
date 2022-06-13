import logging

logger=logging.getLogger('incar_run.py')
stream=logging.StreamHandler()
filehandler=logging.FileHandler('main.log')
formatter=logging.Formatter('%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s')
logger.setLevel(logging.DEBUG)
logger.addHandler(stream)
logger.addHandler(filehandler)
filehandler.setFormatter(formatter)
stream.setFormatter(formatter)