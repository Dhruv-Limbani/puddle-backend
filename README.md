clone the repo 
git clone https://github.com/Dhruv-Limbani/puddle-backend.git

uv venv

uv sync

run backend/extras/database-creation-script.sql in pgadmin

uvicorn app.main:app --reload

create .env file

DATABASE_URL=postgresql+asyncpg://<user>:<password>@localhost:5432/puddle
GEMINI_API_KEY=
SECRET_KEY=39b90aacf9ce216af7b0d989fe9b67349f756bc8bafffffd1179547e04a6448a
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

uv add "passlib>=1.7.4" "bcrypt==4.0.1"

