FROM node:18-slim
COPY package*.json ./
RUN npm install
COPY files/ /files/
COPY webui.js /
CMD ["node", "webui.js"]
EXPOSE 80
