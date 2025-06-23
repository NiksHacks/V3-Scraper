# Use the official Apify base image
FROM apify/actor-python:3.11

# Copy the requirements file to the container
COPY requirements.txt ./

# Install Python dependencies
RUN pip install -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps

# Copy the rest of the actor's source code to the container
COPY . ./

# Set the command to run when the container starts
CMD ["python3", "-m", "src"]