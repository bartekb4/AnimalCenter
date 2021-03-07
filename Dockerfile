FROM python:3.9
#The python image uses /usr/src/app as the default run directory:
WORKDIR /usr/src/app
#Copy from the local current dir to the image workdir:
COPY . .
EXPOSE 5000
#Install any dependencies listed in our ./requirements.txt:
RUN pip install --no-cache-dir -r requirements.txt
#Run api.py on container startup:
CMD [ "python", "app.py" ]