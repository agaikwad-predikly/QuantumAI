import logging
logging.basicConfig(filename='ErrorLog.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

def Error(error):
        logger.error(error)