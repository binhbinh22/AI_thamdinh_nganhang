import logging

# Cấu hình logger gốc
logging.basicConfig(
    format="[%(asctime)s - %(levelname)s - %(funcName)20s()->%(lineno)s]- %(message)s",
    level=logging.INFO,
    filename="logs/api_log.log",  # <-- log API
    filemode="a",
)

# Logger API
api_logger = logging.getLogger("api_logger")
api_logger.setLevel(logging.INFO)

# Logger Ollama
ollama_logger = logging.getLogger("ollama_logger")
ollama_logger.setLevel(logging.INFO)

# Console log
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(levelname)s - %(funcName)20s()->%(lineno)s]- %(message)s"
    )
)
api_logger.addHandler(console_handler)
ollama_logger.addHandler(console_handler)


# import logging

# logging.basicConfig(
#     format="[%(asctime)s - %(levelname)s - %(funcName)20s()->%(lineno)s]- %(message)s",
#     level=logging.INFO,
#     filename="logging.log",
#     filemode="a",
# )
 
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)
# console_handler.setFormatter(
#     logging.Formatter(
#         "%(asctime)s - %(levelname)s - %(funcName)20s()->%(lineno)s]- %(message)s"
#     )
# )
# logging.getLogger().addHandler(console_handler)
# logger = logging.getLogger(__name__)

