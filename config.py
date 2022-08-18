from environs import Env

env = Env()

env.read_env()

URL = env.str("DEBT_DB_URL")
