import os
import sys
from time import perf_counter
from time import sleep
import requests
import logging

from datetime import date, datetime

from theos_functions import readConfig
from halo import Halo

now = datetime.now()
today = "{}-{}-{}".format(now.year, now.month, now.day)
sf = os.path.dirname(os.path.realpath(__file__))
folder = os.path.join(sf, 'logging')
log_file = os.path.join(folder, "{}.log".format(today))

if os.environ['HOME'] == '/Users/theovandersluijs':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    urllib3_log = logging.getLogger("urllib3")
    urllib3_log.setLevel(logging.CRITICAL)
else:
    os.makedirs(folder, exist_ok=True)
    logging.basicConfig(filename=log_file, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.CRITICAL)


class DoImport():
    def __init__(self):
        cf = readConfig('config/config.yml')
        self.config = cf.config

        process_url = self.config['process_url']

        start_t = perf_counter()
        self.process_url(
            url=f"{process_url}trigger", kind='Trigger')
        stop_t = perf_counter()
        elapsed_t = round(stop_t - start_t)
        print(f"{elapsed_t} seconden trigger_URL tijd.")

        while True:
            start_t = perf_counter()
            process = self.process_url(
                url=f"{process_url}processing", timeout=200, kind='Processing')
            if not process:
                break

            stop_t = perf_counter()
            elapsed_t = round(stop_t - start_t)
            print(f"{elapsed_t} seconden processing_URL tijd.")

    def process_url(self, url: str = None, timeout: int = 140, kind: str = 'Processing'):
        try:
            spinner = Halo(
                text=f"{kind} data", spinner='dots')
            spinner.start()
            r = requests.get(url, timeout=timeout)
            spinner.stop()

            if r.status_code == 200:
                try:
                    data = r.json()  # blijkbaar geeft hij niet altijd een json terug
                except Exception as e:
                    print(e)
                    return True

                print(f"status: {data['status']}")
                print(f"message: {data['message']}")

                if data['status'] != 200:
                    spinner = Halo(
                        text='Sleeping 120 sec for next run', spinner='dots')
                    spinner.start()
                    for i in range(120, 0, -1):
                        sleep(1)
                        mss = f"Sleeping {i} sec for next run"
                        spinner.text = mss
                    spinner.stop

                return True

                # {"status":200,"message":"#1 Cron job triggered."}
                # {"status": 403, "message": "Import #1 already triggered. Request skipped."}

                # {"status":200,"message":"Records Processed 21. Records imported 20 of 3167."}

            else:
                raise Exception(
                    f"We've got a {r.status_code} on the requests!")
        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            return True
        except requests.exceptions.TooManyRedirects:
            e = "Too many redirections"
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) +
                            " | " + str(fname) + " | " + str(exc_tb.tb_lineno))
            return False
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(str(e) + " | " + str(exc_type) +
                            " | " + str(fname) + " | " + str(exc_tb.tb_lineno))
            return False
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.critical(str(e) + " | " + str(exc_type) +
                             " | " + str(fname) + " | " + str(exc_tb.tb_lineno))

            return False

    # def processing(self, url):
    #     print(url)


if __name__ == '__main__':
    di = DoImport()
