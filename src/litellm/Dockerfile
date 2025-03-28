# Use the provided base image
FROM ghcr.io/berriai/litellm:main-latest

# Set the working directory to /app
WORKDIR /app

# # Copy the configuration file into the container at /app
COPY litellm_config.yaml .

# Make sure your docker/entrypoint.sh is executable
RUN chmod +x docker/entrypoint.sh
COPY requirements.txt .
RUN pip install -r requirements.txt

# Expose the necessary port
EXPOSE 4000/tcp

# Override the CMD instruction with your desired command and arguments
CMD ["--port", "4000",  "--detailed_debug", "--run_gunicorn", "--config", "litellm_config.yaml"]
