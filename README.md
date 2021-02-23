This application will create below resources in your AWS account

- A lambda function that allows you to create lambda layers for python function.

- An IAM role that Allow the lambda function to publish lambda layers.

**You will be liable for the cost used by the application resources.**

## Lambda input event:

`{ "dependencies": { "requests": "latest", "docopt": "== 0.6.1", "keyring": ">= 4.1.1" }, "layer": { "name": "layer-creation-python-layer", "description": "contains dependencies of layer creation function", "compatible-runtimes": [ "python3.6","python3.7","python3.8" ], "license-info": "MIT" } }`
