## AWS IAM USER
![Python](https://img.shields.io/badge/-Python-333333?style=flat&logo=python)
![AWS Cloud](https://img.shields.io/badge/-AWS%20Cloud-333333?style=flat&logo=amazon)

Create `programmatic user` using `lambda` function

1. Create `User`
2. Create `Policy`
3. Attach `policy to the user`
4. Create `access key` and `secret key`

#### Policy defined 
* Gives `read and write` permission to the `specific folder` in `S3` bucket

#### USAGE

Invoke the lambda with following json input

```json line
{
  'AccountId': '65476567567',
  'UserName': 'NEWIAMUSER',
  'PolicyName': 'NEWPOLICY',
  'BucketName': 'bucket_name',
  'FolderName': 'FOLDERNAME'
}
```
