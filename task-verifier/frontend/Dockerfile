FROM node:20-slim

ENV NODE_ENV=development

WORKDIR /app

# Igual que el backend: primero dependencias, después código
COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

# --host 0.0.0.0 es CRÍTICO en Docker: sin esto Vite no es accesible desde fuera del contenedor
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]