# 1 - About

colabme is a simple cli written in python for uploading files to a Google drive project.


# 2 - Installation

To install, simply clone the project and run pip install.
```
git clone https://github.com/optimazter/colabme.git
cd colabme
pip install .
```

# 3 - Usage

### 3.1 - Setup a Google service account

Visit https://developers.Google.com/identity/protocols/oauth2/service-account#creatinganaccount to see how you can setup your service account.

### 3.2 - Create a JSON key

Create a new key for your account by clicking on the *Add Key* button in the *Keys* tab. Choose *JSON* as the key format. 

![image](https://github.com/user-attachments/assets/50c27715-603c-444f-b5f4-94c7e2bc3b83)

Save your key somewhere you remember, e.g., inside the project you want to commit to Google drive. You will need it later!

### 3.3 - Enable Google Drive API

Go to https://console.cloud.Google.com/apis/library and enable Google Drive API for your project.

### 3.4 - Create a new project in Google drive (optional)

Create a new folder in your Google drive. Right-click the folder, choose Share and add the email address of the service account you created in step 1. The email address can be found under the *detail* tab on your Service Account page.

### 3.4 - Setup colabme project

Open a terminal in the root of your desired project and type the following.

```
colabme setup -s path/to/your/key.json
```
If you have created a certain folder you want to upload to as explained in step *3.4*, you can set the parent folder as follows

```
colabme setup -p folder ID
```
Where the folder ID can be found in the URL of your folder. This is everything that comes after “folder/” in the URL. For example, if the URL was "https://drive.google.com/drive/folders/1dyUEebJaFnWa3Z4n0BFMVAXQ7mfUH11g", then the folder ID would be "1dyUEebJaFnWa3Z4n0BFMVAXQ7mfUH11g".

### 3.5 - Commit files

To commit files and/or folders to your Google drive you can now simply:

```
colabme commit file1 file2 folder1 folder2 ....
```
After your first commit you can also choose to update all your tracked files by:

```
colabme commit -u
```

### 3.6 - Debug errors

It is recomended to always enable verbose mode by adding *-v* or *--verbose* flag to your command to check that everything goes as expected.
E.g., if you have set the wrong parent ID the commit will still be succesful but will not happen in the folder you intended.

# 4 - References

 * https://www.labnol.org/google-api-service-account-220404/
 * https://ragug.medium.com/how-to-upload-files-using-the-google-drive-api-in-python-ebefdfd63eab
 * https://learn.azuqua.com/connector-reference/googledrive/
