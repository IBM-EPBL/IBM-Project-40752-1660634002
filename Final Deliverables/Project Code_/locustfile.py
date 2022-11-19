from locust import HttpUser, task

class skilljob(HttpUser):
    @task
    def home(self):
        self.client.get("/")
        

    @task
    def login(self):
        self.client.get("/user/signin")
        
    @task
    def feed(self):
        self.client.get("/user/newsfeed")