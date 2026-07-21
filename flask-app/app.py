from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello from nandhagopal to Docker!"

@app.route("/update")
def update():
    return (
        "Steps to run this: "
        "1) Install Docker on your laptop. "
        "2) Write a Dockerfile. "
        "3) Build the Docker image from that Dockerfile. "
        "4) Run the image — it will execute as a container."
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)