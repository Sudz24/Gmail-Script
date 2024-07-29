import logging
logging.basicConfig(
   
format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s",
    handlers=[logging.FileHandler("app.log", encoding='utf-8'), logging.StreamHandler()],
    level=logging.INFO
)