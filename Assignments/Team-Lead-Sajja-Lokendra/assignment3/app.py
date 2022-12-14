import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import ibm_boto3
from ibm_botocore.client import Config, ClientError
from dotenv import load_dotenv
load_dotenv()

COS_ENDPOINT = os.environ.get("COS_ENDPOINT")
COS_API_KEY_ID = os.environ.get("COS_API_KEY_ID")
COS_INSTANCE_CRN = os.environ.get("COS_INSTANCE_CRN")


cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

app = Flask(__name__, template_folder="templates")


def multi_part_upload(bucket_name, item_name, file_path):
    try:
        print("Starting file transfer for {0} to bucket: {1}\n".format(item_name, bucket_name))
        part_size = 1024 * 1024 * 5

        file_threshold = 1024 * 1024 * 15

        transfer_config = ibm_boto3.s3.transfer.TransferConfig(
            multipart_threshold=file_threshold,
            multipart_chunksize=part_size
        )
        with open(file_path, "rb") as file_data:
            cos.Object(bucket_name, item_name).upload_fileobj(
                Fileobj=file_data,
                Config=transfer_config
            )

        print("Transfer for {0} Complete!\n".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to complete multi-part upload: {0}".format(e))
    finally:
        os.remove(os.path.dirname(app.instance_path)+"/"+secure_filename(file_path))
        

@app.route('/uploader', methods = ['GET', 'POST'])
def upload():
   if request.method == 'POST':
       bucket= "imagestoring123"
       name_file=request.form['filename']
       f = request.files['file']
       f.save(secure_filename(f.filename))
       multi_part_upload(bucket,name_file,f.filename)
       return 'file uploaded successfully'
    
   if request.method == 'GET':
       return render_template('upload.html')

@app.route("/", methods = ['GET'])
def Index():
    integrationID=os.environ.get("integrationID")
    region=os.environ.get("region")
    serviceInstanceID=os.environ.get("serviceInstanceID")

    try:
        file = cos.Object("imagestoring123", "style.css").get()
        fs = file['Body'].read().decode("utf-8")
        with open(os.path.dirname(app.instance_path)+"/static/style.css", "w") as binary_file:
            binary_file.writelines(fs)
    except Exception as e:
        open(os.path.dirname(app.instance_path)+"/static/style.css", "w").close()
    filesKey = []
    msg = ''
    try:
        files = cos.Bucket("imagestoring123").objects.all()
        for file in files:
            filesKey.append(file.key)
    except ClientError as be:
        msg = 'Database Server Error'
    except Exception as e:
        msg = 'Internal Server Error'
    return render_template('index.html', files = filesKey, msg = msg,
    integrationID =integrationID,
    region = region,
    serviceInstanceID = serviceInstanceID
    )



app.run(port=5000, debug=True)