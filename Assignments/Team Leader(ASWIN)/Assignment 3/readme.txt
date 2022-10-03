Name : ASWIN
Reg No:713919106005
College Name:Sri Ranganathar Institute Of Engineering and technology
Descprition:
    Assignment 3 (To include cloud object storage,watson assistant)

Assignment Tasks:


Task 1:created a bucket in cloud object storage 

Task 2:Uploaded images from flask server and can be viewed
        "/upload"-This Route can upload the files to cloud object storage and the user should enter the bucket name,filename,filename
        "/user" -This Route can display the uploaded images

Task 3:Uploaded a css file from local storage to cloud object storage and this file is applied to an html page 
        "/cssupload"-Routes used to upload a css file to cloud
        "/csspage"  -Route used to view the html page where the css file is returned from the cloud and the css is applied to the page

Task 4:created an watson assistant for to find the branches of the hospital 
        ChatBot URl :https://web-chat.global.assistant.watson.appdomain.cloud/preview.html?backgroundImageURL=https%3A%2F%2Fau-syd.assistant.watson.cloud.ibm.com%2Fpublic%2Fimages%2Fupx-b7c34bce-b411-4be2-bf13-126163f14530%3A%3A899a49e9-f557-4320-911c-72b686c7da43&integrationID=f23a88eb-fc15-425f-8f71-0d30b3faeed0&region=au-syd&serviceInstanceID=b7c34bce-b411-4be2-bf13-126163f14530

Task 5:created a watson assistant service which includes 10 steps and 3 conditions
        "/bot" - Route where the assistant is included in the httml page

//TO RUN SERVER : flask --debug run 
//Note: The connection string of (Cloud Object Storage) is removed to avoid the usage of unauthorised people.
