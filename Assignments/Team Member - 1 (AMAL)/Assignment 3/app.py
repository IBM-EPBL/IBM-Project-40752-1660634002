from flask import Flask,render_template,request,redirect
import ibm_boto3
from ibm_botocore.client import Config, ClientError 

COS_ENDPOINT="https://s3.jp-tok.cloud-object-storage.appdomain.cloud"
COS_API_KEY=""
COS_INSTANCE_CRN=""

cos=ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT

)
def get_bucket_contents(bucket_name):
    print("Retrieving bucket contents from: {0}".format(bucket_name))
    try:
        files = cos.Bucket(bucket_name).objects.all()
        files_names=[]
        for file in files:

            print("Item: {0} ({1} bytes).".format(file.key, file.size))
            files_names.append(file.key)
            
            
        return files_names
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve bucket contents: {0}".format(e))




def multi_part_upload(bucket_name, item_name, file_path):
    try:
        print("Starting file transfer for {0} to bucket: {1}\n".format(
            item_name, bucket_name))
        # set 5 MB chunks
        part_size = 1024 * 1024 * 5

        # set threadhold to 15 MB
        file_threshold = 1024 * 1024 * 15

        # set the transfer threshold and chunk size
        transfer_config = ibm_boto3.s3.transfer.TransferConfig(
            multipart_threshold=file_threshold,
            multipart_chunksize=part_size
        )

        # the upload_fileobj method will automatically execute a multi-part upload
        # in 5 MB chunks for all files over 15 MB
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


app=Flask(__name__)

@app.route('/')
def home():
    print("home")
    files=get_bucket_contents("flask-cos")

    
    
    return render_template("home.html",files=files)

@app.route('/upload')
def upload():
    return render_template("upload.html")



@app.route("/upload", methods=['POST','GET'])
def upload_file():
    if request.method == 'POST':
       bucket=request.form['bucket']
       file_name=request.form['name']
       f = request.files['file']
       multi_part_upload(bucket,file_name,f.filename)
       return 'file uploaded Successfully'

@app.route('/css')
def css():
    print("css")
    files=get_bucket_contents("flask-cos")
    
    print(files)
    print(files[0])
    return render_template("css.html", files=files) 

@app.route("/bot")
def bot():
    print("bot")
    return render_template("bot.html")

# if __name__=='__main__': 
#     app.run(port=3000,debug=True)