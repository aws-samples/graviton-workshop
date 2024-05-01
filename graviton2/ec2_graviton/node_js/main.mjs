
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { PutCommand, GetCommand, DynamoDBDocumentClient } from "@aws-sdk/lib-dynamodb";
import { CloudFormationClient, DescribeStacksCommand } from '@aws-sdk/client-cloudformation';


import randomstring from 'randomstring';
import express from 'express';
import bodyParser from 'body-parser';
import axios from 'axios';


try {

    const awsRegion = await getAwsRegion();

    //AWS
    const client = new DynamoDBClient({
        region: awsRegion // Replace with your desired AWS region
    });
    const docClient = DynamoDBDocumentClient.from(client);
    const cloudformation = new CloudFormationClient({ region: awsRegion });

    //App
    const app = express();
    app.use(bodyParser.json());
    const PORT = 8080;

    const gravitonEc2Stack = 'GravitonID-ec2';
    const dynamoDBTableKey = 'EC2ModuleDynamoDBTable'
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

            const data = await cloudformation.send(new DescribeStacksCommand({ StackName: stackName }));
            const stack = data.Stacks[0];

            const outputs = stack.Outputs;
            outputs.forEach(output => {
                cloudformationOutputs.outputs[output.OutputKey] = output.OutputValue;
            });

        } catch (err) {
            console.error('Error fetching stack details:', err);
        }
    }


    async function getAwsRegion() {
        try {

            // Fetch the token
            const tokenResponse = await axios.put(
                'http://169.254.169.254/latest/api/token',
                {},
                {
                    headers: {
                        'X-aws-ec2-metadata-token-ttl-seconds': '21600'
                    }
                }
            );
            const token = tokenResponse.data;

            // Use the token to fetch the region
            const response = await axios.get(
                'http://169.254.169.254/latest/dynamic/instance-identity/document',
                {
                    headers: {
                        'X-aws-ec2-metadata-token': token
                    }
                }
            );
            
            return response.data.region;

        } catch (error) {
            console.error(`Error fetching AWS region: ${error}`);
            return null;
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

            if (!response || !response.Item || !response.Item.originalUrl) {
                return res.status(404).json({ error: 'Short URL not found.' });
            }

            const originalURL = response.Item.originalUrl

            return res.status(200).json(originalURL);

        } catch (error) {
            console.error('Error in main:', error);
            throw error; 
        }

    });


    app.listen(PORT, '0.0.0.0', () => {
        console.log(`Server running on http://0.0.0.0:${PORT}`);
    });


} catch (error) {
    console.error('Error in main:', error);
    throw error; 
}
