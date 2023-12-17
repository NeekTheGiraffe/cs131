# Build frontend
FROM node:18-alpine as build

WORKDIR /frontend
COPY frontend .

RUN npm ci
RUN npm run build

# Deploy Flask server
FROM python:3.11-alpine as deployment

WORKDIR /app
COPY *.py requirements.txt ./
COPY ply ply
COPY --from=build /frontend/dist frontend

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD [ "gunicorn", "-b", "0.0.0.0:8000", "-t", "5", "server:app" ]
