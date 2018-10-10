import StringIO
import zipfile
import mimetypes
import boto3
from botocore.client import Config

def lambda_handler(event, context):
    sns_client = boto3.client('sns')
    fileType = ['woff','woff2','eot','json','ttf','otf']
    
    try:
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
        
        portfolio_bucket = s3.Bucket('example.com')
        build_bucket = s3.Bucket('buildbucket')
        
        example_zip = StringIO.StringIO()
        build_bucket.download_fileobj('example.zip',example_zip)
        
        with zipfile.ZipFile(example_zip) as myzip:
            for nm in myzip.namelist():
                type = nm.split('.')[-1]
                if (type not in fileType) and ('Makefile' not in type) :
                    obj = myzip.open(nm)
                    portfolio_bucket.upload_fileobj(obj, nm,
                        ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                    portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
                else:
                    obj = myzip.open(nm)
                    portfolio_bucket.upload_fileobj(obj, nm)
                    portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
                
        print "Job Done!"
        sns_client.publish(
            PhoneNumber='15555555',
            Message='Website successfully updated',
        )
    except:
        sns_client.publish(
            PhoneNumber='15555555',
            Message='Website deployment error',
        )
        raise
    
    return 'Your files should be ready!'