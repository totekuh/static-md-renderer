# Use the official Jekyll image as the base
FROM ubuntu:latest

RUN apt update && apt install -y \
    make \
    git \
    gcc \
    g++ \
    ruby \
    ruby-bundler \
    ruby-dev

COPY ./app /usr/src/app

# Set the working directory inside the container
WORKDIR /usr/src/app

# Install dependencies
RUN bundle install

# Set the entrypoint to run Jekyll
ENTRYPOINT ["jekyll", "serve", "--livereload", "--host", "0.0.0.0"]
