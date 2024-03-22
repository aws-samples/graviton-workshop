
try {

    const { DynamoDBClient } = require("@aws-sdk/client-dynamodb");
    const { GetCommand, PutCommand, DynamoDBDocumentClient } = require("@aws-sdk/lib-dynamodb");
    const randomstring = require('randomstring');
    const express = require('express');
    const bodyParser = require('body-parser');

    const AWS = require('aws-sdk');
    AWS.config.update({ region: 'us-west-2' });


    //TODO: Delete Unnesessary packages

    const cloudformation = new AWS.CloudFormation();
    const client = new DynamoDBClient({ region: "us-west-2" });

    const docClient = DynamoDBDocumentClient.from(client);
    const gravitonEc2Stack = 'GravitonID-ec2';
    const dynamoDBTableKey= 'EC2ModuleDynamoDBTable'

    //App
    const app = express();
    app.use(bodyParser.json());
    const PORT = 8080;

    const cloudformationOutputs = {
        outputs: {}
    };


    fetchStackParameters(gravitonEc2Stack);

    // Middleware for input validation
    const validateInput = (req, res, next) => {
        const originalUrl = req.body.OriginalURL;
        if (!originalUrl || typeof originalUrl !== 'string' || originalUrl.trim() === '') {
            return res.status(400).json({ error: 'Invalid input: OriginalURL is required and should be a non-empty string.' });
        }
        next();
    };


    // Middleware for input validation
    const validateGetFullURLInput = (req, res, next) => {
        const shortUrl = req.params.shortUrl;
        if (!shortUrl || typeof shortUrl !== 'string' || shortUrl.trim() === '') {
            return res.status(400).json({ error: 'Invalid input: shortUrl is required and should be a non-empty string.' });
        }
        next();
    };

    // Function to fetch parameters and store them globally
    async function fetchStackParameters(stackName) {
        try {
            const data = await cloudformation.describeStacks({ StackName: stackName }).promise();
            const stack = data.Stacks[0];

                // Fetch and store outputs
            const outputs = stack.Outputs;
            outputs.forEach(output => {
                cloudformationOutputs.outputs[output.OutputKey] = output.OutputValue;
            });

            console.log('Global Parameters:', cloudformationOutputs);
        } catch (err) {
            console.error('Error fetching stack details:', err);
        }
    }


    // POST endpoint
    app.post('/shortenURL', validateInput, async (req, res) => {

        try {
            const originalUrl = req.body.OriginalURL;

            const shortUrl = randomstring.generate({
                length: 10,
                charset: 'alphabetic'
            });
          
            const dynamoDBTableName = cloudformationOutputs.outputs[dynamoDBTableKey];

            const command = new PutCommand({
                TableName: dynamoDBTableName,
                Item: {
                    short_url: shortUrl,
                    originalUrl: originalUrl,
                },
            });

            const response = await docClient.send(command);

            // Check if the HTTP status code indicates success
            if (response.$metadata.httpStatusCode !== 200) {
                console.log('Error in DynamoDB request:', response);
                return res.status(response.$metadata.httpStatusCode).json(response);
            }


            const output = {
                shortURL: shortUrl,
                originalURL: originalUrl,
            };

            return res.status(200).json(output);

        } catch (error) {
            console.error('Error in main:', error);
            return res.status(500).json({ error: 'Internal Server Error' });

        }



    });

    // GET endpoint
    app.get('/getFullURL/:shortUrl', validateGetFullURLInput, async (req, res) => {


        try {

            const shortUrl = req.params.shortUrl;

            const dynamoDBTableName = cloudformationOutputs.outputs[dynamoDBTableKey];

            const command = new GetCommand({
                TableName: dynamoDBTableName,
                Key: {
                    short_url: shortUrl,
                },
            });

            const response = await docClient.send(command);

            // Check if the response has the expected structure
            if (!response || !response.Item || !response.Item.originalUrl) {
                return res.status(404).json({ error: 'Short URL not found.' });
            }

            const originalURL = response.Item.originalUrl

            return res.status(200).json(originalURL);

        } catch (error) {
            console.error('Error in main:', error);
            throw error; // Propagate the error to the caller
        }

    });



   /*app.listen(PORT, () => {
        console.log(`Server running on http://localhost:${PORT}`);
    });*/

    app.listen(PORT, '0.0.0.0', () => {
        console.log(`Server running on http://0.0.0.0:${PORT}`);
    });
    


} catch (error) {
    console.error('Error in main:', error);
    throw error; // Propagate the error to the caller
}
