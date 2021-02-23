import json
import os
import zipfile
import boto3
import logging

logger = logging.getLogger()
lambda_client = boto3.client('lambda')
path = '/tmp/layer'
requirement_file_path = path + '/requirement.txt'
python_dependency_folder = '/tmp/layer/python'
layer_package_file_path = path + '/function.zip'


def make_folder(path):
    os.makedirs(name=path, exist_ok=True)


def delete_folder(path):
    for f in os.listdir(path):
        if (os.path.isdir('/'.join([path, f]))):
            delete_folder('/'.join([path, f]))
            os.rmdir(f)
        else:
            os.remove(f)


def write_to_file(path, lines):
    mode = 'a'
    if (not os.path.exists(path)):
        mode = 'w'
    with open(path, mode) as filehandle:
        filehandle.writelines(lines)
        filehandle.close()


# def read_from_file(path):
#     with open(path, 'r') as filehandle:
#         while True:
#             # read a single line
#             line = filehandle.readline()
#             if not line:
#                 break
#             print(line)
#         filehandle.close()


def generate_requirement_txt_file(event):
    dependencies = []
    for d in event['dependencies']:
        if (event['dependencies'][d].lower() == 'latest'):
            dependencies.append("%s\n" % d)
        else:
            dependencies.append("%s %s\n" %
                                (d, event['dependencies'][d]))
    write_to_file(requirement_file_path, dependencies)
    # os.system("cat %s" % requirement_file_path)


# def list_directory(path):
#     for f in os.listdir(path):
#         if (os.path.isdir('/'.join([path, f]))):
#             list_directory('/'.join([path, f]))
#         print(f)


def zipdir(path, filename):
    ziph = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), os.path.relpath(
                os.path.join(root, file), os.path.join(path, '..')))
    ziph.close()


def install_dependencies_then_package_the_layer(requirement_file_path, dependency_target_folder, layer_package_file_path):
    cmd_exit_code = os.system(
        "pip install --target %s -r %s" % (
            dependency_target_folder, requirement_file_path))
    if (cmd_exit_code == 0):
        zipdir(dependency_target_folder, layer_package_file_path)
        # os.system("ls -la %s" % dependency_target_folder)
    else:
        raise Exception("`pip install` ran with exit code %d" % cmd_exit_code)


def create_lambda_layer(layer_package_file_path, layer):
    with open(layer_package_file_path, 'rb') as filehandle:
        response = lambda_client.publish_layer_version(
            CompatibleRuntimes=layer['compatible-runtimes'],
            Content={
                'ZipFile': filehandle.read()
            },
            Description=layer['description'],
            LayerName=layer['name'],
            LicenseInfo=layer['license-info'],
        )
        filehandle.close()
        # print(response)


def lambda_handler(event, context):
    try:
        if (os.path.exists(path)):
            delete_folder(path)
        make_folder(python_dependency_folder)
        if (event['dependencies'] and event['layer']):
            generate_requirement_txt_file(event)
            install_dependencies_then_package_the_layer(
                requirement_file_path, python_dependency_folder, layer_package_file_path)
            create_lambda_layer(layer_package_file_path, event['layer'])
        else:
            raise Exception(
                'BadRequestException - check the invocation payload')

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "layer was created successfully"
            }),
        }
    except Exception as e:
        logger.exception("Something bad happened")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Something bad happened"
            }),
        }
