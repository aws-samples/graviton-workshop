// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved. SPDX-License-Identifier: MIT-0

const http = require('http');

const port = 3000;

const server = http.createServer((req, res) => {
	  res.statusCode = 200;
	  res.setHeader('Content-Type', 'text/plain');
	  res.end(`Hi! This processor architecture is ${process.arch}`);
});

server.listen(port, () => {
	  console.log(`Server running on ${process.arch} architecture.`);
});
