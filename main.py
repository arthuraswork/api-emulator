from fastapi import FastAPI 
from endpoints.sns.social_network_simulator import sns

import uvicorn 
import dotenv
import os

dotenv.load_dotenv()

app = FastAPI(title='APIEmulator')

app.include_router(sns)

if __name__ == '__main__':
    uvicorn.run(app, host=os.getenv('HOST'), port=int(os.getenv('PORT')))