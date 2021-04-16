FROM public.ecr.aws/amazonlinux/amazonlinux:2
WORKDIR /usr/src/app
COPY package*.json nodejs_code/app.js ./
RUN curl -sL https://rpm.nodesource.com/setup_14.x | bash -
RUN yum -y install nodejs
RUN npm install
EXPOSE 3000
CMD ["node", "app.js"]
