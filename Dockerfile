FROM python:3.8

# Create app directory
WORKDIR /

# Install app dependencies
COPY requirements.txt ./

# Bundle app source
COPY app /app
COPY config /config
COPY utils /utils
COPY package /package

RUN pip3 install --target ./package -r requirements.txt
ENV PYTHONPATH="$PYTHONPATH:/package:/utils"

CMD [ "python3", "/app/bot.py" ]