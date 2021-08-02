from ssp import app
from ssp.config import Config
from ssp.logger import logger


logger.info(msg=f"Started {__name__}")

if __name__ == '__main__':
    if Config.DEV_ENV:
        app.run(debug=True)  # run on home pc
    else:
        app.run(host='0.0.0.0', debug=True) # run on k8s