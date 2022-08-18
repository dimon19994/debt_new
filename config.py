from environs import Env

env = Env()

env.read_env()

URL = env.str("DATABASE_URL")
