# cogeo-watchbot-light

Lightweight version of [cogeo-watchbot](https://github.com/developmentseed/cogeo-watchbot) to convert file to COGs at scale using AWS Lambda.

# What is this

This repo host the code for a serverless architecture enabling creation of Cloud Optimized GeoTIFF at scale.

## Architecture

![](https://user-images.githubusercontent.com/10407788/66224855-f3c04580-e6a4-11e9-8903-8319c9a89875.png)


# Deploy

### Requirements
- serverless
- docker
- aws account


1. Install and configure serverless
```bash
# Install and Configure serverless (https://serverless.com/framework/docs/providers/aws/guide/credentials/)
$ npm install serverless -g 
```

2. Create Lambda package

```bash
$ make build
```

5. Deploy the Serverless stack

```bash
$ sls deploy --stage production --bucket my-bucket --region us-east-1
```


# How To

### Example

1. Get a list of files you want to convert
```$
$ aws s3 ls s3://spacenet-dataset/spacenet/SN5_roads/test_public/AOI_7_Moscow/PS-RGB/ --recursive | awk '{print "https://spacenet-dataset.s3.amazonaws.com/"$NF}' > list_moscow.txt
```
Note: we use `https://spacenet-dataset.s3.amazonaws.com` prefix because we don't want to add IAM role for this bucket

2. Use scripts/create_job.py

```bash
$ pip install rio-cogeo rio-tiler
$ cd scripts/
$ cat ../list_moscow.txt | python -m create_jobs - \
   -p webp \
   --co blockxsize=256 \
   --co blockysize=256 \
   --op overview_level=6 \
   --op overview_resampling=bilinear \
   --prefix my-prefix \
   --topic arn:aws:sns:us-east-1:{AWS_ACCOUNT_ID}:cogeo-watchbot-light-production-WatchbotTopic
```

Note: Output files will be saved in the `bucket` defined in the stack. By default (in the CLI) the prefix will be set to `cogs`.

e.g. 

```
bucket = my-bucket

input file: s3://spacenet-dataset/spacenet/SN5_roads/test_public/AOI_7_Moscow/PS-RGB/1.tif

output file: s3://my-bucket/cogs/1.tif
```