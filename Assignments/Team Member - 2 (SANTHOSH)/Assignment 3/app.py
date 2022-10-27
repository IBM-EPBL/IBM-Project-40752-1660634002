from flask import Flask, render_template, request
import ibm_boto3
from ibm_botocore.client import Config, ClientError

app = Flask(__name__)
COS_ENDPOINT = ""
COS_API_KEY_ID = ""
COS_INSTANCE_CRN = ""

cos = ibm_boto3.resource("s3",
                         ibm_api_key_id=COS_API_KEY_ID,
                         ibm_service_instance_id=COS_INSTANCE_CRN,
                         config=Config(signature_version="oauth"),
                         endpoint_url=COS_ENDPOINT)


# CREATE A BUCKET
def create_bucket(bucket_name):
    print("Creating new bucket: {0}".format(bucket_name))
    try:
        cos.Bucket(bucket_name).create(
            CreateBucketConfiguration={
                "LocationConstraint": COS_BUCKET_LOCATION
            }
        )
        print("Bucket: {0} created!".format(bucket_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to create bucket: {0}".format(e))

# CREATING A NEW TEXT FILE


def create_text_file(bucket_name, item_name, file_text):
    print("Creating new item: {0}".format(item_name))
    try:
        cos.Object(bucket_name, item_name).put(
            Body=file_text
        )
        print("Item: {0} created!".format(item_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to create text file: {0}".format(e))

# LIST BUCKETS


def get_buckets():
    print("Retrieving list of buckets")
    try:
        buckets = cos.buckets.all()
        for bucket in buckets:
            print("Bucket Name: {0}".format(bucket.name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve list buckets: {0}".format(e))

# List items in BUCKET NAME


def get_bucket_contents(bucket_name):
    print("Retrieving bucket contents from: {0}".format(bucket_name))
    try:
        files = cos.Bucket(bucket_name).objects.all()
        files_names = []
        for file in files:
            files_names.append(file.key)
            print("Item: {0} ({1} bytes).".format(file.key, file.size))
        return files_names
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve bucket contents: {0}".format(e))


# Cotents
def get_item(bucket_name, item_name):
    print("Retrieving item from bucket: {0}, key: {1}".format(
        bucket_name, item_name))
    try:
        file = cos.Object(bucket_name, item_name).get()
        print("File Contents: {0}".format(file["Body"].read()))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve file contents: {0}".format(e))


# DELETE AN ITEM FROM BUCKET
def delete_item(bucket_name, object_name):
    try:
        cos.delete_object(Bucket=bucket_name, Key=object_name)
        print("Item: {0} deleted!\n".format(object_name))
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to delete object: {0}".format(e))

# Multipart Upload


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


@app.route("/")
def homePage():
    # file=get_bucket_contents('userphotos')
    file = get_buckets()
    print(file)

    return render_template("home.html")


@app.route("/upload", methods=["GET", "POST"])
def uploader():
    if request.method == "GET":
        return render_template('upload.html')
    else:
        bucket = request.form["name"]
        fname = request.form["filename"]
        f = request.files['file']
        print(f.filename, fname, bucket)
        multi_part_upload(bucket, fname, f.filename)
        return "Successfully uploaded"


@app.route("/user")
def newroute():

    files = get_bucket_contents('userphotos')
    # for x in user:
    print(files)

    return render_template('home.html', file=files)


@app.route("/cssupload", methods=["POST", "GET"])
def newfn():
    if request.method == "GET":
        return render_template('addcss.html')
    else:
        bucket = request.form["bucket"]
        fname = request.form["filename"]
        f = request.files['file']
        print(f.filename, fname, bucket)
        multi_part_upload(bucket, fname, f.filename)
        return "Successfully uploaded"


@app.route("/csspage")
def csspagee():
    files = get_bucket_contents('userphotos')
    print("completed")
    print(files[6])

    return render_template("csspage.html", files=files)


@app.route("/bot")
def assistant():
    return render_template('assist.html')
