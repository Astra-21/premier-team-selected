FROM node:23-alpine
WORKDIR /app

COPY ./package.json ./package-lock.json ./
RUN npm install

# その後にアプリのコード全部をコピー
COPY . .

CMD ["npm", "run", "dev", "--", "--host"]

#ビルドに時間がかからないようにする


