FROM public.ecr.aws/amazonlinux/amazonlinux:2
WORKDIR /usr/src/app
COPY package*.json nodejs_code/app.js ./
RUN yum install https://rpm.nodesource.com/pub_16.x/nodistro/repo/nodesource-release-nodistro-1.noarch.rpm -y
RUN yum install nodejs -y --setopt=nodesource-nodejs.module_hotfixes=1
RUN npm install
EXPOSE 3000
CMD ["node", "app.js"]
